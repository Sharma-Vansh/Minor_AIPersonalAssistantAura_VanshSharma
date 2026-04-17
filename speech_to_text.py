"""
voice/speech_to_text.py — Converts your spoken words into text
Uses SpeechRecognition with Google STT (free, needs internet)
Falls back to offline Whisper if Google fails
"""

import speech_recognition as sr
from utils.logger import get_logger
from config import STT_LANGUAGE, LISTEN_TIMEOUT, PHRASE_TIME_LIMIT

logger = get_logger(__name__)


class SpeechToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()

        # Tune for indoor use — reduce sensitivity to background noise
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # Seconds of silence = end of sentence

        self._calibrate()

    def _calibrate(self):
        """Adjust for ambient noise when Aura starts up."""
        logger.info("Calibrating microphone for ambient noise...")
        try:
            # Create a fresh mic instance just for calibration
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
            logger.info("Microphone calibrated.")
        except Exception as e:
            logger.warning(f"Mic calibration failed: {e}")

    def listen(self) -> str | None:
        """
        Listen from mic and return recognized text.
        Creates a fresh Microphone() every call to avoid
        'already inside a context manager' thread conflicts.
        Returns None if nothing was heard or recognition failed.
        """
        print("🎤 Listening...")
        try:
            # Fresh Microphone() every call — safe for multi-threaded GUI
            with sr.Microphone() as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=LISTEN_TIMEOUT,
                    phrase_time_limit=PHRASE_TIME_LIMIT
                )

            return self._recognize(audio)

        except sr.WaitTimeoutError:
            logger.debug("No speech detected within timeout.")
            return None
        except Exception as e:
            logger.error(f"Listening error: {e}")
            return None

    def _recognize(self, audio) -> str | None:
        """Try Google STT first, then Whisper as fallback."""

        # ── Google STT (free, fast, needs internet) ──
        try:
            text = self.recognizer.recognize_google(audio, language=STT_LANGUAGE)
            text = text.strip().lower()
            logger.info(f"You said: {text}")
            print(f"🗣️  You: {text}")
            return text
        except sr.UnknownValueError:
            logger.debug("Google STT: speech not understood.")
            return None
        except sr.RequestError as e:
            logger.warning(f"Google STT unavailable: {e}. Trying Whisper...")

        # ── Whisper fallback (offline, slower but works without internet) ──
        try:
            text = self.recognizer.recognize_whisper(audio, language="english")
            text = text.strip().lower()
            logger.info(f"Whisper recognized: {text}")
            print(f"🗣️  You (whisper): {text}")
            return text
        except Exception as e:
            logger.error(f"Whisper also failed: {e}")

        return None

    def listen_once(self) -> str | None:
        """Alias for listen() — for clarity in code."""
        return self.listen()


# ── Singleton instance ────────────────────────────────────
_stt = None

def listen() -> str | None:
    """
    Module-level shortcut. Use this everywhere:
        from voice.speech_to_text import listen
        text = listen()
    """
    global _stt
    if _stt is None:
        _stt = SpeechToText()
    return _stt.listen()


# ── Quick test ────────────────────────────────────────────
if __name__ == "__main__":
    from voice.text_to_speech import speak
    speak("Microphone test. Please say something.")
    result = listen()
    if result:
        speak(f"I heard you say: {result}")
    else:
        speak("Sorry, I did not catch that.")