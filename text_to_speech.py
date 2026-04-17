"""
voice/text_to_speech.py — Aura speaks with a natural Human AI Voice.
Uses Microsoft Edge Neural TTS (edge-tts) for a beautiful Indian English female voice.
Falls back to pyttsx3 (offline robotic voice) if no internet is available.
"""

import os
import sys
import asyncio
import tempfile
# Hide pygame welcome message BEFORE importing
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from utils.logger import get_logger
from config import TTS_RATE, TTS_VOLUME

logger = get_logger(__name__)

class TextToSpeech:
    def __init__(self):
        self.offline_engine = None
        self._init_offline_engine()
        # The Edge-TTS premium Indian Female Neural Voice (Indian English)
        self.primary_voice = "en-IN-NeerjaNeural"

    def _init_offline_engine(self):
        """Initialize the fallback offline robotic TTS."""
        import pyttsx3
        try:
            self.offline_engine = pyttsx3.init()
            self.offline_engine.setProperty("rate", TTS_RATE)
            self.offline_engine.setProperty("volume", TTS_VOLUME)
            
            # Find a decent female voice
            voices = self.offline_engine.getProperty("voices")
            for v in voices:
                name = v.name.lower()
                if "zira" in name or "heera" in name or "female" in name:
                    self.offline_engine.setProperty("voice", v.id)
                    break
        except Exception as e:
            logger.error(f"Fallback offline TTS init failed: {e}")
            self.offline_engine = None

    def speak(self, text: str):
        """Speak the given text. Tries Premium Human Voice first, falls back if offline."""
        if not text or not text.strip():
            return

        logger.info(f"Aura says: {text}")
        print(f"\n🔊 Aura: {text}\n")

        # Use a new event loop cleanly to avoid deprecation warnings
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
            
        try:
            loop.run_until_complete(self._speak_edge_tts(text))
        except Exception as e:
            logger.warning(f"Premium Voice failed (No Internet?): {e}. Falling back to offline voice.")
            self._speak_offline(text)

    async def _speak_edge_tts(self, text: str):
        """Generate and play high-quality human speech using edge-tts."""
        import edge_tts
        
        # Create a temporary file to store the high-quality MP3
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "aura_voice.mp3")

        # Generate audio using the Neerja (Indian English Female) Neural voice
        communicate = edge_tts.Communicate(text, self.primary_voice)
        await communicate.save(temp_file)

        # Play it gracefully using PyGame
        pygame.mixer.init()
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        # Wait until audio finishes playing
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
            
        # Cleanup
        pygame.mixer.music.unload()
        pygame.mixer.quit()
        try:
            os.remove(temp_file)
        except:
            pass

    def _speak_offline(self, text: str):
        """Fallback to the classic offline Windows robotic Siri voice."""
        if not self.offline_engine:
            return
            
        try:
            import pyttsx3
            # In some Windows systems, SAPI gets stuck if not re-initialized inside a new thread
            if sys.platform == "win32":
                import pythoncom
                import win32com.client
                pythoncom.CoInitialize()
                sapi = win32com.client.Dispatch("SAPI.SpVoice")
                sapi.Rate = 2
                sapi.Volume = int(TTS_VOLUME * 100)
                
                # Pick female voice
                for voice in sapi.GetVoices():
                    desc = voice.GetDescription().lower()
                    if "zira" in desc or "female" in desc or "heera" in desc:
                        sapi.Voice = voice
                        break
                sapi.Speak(text)
            else:
                self.offline_engine.say(text)
                self.offline_engine.runAndWait()
        except Exception as e:
            logger.error(f"Offline TTS also failed: {e}")

# ── Singleton instance ────────────────────────────────────
_tts = None

def speak(text: str):
    global _tts
    if _tts is None:
        _tts = TextToSpeech()
    _tts.speak(text)

if __name__ == "__main__":
    # Test Premium real-human Hindi accent
    speak("नमस्ते बॉस! मैं औरा हूँ। अब मैं बिल्कुल इंसानों जैसी हिंदी आवाज़ में बात कर सकती हूँ।")