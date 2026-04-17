"""
utils/constants.py — All intent constants and keyword lists
✅ INTENT_SPOTIFY added
"""

# ── Intent Labels ─────────────────────────────────────────
INTENT_YOUTUBE   = "youtube"
INTENT_BROWSER   = "browser"
INTENT_WHATSAPP  = "whatsapp"
INTENT_SYSTEM    = "system"
INTENT_WEATHER   = "weather"
INTENT_NEWS      = "news"
INTENT_REMINDER  = "reminder"
INTENT_EMAIL     = "email"
INTENT_FILE      = "file"
INTENT_OPEN_APP  = "open_app"
INTENT_CLOSE_APP = "close_app"
INTENT_SPOTIFY   = "spotify"   # ✅ NEW
INTENT_CHAT      = "chat"

# ── Keyword Lists ─────────────────────────────────────────

YOUTUBE_KEYWORDS = [
    "youtube", "play", "video", "song", "music", "gana",
    "bajao", "chala", "watch", "dekho", "yt", "skip ad",
    "pause video", "fullscreen", "lofi", "bollywood"
]

WHATSAPP_KEYWORDS = [
    "whatsapp", "wa", "message", "msg", "send", "text",
    "bhejo", "likho", "bata do"
]

BROWSER_KEYWORDS = [
    "search", "google", "open", "website", "browser",
    "internet", "chrome", "find", "look up", "dhundo",
    "khojo", "safari", "firefox", "edge"
]

EMAIL_KEYWORDS = [
    "email", "mail", "gmail", "outlook", "inbox",
    "send email", "compose", "read email", "check email"
]

SYSTEM_KEYWORDS = [
    "volume", "brightness", "battery", "shutdown", "restart",
    "sleep", "lock", "mute", "cpu", "ram", "system",
    "awaaz", "reboot", "screen"
]

WEATHER_KEYWORDS = [
    "weather", "temperature", "forecast", "rain", "sunny",
    "mausam", "barish", "garmi", "sardi", "humidity"
]

NEWS_KEYWORDS = [
    "news", "headlines", "khabar", "latest news",
    "today news", "top stories", "current events"
]

REMINDER_KEYWORDS = [
    "remind", "reminder", "alarm", "timer", "alert",
    "yaad", "yaad dilao", "set alarm", "set reminder",
    "minutes", "hours", "baad mein"
]

FILE_KEYWORDS = [
    "file", "folder", "document", "desktop", "downloads",
    "search file", "find file", "open file", "create file",
    "delete file", "disk space", "storage"
]

OPEN_APP_KEYWORDS = [
    "open", "launch", "start", "run", "load",
    "kholo", "chalu karo", "shuru karo", "boot"
]

CLOSE_APP_KEYWORDS = [
    "close", "shut", "exit", "quit", "kill",
    "terminate", "end", "band karo", "band kar do", "hat jao"
]

SPOTIFY_KEYWORDS = [
    "spotify", "spotify par", "spotify pe", "spotify mein",
    "play on spotify", "spotify me chala", "spotify par play"
]