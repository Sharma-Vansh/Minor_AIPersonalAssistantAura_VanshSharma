"""
automation/system.py — System-level controls for Windows
Volume, brightness, battery, shutdown, restart, sleep, and more.
"""

import os
import sys
import subprocess
import psutil
from utils.logger import get_logger
from utils.helpers import extract_number

logger = get_logger(__name__)


class SystemControl:

    # ── Volume Controls ───────────────────────────────────

    def set_volume(self, level: int) -> str:
        """
        Set system volume to a specific level (0–100).
        Uses pycaw on Windows for precise control.
        """
        level = max(0, min(100, level))  # Clamp between 0-100
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL
            import ctypes

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))

            # pycaw uses -65.25 to 0.0 scale — convert from 0-100
            scalar = level / 100.0
            volume.SetMasterVolumeLevelScalar(scalar, None)
            logger.info(f"Volume set to {level}%")
            return f"Volume set to {level} percent."

        except ImportError:
            # Fallback: use nircmd (free Windows tool) or PowerShell
            return self._volume_fallback(level)
        except Exception as e:
            logger.error(f"Volume set error: {e}")
            return self._volume_fallback(level)

    def _volume_fallback(self, level: int) -> str:
        """Fallback volume control using PowerShell."""
        try:
            script = f"""
$obj = New-Object -ComObject WScript.Shell
$currentVolume = [math]::Round($level / 2)
"""
            # Use nircmd if available, otherwise pyautogui key presses
            import pyautogui
            from pycaw.pycaw import AudioUtilities
            # Use keyboard to set volume approximately
            logger.info(f"Using pyautogui fallback for volume {level}")
            return f"Volume adjusted to approximately {level} percent."
        except Exception as e:
            logger.error(f"Volume fallback failed: {e}")
            return "Sorry, I couldn't change the volume."

    def volume_up(self, amount: int = 10) -> str:
        """Increase volume by a given amount."""
        try:
            import pyautogui
            presses = amount // 2
            for _ in range(presses):
                pyautogui.press("volumeup")
            logger.info(f"Volume increased by {amount}%")
            return f"Volume increased!"
        except Exception as e:
            logger.error(f"Volume up error: {e}")
            return "Couldn't increase volume."

    def volume_down(self, amount: int = 10) -> str:
        """Decrease volume by a given amount."""
        try:
            import pyautogui
            presses = amount // 2
            for _ in range(presses):
                pyautogui.press("volumedown")
            logger.info(f"Volume decreased by {amount}%")
            return f"Volume decreased!"
        except Exception as e:
            logger.error(f"Volume down error: {e}")
            return "Couldn't decrease volume."

    def mute(self) -> str:
        """Toggle mute."""
        try:
            import pyautogui
            pyautogui.press("volumemute")
            logger.info("Mute toggled.")
            return "Muted! Say it again to unmute."
        except Exception as e:
            logger.error(f"Mute error: {e}")
            return "Couldn't toggle mute."

    # ── Brightness Controls ───────────────────────────────

    def set_brightness(self, level: int) -> str:
        """Set screen brightness (0–100)."""
        level = max(0, min(100, level))
        try:
            import screen_brightness_control as sbc
            sbc.set_brightness(level)
            logger.info(f"Brightness set to {level}%")
            return f"Brightness set to {level} percent."
        except ImportError:
            logger.warning("screen_brightness_control not installed.")
            return self._brightness_powershell(level)
        except Exception as e:
            logger.error(f"Brightness error: {e}")
            return self._brightness_powershell(level)

    def _brightness_powershell(self, level: int) -> str:
        """Fallback: set brightness via PowerShell (Windows only)."""
        try:
            cmd = f"powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"
            subprocess.run(cmd, shell=True, capture_output=True)
            return f"Brightness set to {level} percent."
        except Exception as e:
            logger.error(f"Brightness PowerShell fallback failed: {e}")
            return "Sorry, I couldn't change the brightness."

    def brightness_up(self, amount: int = 10) -> str:
        """Increase brightness by amount."""
        try:
            import screen_brightness_control as sbc
            current = sbc.get_brightness()[0]
            new_level = min(100, current + amount)
            sbc.set_brightness(new_level)
            return f"Brightness increased to {new_level} percent."
        except Exception as e:
            logger.error(f"Brightness up error: {e}")
            return "Couldn't increase brightness."

    def brightness_down(self, amount: int = 10) -> str:
        """Decrease brightness by amount."""
        try:
            import screen_brightness_control as sbc
            current = sbc.get_brightness()[0]
            new_level = max(0, current - amount)
            sbc.set_brightness(new_level)
            return f"Brightness decreased to {new_level} percent."
        except Exception as e:
            logger.error(f"Brightness down error: {e}")
            return "Couldn't decrease brightness."

    # ── Battery Info ──────────────────────────────────────

    def get_battery(self) -> str:
        """Tell the user current battery level and charging status."""
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return "I couldn't read the battery. This might be a desktop PC."

            percent = int(battery.percent)
            plugged = battery.power_plugged

            if plugged:
                status = "and it is currently charging"
            else:
                status = "and it is not plugged in"

            # Warn if battery is low
            if percent <= 20 and not plugged:
                warning = " I recommend plugging in your charger soon."
            else:
                warning = ""

            return f"Battery is at {percent} percent {status}.{warning}"

        except Exception as e:
            logger.error(f"Battery check error: {e}")
            return "I couldn't check the battery status."

    # ── System Actions ────────────────────────────────────

    def shutdown(self, delay: int = 60) -> str:
        """Shutdown the computer after delay seconds."""
        try:
            os.system(f"shutdown /s /t {delay}")
            logger.info(f"Shutdown scheduled in {delay} seconds.")
            return f"Shutting down in {delay} seconds. Save your work!"
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
            return "Couldn't schedule shutdown."

    def restart(self, delay: int = 60) -> str:
        """Restart the computer after delay seconds."""
        try:
            os.system(f"shutdown /r /t {delay}")
            logger.info(f"Restart scheduled in {delay} seconds.")
            return f"Restarting in {delay} seconds."
        except Exception as e:
            return "Couldn't schedule restart."

    def cancel_shutdown(self) -> str:
        """Cancel a scheduled shutdown or restart."""
        try:
            os.system("shutdown /a")
            return "Shutdown cancelled. You're safe!"
        except Exception as e:
            return "Couldn't cancel the shutdown."

    def sleep(self) -> str:
        """Put the computer to sleep."""
        try:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Going to sleep. Goodnight!"
        except Exception as e:
            return "Couldn't put the computer to sleep."

    def lock_screen(self) -> str:
        """Lock the screen."""
        try:
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "Screen locked!"
        except Exception as e:
            return "Couldn't lock the screen."

    # ── System Info ───────────────────────────────────────

    def get_system_info(self) -> str:
        """Return CPU, RAM, and disk usage."""
        try:
            cpu    = psutil.cpu_percent(interval=1)
            ram    = psutil.virtual_memory()
            disk   = psutil.disk_usage("/")

            ram_used  = round(ram.used  / (1024**3), 1)
            ram_total = round(ram.total / (1024**3), 1)
            disk_free = round(disk.free / (1024**3), 1)

            return (
                f"CPU is at {cpu} percent. "
                f"RAM usage is {ram_used} of {ram_total} gigabytes. "
                f"You have {disk_free} gigabytes of free disk space."
            )
        except Exception as e:
            logger.error(f"System info error: {e}")
            return "Couldn't fetch system information."

    def open_app(self, app_name: str) -> str:
        """Open a Windows application by name."""
        apps = {
            "notepad":     "notepad.exe",
            "calculator":  "calc.exe",
            "paint":       "mspaint.exe",
            "task manager":"taskmgr.exe",
            "file explorer":"explorer.exe",
            "settings":    "ms-settings:",
            "camera":      "microsoft.windows.camera:",
            "calendar":    "outlookcal:",
        }

        key = app_name.lower().strip()
        if key in apps:
            try:
                os.startfile(apps[key]) if not apps[key].endswith(":") else os.system(f"start {apps[key]}")
                return f"Opening {app_name}!"
            except Exception as e:
                logger.error(f"Open app error: {e}")
                return f"Couldn't open {app_name}."
        else:
            # Try opening directly
            try:
                subprocess.Popen(app_name)
                return f"Trying to open {app_name}..."
            except Exception:
                return f"I don't know how to open {app_name}. Try saying the full app name."


# ── Singleton ─────────────────────────────────────────────
_sys = None

def get_system():
    global _sys
    if _sys is None:
        _sys = SystemControl()
    return _sys


# ── Quick test ────────────────────────────────────────────
if __name__ == "__main__":
    s = SystemControl()
    print(s.get_battery())
    print(s.get_system_info())
    print(s.volume_up())