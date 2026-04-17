# 🌟 Aura: AI Personal Voice Assistant

## 📌 Description

Aura is an AI-powered personal voice assistant designed to perform intelligent automation and voice-based interactions. It helps users execute daily tasks such as sending messages, controlling system operations, browsing the internet, and interacting with AI using natural voice commands.

---

## 🚀 Features

### 🎤 Voice Interaction

* Real-time Speech-to-Text (STT) for converting voice into commands
* Text-to-Speech (TTS) for natural voice responses
* Wake word detection to activate the assistant

### 🤖 AI Intelligence

* Handles general queries using AI models
* Smart response generation for conversations
* Supports dynamic query routing for better performance

### ⚙️ Task Automation

* Send WhatsApp messages automatically
* Send and read emails
* Open websites and perform Google searches
* Control YouTube playback (search, play, pause)

### 💻 System Control

* Adjust system volume and brightness
* Shutdown or restart system
* File and folder handling

### 📅 Productivity Tools

* Set reminders and alarms
* Schedule tasks
* Manage basic daily activities

### 🌐 API Integration

* Fetch real-time weather updates
* Get latest news headlines
* Perform online searches

### 🔐 Security Features

* Password strength checking
* URL safety scanning (phishing detection)

---

## ⚙️ Working

1. The assistant continuously listens for a predefined **wake word** (e.g., "Aura").
2. Once activated, it captures the user’s voice input.
3. The voice input is converted into text using **Speech-to-Text (STT)**.
4. The system analyzes the command using **intent detection and entity extraction**.
5. Based on the command:

   * If it is a general query → handled by AI model
   * If it is an action → routed to automation modules
6. The task is executed (e.g., sending message, opening browser, etc.)
7. The response is converted back into voice using **Text-to-Speech (TTS)**.
8. The assistant replies to the user.

---

## 🛠️ Tech Stack

* Python
* Selenium (ChromeDriver)
* Speech Recognition
* Text-to-Speech (TTS)
* APIs (Groq, Weather, News)

---

## ▶️ How to Run

1. Install Python 3.9+
2. Install required dependencies:
   pip install -r requirements.txt
3. Add required API keys in `.env` file
4. Run the project:
   python main.py
   or run `start.bat`

---

## 📌 Note

Make sure ChromeDriver is properly installed and configured before running the project.
