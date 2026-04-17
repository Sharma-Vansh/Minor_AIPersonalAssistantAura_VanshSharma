"""
automation/spotify.py
✅ Open Spotify Desktop
✅ Play song by voice
✅ Pause / Resume / Next / Previous
✅ Volume control
✅ FIXED: No emoji in logger (Windows crash fix)
"""

import subprocess
import time
import urllib.parse
import pyautogui
from utils.logger import get_logger

logger = get_logger(__name__)


class Spotify:

    def open_spotify(self) -> str:
        try:
            subprocess.Popen(
                ["cmd", "/c", "start", "spotify:"],
                shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            logger.info("Spotify opened.")
            time.sleep(3)
            return "Opening Spotify!"
        except Exception as e:
            logger.error(f"Spotify open error: {e}")
            try:
                import os
                spotify_path = os.path.join(
                    os.environ.get("APPDATA", ""),
                    "Spotify", "Spotify.exe"
                )
                if os.path.exists(spotify_path):
                    subprocess.Popen([spotify_path])
                    time.sleep(3)
                    return "Opening Spotify!"
            except Exception:
                pass
            return "Couldn't open Spotify. Make sure it is installed."

    def play(self, song: str) -> str:
        if not song or not song.strip():
            return "What song should I play on Spotify?"

        song = self._clean_query(song.strip())
        logger.info(f"Playing on Spotify: {song}")

        try:
            self._ensure_spotify_open()

            encoded = urllib.parse.quote(song)
            spotify_uri = f"spotify:search:{encoded}"

            subprocess.Popen(
                ["cmd", "/c", "start", spotify_uri],
                shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            time.sleep(3)
            pyautogui.press("enter")
            time.sleep(0.5)

            logger.info(f"Playing on Spotify: {song}")
            return f"Playing {song} on Spotify!"

        except Exception as e:
            logger.error(f"Spotify play error: {e}")
            return f"Couldn't play {song} on Spotify."

    def pause(self) -> str:
        try:
            self._focus_spotify()
            pyautogui.press("space")
            return "Spotify paused!"
        except Exception:
            return "Couldn't pause Spotify."

    def resume(self) -> str:
        try:
            self._focus_spotify()
            pyautogui.press("space")
            return "Spotify resumed!"
        except Exception:
            return "Couldn't resume Spotify."

    def next_track(self) -> str:
        try:
            self._focus_spotify()
            pyautogui.hotkey("ctrl", "right")
            return "Playing next song!"
        except Exception:
            return "Couldn't skip to next."

    def previous_track(self) -> str:
        try:
            self._focus_spotify()
            pyautogui.hotkey("ctrl", "left")
            return "Playing previous song!"
        except Exception:
            return "Couldn't go to previous."

    def volume_up(self, amount: int = 10) -> str:
        try:
            self._focus_spotify()
            for _ in range(max(1, amount // 10)):
                pyautogui.hotkey("ctrl", "up")
                time.sleep(0.1)
            return "Spotify volume increased!"
        except Exception:
            return "Couldn't increase Spotify volume."

    def volume_down(self, amount: int = 10) -> str:
        try:
            self._focus_spotify()
            for _ in range(max(1, amount // 10)):
                pyautogui.hotkey("ctrl", "down")
                time.sleep(0.1)
            return "Spotify volume decreased!"
        except Exception:
            return "Couldn't decrease Spotify volume."

    def mute(self) -> str:
        try:
            self._focus_spotify()
            for _ in range(10):
                pyautogui.hotkey("ctrl", "down")
                time.sleep(0.05)
            return "Spotify muted!"
        except Exception:
            return "Couldn't mute Spotify."

    def _ensure_spotify_open(self):
        try:
            import psutil
            for proc in psutil.process_iter(["name"]):
                if "spotify" in proc.info["name"].lower():
                    return
        except Exception:
            pass
        subprocess.Popen(
            ["cmd", "/c", "start", "spotify:"],
            shell=False,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        time.sleep(4)

    def _focus_spotify(self):
        try:
            import pygetwindow as gw
            wins = gw.getWindowsWithTitle("Spotify")
            if wins:
                wins[0].activate()
                time.sleep(0.5)
        except Exception:
            pass

    def _clean_query(self, query: str) -> str:
        filler = [
            "on spotify", "in spotify", "spotify mein",
            "play song", "play a song", "play the song",
            "song by", "a song", "please play", "play me",
            "spotify par", "spotify pe", "spotify par play",
            "play on spotify", "play"
        ]
        q = query.lower().strip()
        for f in sorted(filler, key=len, reverse=True):
            if q.startswith(f):
                q = q[len(f):].strip()
            if q.endswith(f):
                q = q[:-len(f)].strip()
        return q if q else query


# ── Singleton ─────────────────────────────────────────────
_spotify = None

def get_spotify() -> Spotify:
    global _spotify
    if _spotify is None:
        _spotify = Spotify()
    return _spotify


if __name__ == "__main__":
    sp = Spotify()
    print(sp.play("Kesariya Arijit Singh"))