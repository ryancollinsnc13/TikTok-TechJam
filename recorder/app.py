from quart import Quart, request, jsonify
from quart_cors import cors
import pyaudio
import numpy as np
import pvporcupine
import pvcobra
import wave
import os
import platform
import time
from dotenv import load_dotenv
from collections import deque
import openai
import tempfile
import socketio

load_dotenv('.env')

access_key = os.getenv('PICOVOICE_ACCESS_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

openai.api_key = openai_api_key

app = Quart(__name__)
app = cors(app)
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")
sio_app = socketio.ASGIApp(sio, app)

commands = [
    '1: Go to For You Page',
    '2: Upload a video',
    '3: Go to my profile page',
    '4: Log out',
    '5: Like this video',
    '6: Leave a comment', 
    '7: Search for text', 
    '8: Go to video owner profile',
    '9: Scroll to next video',
    '10: Edit profile',
    '11: Change name',
    '12: Change bio',
]

def get_keyword_path():
    system_platform = platform.system()
    if system_platform == 'Linux':
        return 'models/linux/wake_word.ppn'
    elif system_platform == 'Windows':
        return 'models/windows/wake_word.ppn'
    elif system_platform == 'Darwin':
        return 'models/macos/wake_word.ppn'
    else:
        raise ValueError("Unsupported platform")
    
porcupine = pvporcupine.create(
    access_key=access_key,
    keyword_paths=[get_keyword_path()],
)

cobra = pvcobra.create(access_key=access_key)

async def continuous_recording(callback):
    global pa
    global audio_stream

    pa = pyaudio.PyAudio()
    
    audio_stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=porcupine.sample_rate,
        input=True,
        frames_per_buffer=porcupine.frame_length * 4
    )
    
    pre_buffer = deque(maxlen=5) 
    recording = False
    recorded_audio = []
    silence_start_time = None
    silence_duration = 1.7

    try:
        while True:
            try:
                pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
                pcm = np.frombuffer(pcm, dtype=np.int16)
            except IOError as e:
                print(f"Audio input overflow: {e}")
                continue
            
            pre_buffer.append(pcm)

            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("Wake word detected!")
                recording = True
                recorded_audio = list(pre_buffer) 
                silence_start_time = None

            if recording:
                recorded_audio.append(pcm)
                vad_result = cobra.process(pcm)

                if vad_result < 0.5: 
                    if silence_start_time is None:
                        silence_start_time = time.time()
                    elif time.time() - silence_start_time > silence_duration:
                        recording = False
                        print("User stopped talking!")
                        await callback(np.concatenate(recorded_audio))
                        recorded_audio = []
                        pre_buffer.clear()
                else:
                    silence_start_time = None

    except KeyboardInterrupt:
        print("Recording stopped.")
    finally:
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()
        if porcupine is not None:
            porcupine.delete()
        if cobra is not None:
            cobra.delete()

async def process_audio(buffer):
    print("Processing audio buffer")

    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio_file:
        with wave.open(temp_audio_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(buffer.tobytes())
        
        temp_audio_path = temp_audio_file.name
    
    await transcribe_and_identify_command(temp_audio_path)

async def transcribe_and_identify_command(audio_path):
    with open(audio_path, 'rb') as f:
        # Update to new OpenAI API method for transcription
        transcript_text = openai.audio.translations.create(
            model="whisper-1", 
            file=f,
            response_format="text"
        )
        print(f"Transcription: {transcript_text}")

        prompt = f'The user said: "{transcript_text}". Determine which of the following commands best matches the text: {", ".join(commands)}. Return only the number associated with the command, and if no command matches, return "0".'

        completion_response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI that identifies commands from a predefined list based on user input."},
                {"role": "user", "content": prompt},
            ]
        )

        command = completion_response.choices[0].message.content.strip()
        print(f"Identified command: {command}")

        await sio.emit('command', {'command': command})

    os.remove(audio_path)

@app.route('/start-recording', methods=['POST'])
async def start_recording():
    await continuous_recording(process_audio)
    return jsonify({"message": "Recording started"}), 200

@app.route('/shutdown', methods=['POST'])
async def shutdown():
    # This endpoint will shut down the server when accessed.
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return jsonify({"message": "Server shutting down..."}), 200

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(sio_app, host='0.0.0.0', port=5001)
