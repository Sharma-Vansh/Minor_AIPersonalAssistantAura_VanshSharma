"""
ai/ai_router.py — The brain's traffic controller
Decides: use FastAI (offline) → or Groq (online)?
Also connects with the command router for automation tasks.
"""

from utils.logger import get_logger
from utils.helpers import contains_any
from ai.fast_ai import fast_respond
from ai.groq_ai import ask_groq
from utils.constants import (
    WEATHER_KEYWORDS, NEWS_KEYWORDS, REMINDER_KEYWORDS,
    WHATSAPP_KEYWORDS, EMAIL_KEYWORDS, YOUTUBE_KEYWORDS,
    BROWSER_KEYWORDS, SYSTEM_KEYWORDS, FILE_KEYWORDS,
    INTENT_CHAT
)

logger = get_logger(__name__)


# Keywords that mean the user wants an ACTION not a chat
ACTION_KEYWORDS = (
    WEATHER_KEYWORDS + NEWS_KEYWORDS + REMINDER_KEYWORDS +
    WHATSAPP_KEYWORDS + EMAIL_KEYWORDS + YOUTUBE_KEYWORDS +
    BROWSER_KEYWORDS + SYSTEM_KEYWORDS + FILE_KEYWORDS
)

# Questions FastAI can handle offline (no Groq needed)
SIMPLE_KEYWORDS = [
    "hello", "hi", "hey", "time", "date", "today", "joke",
    "how are you", "your name", "who are you", "thank", "bye",
    "goodbye", "namaste", "kaisa", "shukriya", "alvida"
]


class AIRouter:
    def __init__(self):
        self.groq_available = self._check_groq()
        logger.info(f"AIRouter initialized. Groq available: {self.groq_available}")

    def _check_groq(self) -> bool:
        """Check if Groq API key is configured."""
        from config import GROQ_API_KEY
        return bool(GROQ_API_KEY)

    def get_response(self, user_input: str) -> tuple[str, str]:
        """
        Main entry point. Given user text, returns:
        (response_text, intent_type)

        intent_type can be:
          "chat"      → AI answered it conversationally
          "action"    → needs automation (handled by command_router)
          "offline"   → answered offline by FastAI
        """
        if not user_input or not user_input.strip():
            return "I didn't catch that. Say it again please.", INTENT_CHAT

        text = user_input.lower().strip()
        logger.info(f"AIRouter received: {text}")

        # ── Step 1: Is this an ACTION command? ───────────────
        # If yes, hand off to command_router — don't use AI for this
        if contains_any(text, ACTION_KEYWORDS):
            logger.info("Detected action intent — routing to command_router.")
            return None, "action"  # command_router handles it

        # ── Step 2: Can FastAI handle it offline? ────────────
        if contains_any(text, SIMPLE_KEYWORDS):
            offline_reply = fast_respond(text)
            if offline_reply:
                logger.info("Handled by FastAI (offline).")
                return offline_reply, "offline"

        # ── Step 3: Use Groq for everything else ─────────────
        if self.groq_available:
            logger.info("Routing to Groq AI.")
            reply = ask_groq(user_input)
            return reply, INTENT_CHAT

        # ── Step 4: Groq not available — use FastAI as last resort ──
        offline_reply = fast_respond(text)
        if offline_reply:
            return offline_reply, "offline"

        return (
            "I am offline right now and cannot answer that. "
            "Please check your internet connection.",
            "offline"
        )

    def chat_only(self, user_input: str) -> str:
        """
        Force a conversational AI reply — skip action detection.
        Use this when you already know it's a chat message.
        """
        if self.groq_available:
            return ask_groq(user_input)
        return fast_respond(user_input) or "I'm not sure about that one."

    def refresh_groq_status(self):
        """Re-check if Groq is available (call after network reconnect)."""
        self.groq_available = self._check_groq()


# ── Singleton instance ────────────────────────────────────
_router = None

def get_ai_response(user_input: str) -> tuple[str, str]:
    """
    Module-level shortcut. Use this in main.py:
        from ai.ai_router import get_ai_response
        response, intent = get_ai_response("What is the weather today?")
    """
    global _router
    if _router is None:
        _router = AIRouter()
    return _router.get_response(user_input)


# ── Quick test ────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        "Hello Aura!",
        "What time is it?",
        "Play Bollywood songs on YouTube",
        "What is quantum computing?",
        "Remind me to drink water in 10 minutes",
        "Tell me a joke",
    ]
    for t in tests:
        response, intent = get_ai_response(t)
        print(f"\nYou: {t}")
        print(f"Intent: {intent}")
        print(f"Aura: {response if response else '[→ handled by automation]'}")