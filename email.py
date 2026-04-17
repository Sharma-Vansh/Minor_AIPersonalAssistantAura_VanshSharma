"""
automation/email.py
✅ FIXED: Finds Outlook.exe using PowerShell Get-Command (most reliable)
✅ FIXED: Opens Outlook directly without any URI scheme
✅ FIXED: Compose window via command line switch
"""

import os
import subprocess
import urllib.parse
import time
import json
import pyautogui
from utils.logger import get_logger

logger = get_logger(__name__)


def _find_outlook() -> str | None:
    """
    Find Outlook.exe path using PowerShell Get-Command.
    This is the most reliable method on any Windows PC.
    """
    # Method 1: PowerShell Get-Command (works for any Office installation)
    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "(Get-Command OUTLOOK -ErrorAction SilentlyContinue).Source"],
            capture_output=True, text=True, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        path = result.stdout.strip()
        if path and os.path.exists(path):
            logger.info(f"Outlook found via PowerShell: {path}")
            return path
    except Exception as e:
        logger.warning(f"PowerShell Outlook search failed: {e}")

    # Method 2: Check common install paths
    common_paths = [
        r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\OUTLOOK.EXE",
        r"C:\Program Files\Microsoft Office\Office16\OUTLOOK.EXE",
        r"C:\Program Files (x86)\Microsoft Office\Office16\OUTLOOK.EXE",
        r"C:\Program Files\Microsoft Office\root\Office15\OUTLOOK.EXE",
        r"C:\Program Files\Microsoft Office\Office15\OUTLOOK.EXE",
    ]
    for path in common_paths:
        if os.path.exists(path):
            logger.info(f"Outlook found at: {path}")
            return path

    # Method 3: Search registry via PowerShell
    try:
        result = subprocess.run(
            ["powershell", "-Command",
             r"Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\OUTLOOK.EXE' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty '(default)'"],
            capture_output=True, text=True, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        path = result.stdout.strip()
        if path and os.path.exists(path):
            logger.info(f"Outlook found via registry: {path}")
            return path
    except Exception as e:
        logger.warning(f"Registry Outlook search failed: {e}")

    logger.warning("Outlook.exe not found on this PC.")
    return None


class Email:

    def __init__(self):
        self._outlook_path = _find_outlook()
        if self._outlook_path:
            logger.info("Outlook Desktop ready.")
        else:
            logger.warning("Outlook Desktop NOT found.")

    def _launch_outlook(self, args: list = None) -> bool:
        """Launch Outlook with optional command line args."""
        if not self._outlook_path:
            logger.error("Outlook path not found.")
            return False
        try:
            cmd = [self._outlook_path] + (args or [])
            subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except Exception as e:
            logger.error(f"Outlook launch failed: {e}")
            return False

    def open_outlook(self) -> str:
        """Open Microsoft Outlook Desktop."""
        if self._launch_outlook():
            logger.info("Outlook opened.")
            time.sleep(3)
            return "Opening Outlook for you!"
        # Last fallback: use Start-Process
        try:
            subprocess.Popen(
                ["powershell", "-Command", "Start-Process OUTLOOK.EXE"],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            time.sleep(3)
            return "Opening Outlook!"
        except Exception as e:
            logger.error(f"All Outlook open methods failed: {e}")
            return "Could not open Outlook. Please open it manually."

    def check_inbox(self) -> str:
        """Open Outlook inbox."""
        # /select switches to inbox folder
        if self._launch_outlook(["/select", "outlook:inbox"]):
            logger.info("Outlook inbox opened.")
            time.sleep(3)
            return "Opening your Outlook inbox!"
        return self.open_outlook()

    def compose_new(self) -> str:
        """Open new email compose window."""
        # /c IPM.Note opens a new mail compose window directly
        if self._launch_outlook(["/c", "IPM.Note"]):
            logger.info("Outlook compose opened.")
            time.sleep(3)
            return "Opening new email in Outlook!"
        return self.open_outlook()

    def send_email(self, to: str, subject: str, body: str) -> str:
        """
        Send email via Outlook Desktop.
        Uses /c IPM.Note /m switch to pre-fill recipient.
        """
        try:
            recipient = self._resolve_email(to)

            # /c IPM.Note /m "to&subject=X&body=Y" is the correct Outlook CLI syntax
            mailto_arg = f"{recipient}&subject={subject}&body={body}"

            if self._launch_outlook(["/c", "IPM.Note", "/m", mailto_arg]):
                time.sleep(4)
                # Alt+S to send
                pyautogui.hotkey("alt", "s")
                time.sleep(1)
                logger.info(f"Email sent to {recipient}")
                return f"Done! Email sent to {to} via Outlook!"

            return "Couldn't open Outlook to send the email."

        except Exception as e:
            logger.error(f"Email send error: {e}")
            return f"Sorry, couldn't send the email. Error: {str(e)}"

    def _resolve_email(self, name_or_email: str) -> str:
        if "@" in name_or_email:
            return name_or_email
        try:
            path = os.path.join(
                os.path.dirname(__file__), "..", "memory", "user_data.json"
            )
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                emails = data.get("emails", {})
                search = name_or_email.lower().strip()
                for key, email in emails.items():
                    if key.lower().strip().startswith(search) or search in key.lower():
                        return email
        except Exception as e:
            logger.warning(f"Email resolve error: {e}")
        return name_or_email


# ── Singleton ─────────────────────────────────────────────
_email_instance = None

def get_email() -> Email:
    global _email_instance
    if _email_instance is None:
        _email_instance = Email()
    return _email_instance


if __name__ == "__main__":
    e = Email()
    print(e.check_inbox())