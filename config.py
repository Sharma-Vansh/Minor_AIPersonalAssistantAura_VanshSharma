"""
config.py — Global configuration for Aura
All feature toggles and settings live here.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

# ─── User ────────────────────────────────────────────────
USER_NAME   = os.getenv("USER_NAME", "Boss")
USER_CITY   = os.getenv("USER_CITY", "New Delhi")

# ─── AI Settings ─────────────────────────────────────────
GROQ_API_KEY   = os.getenv("GROQ_API_KEY")
GROQ_MODEL     = "llama-3.3-70b-versatile"   # Fast & powerful (free)
AI_MAX_TOKENS  = 1024
AI_TEMPERATURE = 0.7

# ─── Voice Settings ──────────────────────────────────────
VOICE_ENABLED       = True    # Set False to use text-only mode
WAKE_WORD           = "Aura"
WAKE_WORD_SENSITIVITY = 0.5   # 0.0 (strict) → 1.0 (loose)
TTS_RATE            = 175     # Speech speed (words per minute)
TTS_VOLUME          = 1.0     # 0.0 → 1.0
STT_LANGUAGE        = "en-IN" # en-US, en-IN, hi-IN, etc.
LISTEN_TIMEOUT      = 5       # Max seconds to wait for speech
PHRASE_TIME_LIMIT   = 8       # Max seconds of speech to record

# ─── API Keys ────────────────────────────────────────────
PORCUPINE_KEY    = os.getenv("PORCUPINE_ACCESS_KEY")
WEATHER_API_KEY  = os.getenv("OPENWEATHER_API_KEY")
NEWS_API_KEY     = os.getenv("NEWS_API_KEY")
EMAIL_ADDRESS    = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD   = os.getenv("EMAIL_PASSWORD")

# ─── Feature Toggles ─────────────────────────────────────
ENABLE_WHATSAPP  = True
ENABLE_EMAIL     = True
ENABLE_BROWSER   = True
ENABLE_YOUTUBE   = True
ENABLE_REMINDERS = True
ENABLE_MEMORY    = True
ENABLE_GUI       = False   # Set True to launch with GUI

# ─── Memory ──────────────────────────────────────────────
MEMORY_DIR       = "memory"
CHAT_HISTORY_FILE = "memory/chat_history.json"
USER_DATA_FILE    = "memory/user_data.json"
MAX_HISTORY_TURNS = 20   # How many turns to keep in memory

# ─── Logging ─────────────────────────────────────────────
LOG_FILE   = "logs/app.log"
LOG_LEVEL  = "INFO"  # DEBUG, INFO, WARNING, ERROR