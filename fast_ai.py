"""
ai/fast_ai.py — Offline fallback AI when Groq / internet is unavailable
Uses simple rule-based responses for common questions
so Aura never goes completely silent even without internet
"""

import random
from utils.logger import get_logger
from utils.helpers import get_greeting, get_current_time, get_current_date
from config import USER_NAME

logger = get_logger(__name__)


# ── Hardcoded smart responses for common queries ──────────
RESPONSE_MAP = {
    # Greetings
    ("hello", "hi", "hey", "namaste", "hola"): [
        f"{get_greeting()} {USER_NAME}! How can I help you?",
        f"Hey {USER_NAME}! What's up?",
        f"Hello! I'm listening.",
    ],
    # Time
    ("time", "what time", "bata time", "kitne baje"): [
        f"It is {get_current_time()} right now.",
        f"The time is {get_current_time()}.",
    ],
    # Date
    ("date", "today", "aaj", "din", "what day"): [
        f"Today is {get_current_date()}.",
        f"It's {get_current_date()} today.",
    ],
    # How are you
    ("how are you", "kaisa hai", "kya haal", "you okay"): [
        "I'm doing great, thanks for asking! How about you?",
        "All good on my end! How can I help you?",
        "Running perfectly! What can I do for you?",
    ],
    # Name
    ("your name", "tera naam", "who are you", "kaun hai"): [
        "I am Aura, your personal AI assistant!",
        "My name is Aura. I'm here to help you!",
    ],
    # Thanks
    ("thank", "thanks", "shukriya", "dhanyawad"): [
        "You're welcome!",
        "Happy to help!",
        "Anytime!",
    ],
    # Bye
    ("bye", "goodbye", "alvida", "quit", "exit", "stop"): [
        "Goodbye! Have a great day!",
        "See you later! Take care!",
        "Alvida! Call me when you need me.",
    ],
    # Joke
    ("joke", "mazak", "funny", "laugh", "haha"): [
        "Why don't scientists trust atoms? Because they make up everything!",
        "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
        "Why did the AI go to school? To improve its language model!",
    ],
}


class FastAI:
    """
    Simple offline AI using pattern matching.
    No internet needed. Used as fallback when Groq is down.
    """

    def respond(self, user_input: str) -> str | None:
        """
        Try to match user input to a known pattern.
        Returns a response string, or None if no match found.
        """
        text = user_input.lower().strip()

        for keywords, responses in RESPONSE_MAP.items():
            if any(kw in text for kw in keywords):
                reply = random.choice(responses)
                logger.info(f"FastAI matched response for: {text}")
                return reply

        logger.debug(f"FastAI: no match for '{text}'")
        return None


# ── Singleton instance ────────────────────────────────────
_fast_ai = FastAI()

def fast_respond(text: str) -> str | None:
    """
    Module-level shortcut:
        from ai.fast_ai import fast_respond
        reply = fast_respond("what time is it")
    """
    return _fast_ai.respond(text)


# ── Quick test ────────────────────────────────────────────
if __name__ == "__main__":
    tests = ["hello", "what time is it", "tell me a joke", "thank you", "bye"]
    for t in tests:
        reply = fast_respond(t)
        print(f"You: {t}\nAura: {reply}\n")