"""
main.py — Aura Voice AI Assistant
The main entry point. Boots all systems and runs the main loop.

Run with:
    python main.py
"""

import os
import sys
import time
import threading

# ── Make sure we can import from project root ─────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import get_logger
from utils.helpers import get_greeting, get_current_time
from config import (
    USER_NAME, VOICE_ENABLED, ENABLE_MEMORY,
    ENABLE_GUI, ENABLE_REMINDERS
)

logger = get_logger(__name__)


# ═══════════════════════════════════════════════════════════
#  BOOT SEQUENCE
# ═══════════════════════════════════════════════════════════

def boot_banner():
    """Print Aura startup banner in terminal."""
    banner = f"""
╔══════════════════════════════════════════╗
║                                          ║
║        ✦  A U R A  ✦                    ║
║     Voice AI Assistant  v1.0             ║
║                                          ║
║  {get_greeting()}, {USER_NAME}!{" " * max(0, 24 - len(USER_NAME))}║
║  Time: {get_current_time()}{" " * max(0, 33 - len(get_current_time()))}║
║                                          ║
╚══════════════════════════════════════════╝
"""
    print(banner)


def load_voice():
    """Load TTS and STT modules."""
    from voice.text_to_speech import speak, TextToSpeech
    from voice.speech_to_text import SpeechToText

    logger.info("Loading voice systems...")
    tts = TextToSpeech()
    stt = SpeechToText()
    logger.info("✅ Voice systems ready.")
    return tts, stt


def load_wake_word():
    """Load wake word detector."""
    from voice.wake_word import WakeWordDetector
    logger.info("Loading wake word detector...")
    wwd = WakeWordDetector()
    logger.info("✅ Wake word detector ready.")
    return wwd


def load_ai():
    """Load AI router (Groq + FastAI)."""
    from ai.ai_router import AIRouter
    logger.info("Loading AI brain...")
    router = AIRouter()
    logger.info(f"✅ AI brain ready. Groq available: {router.groq_available}")
    return router


def load_commands():
    """Load intent detector and command router."""
    from commands.intent_detector import IntentDetector
    from commands.entity_extractor import EntityExtractor
    from commands.command_router import CommandRouter
    logger.info("Loading command system...")
    intent  = IntentDetector()
    entity  = EntityExtractor()
    cmd     = CommandRouter()
    logger.info("✅ Command system ready.")
    return intent, entity, cmd


def load_memory():
    """Load memory manager."""
    if not ENABLE_MEMORY:
        return None
    try:
        from memory.memory_manager import MemoryManager
        logger.info("Loading memory system...")
        mem = MemoryManager()
        logger.info("✅ Memory system ready.")
        return mem
    except Exception as e:
        logger.warning(f"Memory system failed to load: {e}")
        return None


# ═══════════════════════════════════════════════════════════
#  CORE LOGIC — Process one command
# ═══════════════════════════════════════════════════════════

def process_input(
    user_text: str,
    tts,
    ai_router,
    intent_detector,
    entity_extractor,
    command_router,
    memory
):
    """
    Takes user text, figures out what to do, and responds.
    This is the brain of every interaction.
    """
    if not user_text or not user_text.strip():
        return

    user_text = user_text.strip().lower()
    logger.info(f"Processing: '{user_text}'")

    # ── Special commands ─────────────────────────────────
    if user_text in ("quit", "exit", "shutdown aura", "band kar", "stop"):
        tts.speak("Goodbye! Have a great day!")
        logger.info("Aura shutting down by user command.")
        sys.exit(0)

    if user_text in ("clear memory", "memory clear", "forget everything"):
        from ai.groq_ai import clear_memory
        clear_memory()
        if memory:
            memory.clear_history()
        tts.speak("Memory cleared. Starting fresh!")
        return

    # ── Step 1: Detect intent ────────────────────────────
    intent = intent_detector.detect(user_text)
    logger.info(f"Intent detected: {intent}")

    # ── Step 2: Extract entities ─────────────────────────
    entities = entity_extractor.extract(user_text)
    logger.debug(f"Entities: {entities}")

    # ── Step 3: Route to action OR AI ────────────────────
    from utils.constants import INTENT_CHAT

    if intent == INTENT_CHAT:
        # Pure conversation → send to AI brain
        response, _ = ai_router.get_response(user_text)
    else:
        # Automation task → send to command router
        response = command_router.route(intent, entities, user_text)

    # ── Step 4: Speak the response ───────────────────────
    if response:
        tts.speak(response)

    # ── Step 5: Save to memory ───────────────────────────
    if memory:
        memory.save_turn(user_text, response or "")


# ═══════════════════════════════════════════════════════════
#  MAIN LOOP — Voice mode
# ═══════════════════════════════════════════════════════════

def run_voice_mode(tts, stt, wake_word, ai_router, intent, entity, cmd, memory):
    """
    Full voice loop:
    1. Wait for wake word ("Aura")
    2. Listen to command
    3. Process and respond
    4. Go back to sleep
    """
    tts.speak(
        f"{get_greeting()} {USER_NAME}! "
        f"I am Aura, your personal assistant. "
        f"Say my name to wake me up!"
    )

    logger.info("Entering voice loop...")

    while True:
        try:
            # ── Wait for wake word ────────────────────────
            detected = wake_word.wait_for_wake_word()
            if not detected:
                continue

            # ── Wake up! ──────────────────────────────────
            tts.speak("Yes? I'm listening.")
            time.sleep(0.3)  # Small pause so mic doesn't pick up TTS echo

            # ── Listen for the command ────────────────────
            user_text = stt.listen()

            if not user_text:
                tts.speak("I didn't catch that. Please try again.")
                continue

            # ── Process the command ───────────────────────
            process_input(
                user_text, tts, ai_router,
                intent, entity, cmd, memory
            )

        except KeyboardInterrupt:
            tts.speak("Goodbye!")
            logger.info("Stopped by KeyboardInterrupt.")
            break
        except Exception as e:
            logger.error(f"Voice loop error: {e}")
            tts.speak("Something went wrong. I'm still here though!")
            continue


# ═══════════════════════════════════════════════════════════
#  MAIN LOOP — Text mode (fallback / dev mode)
# ═══════════════════════════════════════════════════════════

def run_text_mode(tts, ai_router, intent, entity, cmd, memory):
    """
    Text-only mode — type commands instead of speaking.
    Useful for testing without a microphone.
    """
    print("\n💬 Text mode active. Type your commands below.")
    print("    Type 'quit' to exit.\n")

    tts.speak(f"{get_greeting()} {USER_NAME}! Running in text mode. Type your command.")

    while True:
        try:
            user_text = input("You: ").strip()
            if not user_text:
                continue

            process_input(
                user_text, tts, ai_router,
                intent, entity, cmd, memory
            )

        except KeyboardInterrupt:
            tts.speak("Goodbye!")
            print("\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Text mode error: {e}")
            print(f"Error: {e}")


# ═══════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════

def main():
    boot_banner()
    logger.info("=== Aura starting up ===")

    # ── Create required directories ───────────────────────
    os.makedirs("logs",   exist_ok=True)
    os.makedirs("memory", exist_ok=True)

    # ── Load all systems ──────────────────────────────────
    print("🔄 Loading systems...\n")

    tts, stt   = load_voice()
    wake_word  = load_wake_word()
    ai_router  = load_ai()
    intent, entity, cmd = load_commands()
    memory     = load_memory()

    print("\n✅ All systems ready!\n")
    logger.info("All systems loaded successfully.")

    # ── Choose mode ───────────────────────────────────────
    # Pass --text flag to run in text mode (no mic needed)
    # e.g.:  python main.py --text
    if "--text" in sys.argv or not VOICE_ENABLED:
        run_text_mode(tts, ai_router, intent, entity, cmd, memory)
    else:
        run_voice_mode(tts, stt, wake_word, ai_router, intent, entity, cmd, memory)


if __name__ == "__main__":
    main()