# 🌟 Aura: Voice AI Assistant

Aura is an advanced, modular AI personal assistant designed to handle intelligence, automation, command routing, voice interactions, and more.

## 📂 Project Structure

Here is a quick overview of the directories and files in this project:

```text
voice_ai_assistant/
│
├── ai/                        # 🧠 AI Brain: Handles LLM logic
│   ├── groq_ai.py            # Interacts with Groq API for rapid AI responses
│   ├── fast_ai.py            # Fast/local fallback model logic
│   ├── ai_router.py          # Dynamically routes queries to appropriate AI models
│   └── prompts.py            # Stores system prompts for different personas/tasks
│
├── automation/               # ⚙️ Automation Powerhouse: Action executors
│   ├── whatsapp.py           # Handles sending and reading WhatsApp messages
│   ├── email.py              # Manages fetching and sending emails
│   ├── youtube.py            # Controls YouTube searches and video playback
│   ├── browser.py            # Automates web browsing and Google searches
│   ├── system.py             # System-level controls (shutdown, volume, brightness)
│   ├── file_manager.py       # Interacts with local files and directories
│   └── reminder.py           # Sets alarms, timers, and scheduled tasks
│
├── commands/                 # 🧠 Command Handling: Intent and execution routing
│   ├── intent_detector.py    # NLP logic to classify what the user wants to do
│   ├── entity_extractor.py   # Pulls relevant data (names, times, messages) from text
│   └── command_router.py     # Triggers the correct automation module based on intent
│
├── voice/                    # 🎤 Voice System: Audio inputs and outputs
│   ├── speech_to_text.py     # Transcribes user's spoken audio into text (STT)
│   ├── text_to_speech.py     # Synthesizes text back into spoken audio (TTS)
│   └── wake_word.py          # Continuously listens for the specific wake word (e.g. "Aura")
│
├── memory/                   # 🧠 Memory System: State and context management
│   ├── memory_manager.py     # Logic for reading and writing contextual data
│   ├── user_data.json        # Persistent user definitions, preferences, and contacts
│   └── chat_history.json     # Rolling log of the current conversation context
│
├── api/                      # 🌐 External APIs: Fetching internet data
│   ├── weather_api.py        # Contacts APIs (like OpenWeather) for forecasts
│   ├── news_api.py           # Pulls latest headlines from news APIs
│   └── search_api.py         # Performs general information lookups via search engines
│
├── security/                 # 🔐 Cyber Security: Protection and scanning
│   ├── password_checker.py   # Analyzes password strength or checks for breaches
│   └── url_scanner.py        # Verifies URLs for malicious or phishing content
│
├── utils/                    # 🛠 Helper Functions: Shared utility logic
│   ├── logger.py             # Configures app-wide logging formats and destinations
│   ├── helpers.py            # General miscellaneous utility functions
│   └── constants.py          # Centralizes all magic strings, limits, and fixed configurations
│
├── gui/                      # 🖥️ User Interface (Optional interface)
│   ├── app_ui.py             # Defines the main application graphical window
│   └── components.py         # Defines reusable UI widgets and styling
│
├── logs/                     # 📄 Log Files: Execution tracking
│   └── app.log               # The main log file where runtime events are stored
│
├── config.py                 # ⚙️ Global configurations (AI usage modes, voice toggles, etc.)
├── main.py                   # 🚀 Main Entry Point: Boots up all systems and wait for commands
├── requirements.txt          # 📦 Python Dependencies: Lists all pip packages needed
├── .env                      # 🔐 Environment Variables: Used to securely store API Keys
├── start.bat                 # ▶️ Quick start: A simple Windows script to run the project
└── README.md                 # 📖 Project documentation (This file)
```

## 🚀 Getting Started

### 1️⃣ Prerequisites
- **Python 3.9+** installed and added to your system PATH.
- Virtual Environment (recommended).
- Required API Keys (e.g., Groq API key, Weather API key) securely added to the `.env` file.

### 2️⃣ Installation

1. Open your terminal or command prompt in the `voice_ai_assistant` directory.
2. Install the necessary Python dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

### 3️⃣ Running the Assistant

Once dependencies are installed and API keys are set, start the assistant by executing the main python script or the batch runner:

```cmd
python main.py
```
*(Or simply double click on `start.bat`)*

---

### 🧠 Modules Work Flow
1. **Wake Word** triggers the assistant.
2. **Speech-to-Text (STT)** converts your voice to text.
3. **Intent Detector** & **Entity Extractor** figure out what operation you need.
4. If it's a conversation or knowledge question, **AI Brain (Groq)** handles it.
5. If it's an action, the **Command Router** tells the **Automation Powerhouse** to run it.
6. **Text-to-Speech (TTS)** responds to you with voice!
