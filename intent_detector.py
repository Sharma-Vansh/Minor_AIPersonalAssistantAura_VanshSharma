"""
commands/intent_detector.py — Intent detection
✅ Spotify intent added
✅ Wake word stripped before detection
✅ "open whatsapp" → WHATSAPP intent
✅ "skip ad" → YOUTUBE intent
"""

from utils.logger import get_logger
from utils.helpers import contains_any
from utils.constants import *

logger = get_logger(__name__)

WAKE_WORDS = ["hey aura", "ok aura", "oi aura", "aura"]

# ── Spotify keywords ──────────────────────────────────────
SPOTIFY_KEYWORDS = [
    "spotify", "spotify par", "spotify pe", "spotify mein",
    "spotify par play", "play on spotify", "spotify me chala"
]

SPOTIFY_CONTROL = [
    "next song", "previous song", "agla song", "pichla song",
    "spotify pause", "spotify resume", "spotify next", "spotify back"
]


class IntentDetector:

    def detect(self, text: str) -> str:
        text = text.lower().strip()

        # ── Strip wake word ──────────────────────────────
        for wake in sorted(WAKE_WORDS, key=len, reverse=True):
            if text.startswith(wake):
                text = text[len(wake):].strip()
                break

        logger.debug(f"Detecting intent (cleaned): {text}")

        # ── WhatsApp ─────────────────────────────────────
        WHATSAPP_OPEN = ["open whatsapp", "whatsapp kholo", "start whatsapp"]
        if any(text.startswith(p) for p in WHATSAPP_OPEN):
            return INTENT_WHATSAPP
        if contains_any(text, WHATSAPP_KEYWORDS):
            if any(w in text for w in ["send", "message", "text", "msg", "whatsapp", "wa"]):
                return INTENT_WHATSAPP

        # ── Close App ────────────────────────────────────
        if contains_any(text, CLOSE_APP_KEYWORDS):
            if not any(w in text for w in ["shutdown", "restart", "computer", "pc", "system"]):
                return INTENT_CLOSE_APP

        # ── Email ────────────────────────────────────────
        if contains_any(text, EMAIL_KEYWORDS):
            return INTENT_EMAIL

        # ── File ─────────────────────────────────────────
        if contains_any(text, FILE_KEYWORDS):
            return INTENT_FILE

        # ── Spotify ──────────────────────────────────────
        if contains_any(text, SPOTIFY_KEYWORDS) or contains_any(text, SPOTIFY_CONTROL):
            return INTENT_SPOTIFY

        # ── Open App ─────────────────────────────────────
        if contains_any(text, OPEN_APP_KEYWORDS):
            if not any(w in text for w in ["play", "send", "message", "search", "whatsapp", "spotify"]):
                return INTENT_OPEN_APP

        # ── YouTube ──────────────────────────────────────
        if contains_any(text, YOUTUBE_KEYWORDS):
            return INTENT_YOUTUBE

        # ── Browser ──────────────────────────────────────
        if contains_any(text, BROWSER_KEYWORDS):
            return INTENT_BROWSER

        # ── Weather ──────────────────────────────────────
        if contains_any(text, WEATHER_KEYWORDS):
            return INTENT_WEATHER

        # ── News ─────────────────────────────────────────
        if contains_any(text, NEWS_KEYWORDS):
            return INTENT_NEWS

        # ── Reminder ─────────────────────────────────────
        if contains_any(text, REMINDER_KEYWORDS):
            return INTENT_REMINDER

        # ── System ───────────────────────────────────────
        if contains_any(text, SYSTEM_KEYWORDS):
            return INTENT_SYSTEM

        # ── Default: AI chat ─────────────────────────────
        return INTENT_CHAT


# ── Singleton ─────────────────────────────────────────────
_detector = None

def detect_intent(text: str) -> str:
    global _detector
    if _detector is None:
        _detector = IntentDetector()
    return _detector.detect(text)