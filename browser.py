"""
automation/browser.py — Web browsing and Google search automation
Aura can search Google, open websites, and control Chrome.
"""

import webbrowser
import urllib.parse
import subprocess
import time
from utils.logger import get_logger

logger = get_logger(__name__)


class Browser:

    def __init__(self):
        # Try to find Chrome path automatically
        self.chrome_path = self._find_chrome()

    def _find_chrome(self) -> str | None:
        """Find Google Chrome installation path on Windows."""
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            rf"C:\Users\{__import__('os').getlogin()}\AppData\Local\Google\Chrome\Application\chrome.exe",
        ]
        import os
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Chrome found at: {path}")
                return path
        logger.warning("Chrome not found. Using default browser.")
        return None

    # ── Search ────────────────────────────────────────────

    def google_search(self, query: str) -> str:
        """
        Search Google for a query and open results in browser.
        Example: google_search("best Python projects for beginners")
        """
        if not query or not query.strip():
            return "What should I search for?"

        query = query.strip()
        encoded = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded}"

        try:
            webbrowser.open(url)
            logger.info(f"Google search: {query}")
            return f"Searching Google for {query}."
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return f"Couldn't open Google search. Error: {e}"

    def search_youtube(self, query: str) -> str:
        """Search YouTube directly from browser."""
        encoded = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        webbrowser.open(url)
        return f"Searching YouTube for {query}."

    def search_maps(self, location: str) -> str:
        """Open Google Maps for a location."""
        encoded = urllib.parse.quote(location)
        url = f"https://www.google.com/maps/search/{encoded}"
        webbrowser.open(url)
        return f"Opening Google Maps for {location}."

    def search_wikipedia(self, topic: str) -> str:
        """Open Wikipedia page for a topic."""
        encoded = urllib.parse.quote(topic.replace(" ", "_"))
        url = f"https://en.wikipedia.org/wiki/{encoded}"
        webbrowser.open(url)
        return f"Opening Wikipedia for {topic}."

    # ── Open Websites ─────────────────────────────────────

    def open_website(self, url: str) -> str:
        """
        Open any URL directly.
        Automatically adds https:// if missing.
        """
        if not url.startswith("http"):
            url = "https://" + url

        try:
            webbrowser.open(url)
            logger.info(f"Opened URL: {url}")
            return f"Opening {url}."
        except Exception as e:
            logger.error(f"Open URL error: {e}")
            return f"Couldn't open {url}."

    def open_common_site(self, site_name: str) -> str:
        """
        Open popular websites by name.
        Example: open_common_site("instagram") → opens Instagram
        """
        sites = {
            # Social Media
            "instagram":  "https://www.instagram.com",
            "facebook":   "https://www.facebook.com",
            "twitter":    "https://www.twitter.com",
            "linkedin":   "https://www.linkedin.com",
            "reddit":     "https://www.reddit.com",
            "snapchat":   "https://web.snapchat.com",
            # Entertainment
            "youtube":    "https://www.youtube.com",
            "netflix":    "https://www.netflix.com",
            "hotstar":    "https://www.hotstar.com",
            "spotify":    "https://open.spotify.com",
            "prime":      "https://www.primevideo.com",
            # Work & Study
            "gmail":      "https://mail.google.com",
            "google":     "https://www.google.com",
            "drive":      "https://drive.google.com",
            "docs":       "https://docs.google.com",
            "sheets":     "https://sheets.google.com",
            "meet":       "https://meet.google.com",
            "zoom":       "https://zoom.us",
            "github":     "https://www.github.com",
            "stackoverflow": "https://stackoverflow.com",
            # News
            "bbc":        "https://www.bbc.com",
            "ndtv":       "https://www.ndtv.com",
            "times of india": "https://timesofindia.indiatimes.com",
            # Shopping
            "amazon":     "https://www.amazon.in",
            "flipkart":   "https://www.flipkart.com",
            "swiggy":     "https://www.swiggy.com",
            "zomato":     "https://www.zomato.com",
        }

        key = site_name.lower().strip()
        if key in sites:
            return self.open_website(sites[key])
        else:
            # Try adding .com and opening
            return self.open_website(f"https://www.{key}.com")

    # ── Chrome Controls ───────────────────────────────────

    def open_new_tab(self, url: str = "https://www.google.com") -> str:
        """Open a new Chrome tab."""
        try:
            import pyautogui
            pyautogui.hotkey("ctrl", "t")
            time.sleep(0.5)
            if url != "https://www.google.com":
                webbrowser.open(url)
            return "Opened a new tab!"
        except Exception as e:
            logger.error(f"New tab error: {e}")
            return "Couldn't open a new tab."

    def close_tab(self) -> str:
        """Close the current browser tab."""
        try:
            import pyautogui
            pyautogui.hotkey("ctrl", "w")
            return "Tab closed!"
        except Exception as e:
            return "Couldn't close the tab."

    def go_back(self) -> str:
        """Go back in browser history."""
        try:
            import pyautogui
            pyautogui.hotkey("alt", "left")
            return "Going back!"
        except Exception as e:
            return "Couldn't go back."

    def go_forward(self) -> str:
        """Go forward in browser history."""
        try:
            import pyautogui
            pyautogui.hotkey("alt", "right")
            return "Going forward!"
        except Exception as e:
            return "Couldn't go forward."

    def refresh_page(self) -> str:
        """Refresh the current page."""
        try:
            import pyautogui
            pyautogui.hotkey("ctrl", "r")
            return "Page refreshed!"
        except Exception as e:
            return "Couldn't refresh the page."

    def zoom_in(self) -> str:
        """Zoom in on the browser page."""
        try:
            import pyautogui
            pyautogui.hotkey("ctrl", "=")
            return "Zoomed in!"
        except Exception as e:
            return "Couldn't zoom in."

    def zoom_out(self) -> str:
        """Zoom out on the browser page."""
        try:
            import pyautogui
            pyautogui.hotkey("ctrl", "-")
            return "Zoomed out!"
        except Exception as e:
            return "Couldn't zoom out."

    def scroll_down(self, times: int = 3) -> str:
        """Scroll down the page."""
        try:
            import pyautogui
            pyautogui.scroll(-300 * times)
            return "Scrolling down!"
        except Exception as e:
            return "Couldn't scroll."

    def scroll_up(self, times: int = 3) -> str:
        """Scroll up the page."""
        try:
            import pyautogui
            pyautogui.scroll(300 * times)
            return "Scrolling up!"
        except Exception as e:
            return "Couldn't scroll up."

    def fullscreen_browser(self) -> str:
        """Toggle browser fullscreen with F11."""
        try:
            import pyautogui
            pyautogui.press("f11")
            return "Toggled fullscreen!"
        except Exception as e:
            return "Couldn't toggle fullscreen."


# ── Singleton ─────────────────────────────────────────────
_browser = None

def get_browser():
    global _browser
    if _browser is None:
        _browser = Browser()
    return _browser

def google_search(query: str) -> str:
    return get_browser().google_search(query)

def open_website(url: str) -> str:
    return get_browser().open_website(url)


# ── Quick test ────────────────────────────────────────────
if __name__ == "__main__":
    b = Browser()
    print(b.google_search("Aura AI assistant Python project"))
    time.sleep(3)
    print(b.open_common_site("github"))