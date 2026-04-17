"""
ai/groq_ai.py — Connects Aura to Groq's ultra-fast LLM API
Groq runs Llama3-70B at insane speed — perfect for a voice assistant
Get your FREE key at: https://console.groq.com
"""

from groq import Groq
from utils.logger import get_logger
from utils.helpers import truncate
from config import GROQ_API_KEY, GROQ_MODEL, AI_MAX_TOKENS, AI_TEMPERATURE
from ai.prompts import get_main_prompt

logger = get_logger(__name__)


class GroqAI:
    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is missing in your .env file!")

        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL
        self.conversation_history = []  # Keeps track of chat context
        logger.info(f"Groq AI initialized with model: {self.model}")

    def chat(self, user_message: str, system_prompt: str = None) -> str:
        """
        Send a message to Groq and get a response.
        Maintains conversation history for context.
        """
        if not user_message or not user_message.strip():
            return "I didn't catch that. Could you say it again?"

        # Use provided system prompt or default Aura personality
        if system_prompt is None:
            system_prompt = get_main_prompt()

        # Build messages list: system + history + new user message
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_message})

        try:
            logger.debug(f"Sending to Groq: {user_message}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=AI_MAX_TOKENS,
                temperature=AI_TEMPERATURE,
            )

            reply = response.choices[0].message.content.strip()
            logger.debug(f"Groq replied: {reply}")

            # Save this turn to conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": reply})

            # Keep history from growing too large (last 20 messages = 10 turns)
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            # Truncate for TTS — keep it speakable
            return truncate(reply, max_chars=400)

        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return "Sorry, I am having trouble thinking right now. Please try again."

    def quick_ask(self, prompt: str, system: str = None) -> str:
        """
        One-shot question — no conversation history.
        Use for summaries, email writing, one-off tasks.
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=AI_MAX_TOKENS,
                temperature=AI_TEMPERATURE,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq quick_ask error: {e}")
            return "I could not process that right now."

    def clear_history(self):
        """Clear conversation memory — start fresh."""
        self.conversation_history = []
        logger.info("Conversation history cleared.")

    def set_model(self, model_name: str):
        """Switch Groq model on the fly."""
        self.model = model_name
        logger.info(f"Groq model switched to: {model_name}")


# ── Singleton instance ────────────────────────────────────
_groq = None

def ask_groq(message: str, system_prompt: str = None) -> str:
    """
    Module-level shortcut. Use this anywhere in Aura:
        from ai.groq_ai import ask_groq
        reply = ask_groq("What is the capital of India?")
    """
    global _groq
    if _groq is None:
        _groq = GroqAI()
    return _groq.chat(message, system_prompt)


def quick_ask(prompt: str, system: str = None) -> str:
    """One-shot ask without conversation context."""
    global _groq
    if _groq is None:
        _groq = GroqAI()
    return _groq.quick_ask(prompt, system)


def clear_memory():
    """Reset Aura's conversation history."""
    global _groq
    if _groq:
        _groq.clear_history()


# ── Quick test ────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing Groq AI...\n")
    
    reply = ask_groq("Hello Aura! Introduce yourself in 2 sentences.")
    print(f"Aura: {reply}\n")

    reply = ask_groq("What is 25 multiplied by 4?")
    print(f"Aura: {reply}\n")

    reply = ask_groq("Tell me a very short joke.")
    print(f"Aura: {reply}\n")