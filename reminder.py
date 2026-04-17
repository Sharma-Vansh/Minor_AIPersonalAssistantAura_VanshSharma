"""
automation/reminder.py — Set timers, alarms, and reminders
Aura will speak and show a notification when the time is up.
"""

import threading
import time
from utils.logger import get_logger

logger = get_logger(__name__)


class ReminderManager:
    def __init__(self):
        self.active_reminders = []

    def set_reminder(self, task: str, minutes: int) -> str:
        """
        Set a reminder that fires after 'minutes' minutes.
        Runs in background thread — doesn't block Aura.
        """
        if minutes <= 0:
            return "Please give a valid time for the reminder."

        seconds = minutes * 60
        logger.info(f"Reminder set: '{task}' in {minutes} minutes.")

        def _fire():
            time.sleep(seconds)
            self._notify(task, minutes)

        thread = threading.Thread(target=_fire, daemon=True)
        thread.start()
        self.active_reminders.append({"task": task, "minutes": minutes})

        if minutes == 1:
            return f"Got it! I'll remind you to {task} in 1 minute."
        return f"Got it! I'll remind you to {task} in {minutes} minutes."

    def _notify(self, task: str, minutes: int):
        """Fire the reminder — speak it and show Windows notification."""
        message = f"Reminder! {task}"
        logger.info(f"Reminder fired: {message}")

        # Speak the reminder
        try:
            from voice.text_to_speech import speak
            speak(f"Hey! Reminder alert. It's time to {task}.")
        except Exception as e:
            logger.error(f"Reminder TTS error: {e}")

        # Show Windows toast notification
        try:
            from plyer import notification
            notification.notify(
                title="⏰ Aura Reminder",
                message=task,
                app_name="Aura",
                timeout=10
            )
        except Exception as e:
            logger.warning(f"Desktop notification failed: {e}")
            print(f"\n⏰ REMINDER: {task}\n")

    def set_timer(self, seconds: int) -> str:
        """Quick countdown timer."""
        def _beep():
            time.sleep(seconds)
            try:
                from voice.text_to_speech import speak
                speak("Timer is up!")
            except Exception:
                print("\n⏰ Timer is up!\n")

        thread = threading.Thread(target=_beep, daemon=True)
        thread.start()

        if seconds < 60:
            return f"Timer set for {seconds} seconds."
        return f"Timer set for {seconds // 60} minutes."


# ── Singleton ─────────────────────────────────────────────
_manager = None

def set_reminder(task: str, minutes: int) -> str:
    global _manager
    if _manager is None:
        _manager = ReminderManager()
    return _manager.set_reminder(task, minutes)


# ── Quick test ────────────────────────────────────────────
if __name__ == "__main__":
    print(set_reminder("drink water", 1))
    print("Reminder set! Waiting...")
    time.sleep(65)