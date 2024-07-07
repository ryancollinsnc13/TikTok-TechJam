# 🎉 **Tikki: The Voice Assistant for TikTok** 🎉

Welcome to **Tikki**, an innovative voice assistant designed to enhance your TikTok experience! With Tikki, you can navigate TikTok effortlessly using just your voice. This project leverages cutting-edge generative AI technology to make the app accessible to everyone, including those with mobility constraints.


## 🏆 **2024 TikTok Tech Jam Submission**

This is our prototype submission for the 2024 TikTok Tech Jam in the category of **Inspiring Creativity with Generative AI**. The project, **Tikki for TikTok**, is brought to you by TikTalkers—**Ooha Reddy** and **Ryan Collins**. You can view our submission on [Devpost](https://devpost.com/software/voiceassist).


## 🌟 **Tikki's Story**

As we continue to reimagine the capabilities of our technology, we recognize the importance of accessibility. Voice-powered navigation has become increasingly powerful with advancements in Generative AI, allowing us to track acoustic patterns, detect voice activity, and process complex commands more accurately than ever.

**Tikki** is a generative AI-powered voice assistant that allows users to navigate TikTok with a variety of voice commands. Simply wake Tikki up with a "Hi Tikki," and your wish is its command. Tikki supports a wide range of languages, making it a truly global assistant.

For this prototype, we recreated the TikTok web front-end using **Next.js**. The backend uses a trained wake word detection neural network to match real-time audio input with the acoustic pattern for "Hi Tikki." Upon detection, it records the user's speech, transcribes it, and processes the command with GPT-4. The frontend then executes the command within the TikTok interface.

We faced several challenges, including ensuring a natural and intuitive recording experience and protecting user privacy by recording only when necessary. Despite these challenges, we achieved impressive wake word detection accuracy and developed a system that understands even vaguely expressed commands.

Next steps would include integrating Tikki into the mobile app and developing a distinct character identity for Tikki as an interactable entity, not just a back-end app.


## 📖 **Presentation**

To learn more about Tikki, check out our Google Slides presentation:

<iframe src="https://docs.google.com/presentation/d/e/2PACX-1vRD-klN0_NxW2eMq7EDBQtD8TJo5_tZPXADla6-V1kHv4QFkpw6KdGvfPN_qpuz9yS-7-d2Gcqq2GwV/embed?start=false&loop=false&delayms=5000" frameborder="0" width="1920" height="1109" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>

## ⚙️ **How to Run a Test Build**

Follow these steps to run a test build of Tikki:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ryancollinsnc13/TikTok-TechJam.git
   cd TikTok-TechJam
   ```
2. **Set Up the Backend**:
   - Navigate to the recorder directory:
     ```bash
     cd recorder
     ```
   - Install the required Python packages:
     ```bash
     pip install -r requirements.txt
     ```
   - Run the backend application:
     ```bash
     python app.py
     ```

3. **Set Up the Frontend**:
   - Open a new terminal and navigate to the tiktok-demoshowcase directory:
     ```bash
     cd ../tiktok-demoshowcase
     ```
   - Install the necessary npm packages:
     ```bash
     npm install
     ```
   - Start the development server:
     ```bash
     npm run dev
     ```

4. **Start Recording**:
   - In another terminal, initiate the recording process:
     ```bash
     curl -X POST http://127.0.0.1:5001/start-recording
     ```

## ⏱ **Timeout**

Please note that the application will timeout after a bit, so make sure to test your commands promptly.

---

Enjoy navigating TikTok hands-free with Tikki! 🎉