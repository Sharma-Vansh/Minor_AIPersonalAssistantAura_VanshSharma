"""
memory/memory_manager.py — Aura's brain memory
Saves chat history and user preferences to JSON files
so Aura remembers context between conversations.
"""

import json
import os
from datetime import datetime
from utils.logger import get_logger
from config import CHAT_HISTORY_FILE, USER_DATA_FILE, MAX_HISTORY_TURNS

logger = get_logger(__name__)


class MemoryManager:
    def __init__(self):
        os.makedirs("memory", exist_ok=True)
        self._init_files()

    def _init_files(self):
        """Create JSON files if they don't exist yet."""
        if not os.path.exists(CHAT_HISTORY_FILE):
            self._write(CHAT_HISTORY_FILE, {"history": []})

        if not os.path.exists(USER_DATA_FILE):
            self._write(USER_DATA_FILE, {
                "name": "",
                "city": "",
                "contacts": {},
                "preferences": {
                    "language": "en-IN",
                    "voice_speed": 175,
                    "theme": "dark"
                }
            })

    # ── Read / Write helpers ──────────────────────────────

    def _read(self, filepath: str) -> dict:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Memory read error ({filepath}): {e}")
            return {}

    def _write(self, filepath: str, data: dict):
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Memory write error ({filepath}): {e}")

    # ── Chat History ──────────────────────────────────────

    def save_turn(self, user_text: str, aura_response: str):
        """Save one conversation turn to chat history."""
        data = self._read(CHAT_HISTORY_FILE)
        history = data.get("history", [])

        history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": user_text,
            "aura": aura_response
        })

        # Keep only last N turns to prevent file from growing forever
        if len(history) > MAX_HISTORY_TURNS:
            history = history[-MAX_HISTORY_TURNS:]

        data["history"] = history
        self._write(CHAT_HISTORY_FILE, data)

    def get_history(self, last_n: int = 10) -> list:
        """Return last N conversation turns as a list of dicts."""
        data = self._read(CHAT_HISTORY_FILE)
        history = data.get("history", [])
        return history[-last_n:]

    def get_history_for_groq(self, last_n: int = 6) -> list:
        """
        Return history formatted for Groq API messages list.
        Used to give the AI context of previous turns.
        """
        turns = self.get_history(last_n)
        messages = []
        for turn in turns:
            messages.append({"role": "user",      "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["aura"]})
        return messages

    def clear_history(self):
        """Wipe all chat history."""
        self._write(CHAT_HISTORY_FILE, {"history": []})
        logger.info("Chat history cleared.")

    # ── User Preferences ──────────────────────────────────

    def get_user_data(self) -> dict:
        return self._read(USER_DATA_FILE)

    def set_preference(self, key: str, value):
        """Save a user preference. key = "theme", "language", etc."""
        data = self._read(USER_DATA_FILE)
        if "preferences" not in data:
            data["preferences"] = {}
        data["preferences"][key] = value
        self._write(USER_DATA_FILE, data)
        logger.info(f"Preference saved: {key} = {value}")

    def get_preference(self, key: str, default=None):
        data = self._read(USER_DATA_FILE)
        return data.get("preferences", {}).get(key, default)

    # ── Contacts ──────────────────────────────────────────

    def add_contact(self, name: str, number: str):
        data = self._read(USER_DATA_FILE)
        if "contacts" not in data:
            data["contacts"] = {}
        data["contacts"][name.lower()] = number
        self._write(USER_DATA_FILE, data)

    def get_contact(self, name: str) -> str | None:
        data = self._read(USER_DATA_FILE)
        return data.get("contacts", {}).get(name.lower())

    def get_all_contacts(self) -> dict:
        data = self._read(USER_DATA_FILE)
        return data.get("contacts", {})


# ── Singleton ─────────────────────────────────────────────
_memory = None

def get_memory() -> MemoryManager:
    global _memory
    if _memory is None:
        _memory = MemoryManager()
    return _memory


# ── Quick test ────────────────────────────────────────────
if __name__ == "__main__":
    m = MemoryManager()
    m.save_turn("What is the weather?", "It is sunny and 32 degrees in Delhi.")
    m.save_turn("Play Kesariya", "Playing Kesariya on YouTube!")
    print("Last 2 turns:", m.get_history(2))
    m.add_contact("Rahul", "+919876543210")
    print("Contacts:", m.get_all_contacts())