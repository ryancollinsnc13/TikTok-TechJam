from flask import Flask, request, jsonify
from flask_cors import CORS
import pyaudio
import numpy as np
import pvporcupine
import pvcobra
import wave
import os
import requests
import platform
import time
from dotenv import load_dotenv
from collections import deque


load_dotenv('.env.local')

access_key = os.getenv('PICOVOICE_ACCESS_KEY')

app = Flask(__name__)
CORS(app)

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

def continuous_recording(callback):
    global pa
    global audio_stream

    pa = pyaudio.PyAudio()
    
    audio_stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=porcupine.sample_rate,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )
    
    pre_buffer = deque(maxlen=5) 
    recording = False
    recorded_audio = []
    silence_start_time = None
    silence_duration = 1.0 

    try:
        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = np.frombuffer(pcm, dtype=np.int16)
            
        
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
                        callback(np.concatenate(recorded_audio))
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

def process_audio(buffer):
    print("Processing audio buffer")

    temp_audio_path = 'audio/temp_audio.wav'
    with wave.open(temp_audio_path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(buffer.tobytes())


    send_to_nextjs(temp_audio_path)
def send_to_nextjs(audio_path):
    with open(audio_path, 'rb') as f:
        response = requests.post('http://localhost:3000/api/transcribe', files={'audio': f})
        if response.status_code == 200:
            print("Audio successfully sent to Next.js API")
        else:
            print("Failed to send audio to Next.js API")
    os.remove(audio_path)

@app.route('/start-recording', methods=['POST'])
def start_recording():
    continuous_recording(process_audio)
    return jsonify({"message": "Recording started"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)