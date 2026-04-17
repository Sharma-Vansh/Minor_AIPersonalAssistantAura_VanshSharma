import os
import psutil
import webbrowser
from utils.logger import get_logger

logger = get_logger(__name__)

class AppController:
    """Handles Opening and Closing both PC Applications and Websites."""
    
    def __init__(self):
        # Common PC apps mapped to their Windows executable commands
        self.app_map = {
            "excel": "excel",
            "word": "winword",
            "powerpoint": "powerpnt",
            "notepad": "notepad",
            "calculator": "calc",
            "paint": "mspaint",
            "mspaint": "mspaint",
            "chrome": "chrome",
            "edge": "msedge",
            "firefox": "firefox",
            "vscode": "code",
            "code": "code",
            "spotify": "spotify",
            "vlc": "vlc",
            "file explorer": "explorer",
            "explorer": "explorer",
            "task manager": "taskmgr",
            "settings": "ms-settings:",
            "whatsapp": "whatsapp:",
            "camera": "microsoft.windows.camera:",
            "clock": "ms-clock:",
            "maps": "bingmaps:",
            "store": "ms-windows-store:"
        }
        
        # Common website URLs
        self.site_map = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "facebook": "https://www.facebook.com",
            "instagram": "https://www.instagram.com",
            "github": "https://www.github.com",
            "chatgpt": "https://chatgpt.com",
            "claude": "https://claude.ai",
            "gmail": "https://mail.google.com",
            "whatsapp web": "https://web.whatsapp.com"
        }

    def open_app(self, name: str) -> str:
        name = name.lower().strip()
        
        # 1. Check standard Websites
        for site_key, url in self.site_map.items():
            if site_key in name:
                logger.info(f"Opening site: {url}")
                webbrowser.open(url)
                return f"Opening {site_key.title()}."
                
        # 2. Handle specific ".com" queries
        if "." in name and " " not in name:
            url = name if name.startswith("http") else f"https://{name}"
            webbrowser.open(url)
            return f"Opening link {name}."

        # 3. Check PC Apps
        app_cmd = None
        found_app = name.title()
        for app_key, cmd in self.app_map.items():
            if app_key in name:
                app_cmd = cmd
                found_app = app_key.title()
                break
                
        if app_cmd:
            logger.info(f"Opening PC app: {app_cmd}")
            os.system(f"start {app_cmd}")
            return f"Opening {found_app}."
            
        # 4. Fallback: try to run the naked command
        import subprocess
        logger.info(f"Attempting generic start: {name}")
        try:
            clean_name = name.replace(" ", "")
            subprocess.Popen(
                ["cmd", "/c", "start", clean_name],
                shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return f"Trying to open {name}."
        except Exception:
            return f"Sorry, I couldn't find an app or website named {name}."

    def close_app(self, name: str) -> str:
        name = name.lower().strip()
        target_process = None
        found_name = name.title()
        
        # Process lookup table
        process_map = {
            "excel": "excel.exe",
            "word": "winword.exe",
            "powerpoint": "powerpnt.exe",
            "notepad": "notepad.exe",
            "calculator": "calculatorapp.exe",
            "chrome": "chrome.exe",
            "edge": "msedge.exe",
            "vscode": "code.exe",
            "code": "code.exe",
            "spotify": "spotify.exe",
            "whatsapp": "whatsapp.exe",
            # If they ask to close youtube, close the browser (Chrome default)
            "youtube": "chrome.exe", 
            "google": "chrome.exe",
            "browser": "chrome.exe"
        }
        
        for key, proc in process_map.items():
            if key in name:
                target_process = proc
                found_name = key.title()
                break
                
        if not target_process:
            # Fallback: guess the .exe name
            target_process = name.replace(" ", "") + ".exe"

        closed_any = False
        try:
            # Iterate through all running processes
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and proc.info['name'].lower() == target_process:
                    proc.terminate()
                    closed_any = True
        except Exception as e:
            logger.error(f"Error terminating {target_process}: {e}")
            return f"I encountered an error trying to close {found_name}."
            
        if closed_any:
            return f"Closed {found_name}."
        else:
            return f"I couldn't find {found_name} running on your PC."
