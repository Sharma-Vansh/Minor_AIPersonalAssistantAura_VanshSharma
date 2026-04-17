"""
voice/wake_word.py — Continuously listens for the wake word "Aura"
Uses Porcupine (free, offline, very accurate) by Picovoice
"""

import struct
import pyaudio
from utils.logger import get_logger
from config import PORCUPINE_KEY, WAKE_WORD_SENSITIVITY

logger = get_logger(__name__)


class WakeWordDetector:
    def __init__(self):
        self.porcupine = None
        self.audio_stream = None
        self.pa = None
        self._init_porcupine()

    def _init_porcupine(self):
        """Set up the Porcupine wake word engine."""
        try:
            import pvporcupine
            # "Aura" is not a built-in keyword, so we use "jarvis" or "computer"
            # as placeholder. To use "Aura" exactly, download the custom keyword
            # file from: console.picovoice.ai (free account)
            # Then replace keyword_paths=[...] below with your .ppn file path.

            self.porcupine = pvporcupine.create(
                access_key=PORCUPINE_KEY,
                keywords=["jarvis"],          # ← Replace with custom "Aura" keyword
                sensitivities=[WAKE_WORD_SENSITIVITY]
            )

            self.pa = pyaudio.PyAudio()
            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )
            logger.info("Porcupine wake word detector initialized.")

        except ImportError:
            logger.warning("pvporcupine not installed. Using simple keyword fallback.")
            self.porcupine = None
        except Exception as e:
            logger.error(f"Porcupine init failed: {e}")
            self.porcupine = None

    def wait_for_wake_word(self) -> bool:
        """
        Blocks until the wake word is detected.
        Returns True when detected.
        Uses Porcupine if available, otherwise falls back to STT-based detection.
        """
        if self.porcupine and self.audio_stream:
            return self._porcupine_listen()
        else:
            return self._stt_fallback_listen()

    def _porcupine_listen(self) -> bool:
        """Listen via Porcupine (accurate, offline, low CPU)."""
        logger.info(f'Waiting for wake word... (say "Aura")')
        print(f'😴 Aura is sleeping... Say "Aura" to wake up!')

        while True:
            try:
                pcm = self.audio_stream.read(
                    self.porcupine.frame_length,
                    exception_on_overflow=False
                )
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                result = self.porcupine.process(pcm)

                if result >= 0:
                    logger.info("Wake word detected!")
                    print("✅ Wake word detected!")
                    return True

            except KeyboardInterrupt:
                logger.info("Stopped by user.")
                return False
            except Exception as e:
                logger.error(f"Porcupine listen error: {e}")
                return False

    def _stt_fallback_listen(self) -> bool:
        """
        Fallback: uses SpeechRecognition to detect the wake word.
        Less accurate but works without Porcupine API key.
        """
        import speech_recognition as sr
        from config import WAKE_WORD

        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True
        mic = sr.Microphone()

        logger.info(f'[Fallback] Waiting for wake word "{WAKE_WORD}"...')
        print(f'😴 Say "{WAKE_WORD}" to activate Aura...')

        while True:
            try:
                with mic as source:
                    audio = recognizer.listen(source, timeout=None, phrase_time_limit=4)

                text = recognizer.recognize_google(audio).lower()
                logger.debug(f"Heard: {text}")

                if WAKE_WORD.lower() in text:
                    logger.info(f"Wake word '{WAKE_WORD}' detected via STT fallback!")
                    print(f"✅ Aura activated!")
                    return True

            except sr.UnknownValueError:
                pass  # Silence — keep listening
            except sr.WaitTimeoutError:
                pass  # No speech — keep listening
            except KeyboardInterrupt:
                return False
            except Exception as e:
                logger.error(f"Wake word fallback error: {e}")

    def cleanup(self):
        """Release mic and Porcupine resources."""
        if self.audio_stream:
            self.audio_stream.close()
        if self.pa:
            self.pa.terminate()
        if self.porcupine:
            self.porcupine.delete()
        logger.info("Wake word detector cleaned up.")


# ── Quick test ────────────────────────────────────────────
if __name__ == "__main__":
    detector = WakeWordDetector()
    detected = detector.wait_for_wake_word()
    if detected:
        from voice.text_to_speech import speak
        speak("Yes? I am here. How can I help you?")
    detector.cleanup()