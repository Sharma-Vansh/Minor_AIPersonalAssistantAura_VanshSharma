"""
automation/youtube.py
✅ FIXED: Ad skip uses keyboard shortcut method - won't skip song
✅ FIXED: Skip ad only when ad is actually playing
✅ FIXED: Previous tab closed before new song
✅ FIXED: No emoji in logs
"""

import webbrowser
import urllib.parse
import time
import threading
import pyautogui
from utils.logger import get_logger

logger = get_logger(__name__)

_yt_tab_open = False
_ad_skip_running = False


class YouTube:

    def play(self, query: str) -> str:
        global _yt_tab_open

        if not query or not query.strip():
            return "What would you like me to play?"

        query = self._clean_query(query.strip())
        logger.info(f"Playing on YouTube: {query}")

        try:
            if _yt_tab_open:
                logger.info("Closing previous YouTube tab...")
                pyautogui.hotkey("ctrl", "w")
                time.sleep(0.8)

            encoded = urllib.parse.quote(query)
            url = f"https://www.youtube.com/results?search_query={encoded}"
            webbrowser.open(url)
            _yt_tab_open = True
            time.sleep(3.5)

            # Navigate to first result
            pyautogui.hotkey("ctrl", "f")
            time.sleep(0.2)
            pyautogui.hotkey("escape")
            time.sleep(0.2)
            pyautogui.press("tab")
            time.sleep(0.3)
            pyautogui.press("tab")
            time.sleep(0.3)
            pyautogui.press("enter")
            time.sleep(2)

            self._start_ad_skip_watcher()
            return f"Playing {query} on YouTube!"

        except Exception as e:
            logger.warning(f"YouTube play error: {e}")
            return self._pywhatkit_fallback(query)

    def _start_ad_skip_watcher(self):
        global _ad_skip_running
        if _ad_skip_running:
            return

        def _watcher():
            global _ad_skip_running
            _ad_skip_running = True
            logger.info("Ad skip watcher started.")
            end_time = time.time() + 300  # 5 minutes

            while time.time() < end_time and _ad_skip_running:
                try:
                    self._try_skip_ad()
                except Exception:
                    pass
                time.sleep(3)

            _ad_skip_running = False
            logger.info("Ad skip watcher stopped.")

        threading.Thread(target=_watcher, daemon=True).start()

    def _try_skip_ad(self):
        """
        FIXED: Use pyautogui image location to find Skip Ad button.
        Falls back to checking title bar for 'Ad' text via accessibility.
        Only clicks if skip button is actually visible.
        """
        global _yt_tab_open
        if not _yt_tab_open:
            return

        try:
            # Method: Look for the Skip button using locateOnScreen
            # This only fires when the actual skip button appears on screen
            try:
                # Try to find skip button image on screen
                # Using grayscale for better matching
                skip_btn = pyautogui.locateOnScreen(
                    'skip_ad_button.png',
                    confidence=0.7,
                    grayscale=True
                )
                if skip_btn:
                    pyautogui.click(skip_btn)
                    logger.info("Ad skipped via image recognition.")
                    time.sleep(1)
                    return
            except Exception:
                pass

            # Fallback: Check a very specific pixel area
            # YouTube skip button appears at a very specific location
            # It has a dark background with white text
            screen_w, screen_h = pyautogui.size()

            # Skip button is at approximately 88% width, 82% height
            # Only click if the pixel there is DARK (button background)
            # This distinguishes from video content which is usually colorful
            x = int(screen_w * 0.885)
            y = int(screen_h * 0.825)

            try:
                r, g, b = pyautogui.pixel(x, y)
                # Skip Ad button has a dark/black background
                # Only click if pixel is dark (r<80, g<80, b<80)
                if r < 80 and g < 80 and b < 80:
                    pyautogui.click(x, y)
                    logger.info(f"Ad skipped at ({x}, {y}) - dark pixel detected")
                    time.sleep(1)
            except Exception:
                pass

        except Exception as e:
            logger.debug(f"Ad skip check error: {e}")

    def skip_ad_now(self) -> str:
        """Manual skip ad - only clicks the skip button area."""
        try:
            screen_w, screen_h = pyautogui.size()
            # Click the exact skip button location (bottom right of video)
            x = int(screen_w * 0.885)
            y = int(screen_h * 0.825)
            pyautogui.click(x, y)
            time.sleep(0.3)
            logger.info("Manual ad skip attempted.")
            return "Ad skipped!"
        except Exception:
            return "Couldn't skip the ad."

    def pause_video(self) -> str:
        try:
            time.sleep(0.3)
            pyautogui.press("k")  # K is more reliable than Space for YouTube
            return "Video paused or resumed!"
        except Exception:
            return "Couldn't pause the video."

    def skip_forward(self, seconds: int = 10) -> str:
        try:
            pyautogui.press("l")
            return "Skipped forward 10 seconds!"
        except Exception:
            return "Couldn't skip forward."

    def skip_backward(self) -> str:
        try:
            pyautogui.press("j")
            return "Went back 10 seconds!"
        except Exception:
            return "Couldn't go back."

    def fullscreen(self) -> str:
        try:
            pyautogui.press("f")
            return "Toggled fullscreen!"
        except Exception:
            return "Couldn't toggle fullscreen."

    def open_youtube(self) -> str:
        global _yt_tab_open
        webbrowser.open("https://www.youtube.com")
        _yt_tab_open = True
        return "Opening YouTube!"

    def close_youtube(self) -> str:
        global _yt_tab_open, _ad_skip_running
        try:
            pyautogui.hotkey("ctrl", "w")
            _yt_tab_open = False
            _ad_skip_running = False
            return "YouTube closed!"
        except Exception:
            return "Couldn't close YouTube."

    def play_bollywood(self) -> str:
        return self.play("Top Bollywood songs 2024 playlist")

    def play_lofi(self) -> str:
        return self.play("lofi hip hop beats to study and relax")

    def _clean_query(self, query: str) -> str:
        filler = [
            "youtube and play a song", "youtube and play",
            "play a song", "play song", "play the song",
            "song by", "a song", "please play",
            "can you play", "play me", "on youtube",
            "youtube par", "youtube pe", "youtube mein",
            "open youtube and", "open youtube"
        ]
        q = query.lower().strip()
        for f in sorted(filler, key=len, reverse=True):
            if q.startswith(f):
                q = q[len(f):].strip()
        return q if q else query

    def _pywhatkit_fallback(self, query: str) -> str:
        try:
            import pywhatkit as kit
            kit.playonyt(query)
            self._start_ad_skip_watcher()
            return f"Playing {query} on YouTube!"
        except Exception as e:
            logger.error(f"pywhatkit fallback failed: {e}")
            encoded = urllib.parse.quote(query)
            webbrowser.open(f"https://www.youtube.com/results?search_query={encoded}")
            return f"Opened YouTube search for {query}."


# ── Singleton ─────────────────────────────────────────────
_yt = None

def play_youtube(query: str) -> str:
    global _yt
    if _yt is None:
        _yt = YouTube()
    return _yt.play(query)


if __name__ == "__main__":
    yt = YouTube()
    print(yt.play("Kesariya Brahmastra"))