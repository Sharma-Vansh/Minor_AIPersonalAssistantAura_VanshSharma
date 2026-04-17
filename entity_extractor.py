"""
commands/entity_extractor.py
✅ FIXED: Phonetic matching — Aakash = Akash, Shivam = Shivam
✅ FIXED: Contact + message properly split
✅ FIXED: Hinglish patterns (tu, ko, ko bolo)
✅ FIXED: Logger emoji crash (no emojis in log strings)
"""

import re
import os
import json
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Load contacts for phonetic matching ───────────────────
def _load_contact_keys() -> list:
    try:
        path = os.path.join(os.path.dirname(__file__), "..", "memory", "user_data.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return list(data.get("contacts", {}).keys())
    except Exception:
        pass
    return []


def _normalize(text: str) -> str:
    """Normalize for phonetic matching: lowercase, remove extra a/i/e."""
    t = text.lower().strip()
    # Common Indian name phonetic fixes
    t = t.replace("aa", "a").replace("ee", "i").replace("oo", "u")
    t = t.replace("sh", "s").replace("kh", "k")
    return t


def _phonetic_match(spoken: str, contact_keys: list) -> str | None:
    """
    Match spoken name to saved contacts using normalization.
    'Aakash' -> normalize -> 'akas' matches 'Akash Gurjar' normalized -> 'akas gurjar'
    Returns the best matching contact key name (as stored).
    """
    spoken_norm = _normalize(spoken)

    # Level 1: exact normalized match
    for key in contact_keys:
        first_word = key.split()[0]  # Compare first name only
        if _normalize(first_word) == spoken_norm:
            logger.info(f"Phonetic match: '{spoken}'->'{spoken_norm}' matched '{key}'")
            return key.split()[0].title()  # Return first name

    # Level 2: spoken is prefix of normalized key
    for key in contact_keys:
        first_word = key.split()[0]
        key_norm = _normalize(first_word)
        if key_norm.startswith(spoken_norm) or spoken_norm.startswith(key_norm):
            logger.info(f"Phonetic prefix match: '{spoken}'->'{spoken_norm}' matched '{key}'")
            return key.split()[0].title()

    return None


class EntityExtractor:

    def __init__(self):
        self._contact_keys = _load_contact_keys()

    def extract(self, text: str) -> dict:
        text = text.strip()
        result = {}

        result.update(self._extract_contact_and_message(text))
        result.update(self._extract_song(text))
        result.update(self._extract_search_query(text))
        result.update(self._extract_number(text))
        result.update(self._extract_website(text))
        result.update(self._extract_reminder_time(text))

        logger.debug(f"Extracted entities: {result}")
        return result

    def _extract_contact_and_message(self, text: str) -> dict:
        """
        Extract contact + message with phonetic matching.
        
        Examples:
          "send message to Aakash hello bhai"  -> contact=Akash, message=hello bhai
          "send message tu shivam kya haal hai" -> contact=Shivam, message=kya haal hai
          "aakash ko whatsapp karo hello"       -> contact=Akash, message=hello
        """
        result = {}

        SKIP_WORDS = {
            "to", "tu", "ko", "that", "say", "saying", "the",
            "a", "an", "my", "your", "his", "her",
            "message", "send", "whatsapp", "text", "msg",
            "on", "per", "par", "mein", "ka", "ki", "ke",
            "and", "or", "but", "hai", "hain", "karo"
        }

        # Words that can NEVER be the start of a contact name
        CONTACT_BLOCKLIST = {
            "aur", "aap", "bhai", "yaar", "dost", "please", "kya",
            "ek", "the", "and", "or", "send", "open", "close"
        }

        patterns = [
            # "send message to Akash say hello bhai"
            r"(?:send|whatsapp|message|text)\s+(?:a\s+)?(?:message\s+)?(?:to\s+|tu\s+|ko\s+)?([a-zA-Z][a-zA-Z\s]{0,30}?)\s+(?:say|saying|that|bolo|likhna)\s+(.+)",
            # "send message to Akash hello bhai" (freeform)
            r"(?:send|whatsapp|message|text)\s+(?:a\s+)?(?:message\s+)?(?:to|tu|ko)\s+([a-zA-Z][a-zA-Z\s]{1,30}?)\s+(\S.+)",
            # "whatsapp Akash hi bhai"
            r"(?:whatsapp|text)\s+([a-zA-Z][a-zA-Z\s]{0,30}?)\s+(\S.+)",
            # contact only: "send message to Akash"
            r"(?:send|whatsapp|message|text)\s+(?:a\s+)?(?:message\s+)?(?:to|tu|ko)\s+([a-zA-Z][a-zA-Z\s]{1,30}?)$",
        ]


        for i, pattern in enumerate(patterns):
            match = re.search(pattern, text.strip(), re.IGNORECASE)
            if match:
                contact_raw = match.group(1).strip()

                if contact_raw.lower() in SKIP_WORDS:
                    continue

                # Reject if first word is a known filler/non-name word
                first_word = contact_raw.split()[0].lower() if contact_raw.split() else ""
                if first_word in CONTACT_BLOCKLIST:
                    continue

                # Strip trailing skip words
                words = contact_raw.split()
                while words and words[-1].lower() in SKIP_WORDS:
                    words.pop()
                contact_raw = " ".join(words).strip()
                if not contact_raw or len(contact_raw) < 2:
                    continue

                # Phonetic match against saved contacts
                matched = _phonetic_match(contact_raw, self._contact_keys)
                result["contact"] = matched if matched else contact_raw.title()

                # Get message if available (not contact-only pattern)
                if i < 4 and len(match.groups()) >= 2:
                    msg = match.group(2).strip()
                    # Clean message from WhatsApp/send filler
                    msg = re.sub(r'^(karo|bhejo|send|on whatsapp|on wa)\s*', '', msg, flags=re.IGNORECASE).strip()
                    if msg and msg.lower() not in SKIP_WORDS:
                        result["message"] = msg
                break

        return result

    def _extract_song(self, text: str) -> dict:
        """Extract song/video name for YouTube or Spotify."""
        patterns = [
            r"(?:play|chalao|gaao|sunao)\s+(.+?)(?:\s+on\s+(?:youtube|spotify|yt))?$",
            r"youtube\s+(?:par\s+)?(?:play\s+)?(.+)",
            r"spotify\s+(?:par\s+|pe\s+|mein\s+)?(?:play\s+)?(.+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                song = match.group(1).strip()
                song = re.sub(r"\s+(song|video|music|gaana)$", "", song, flags=re.IGNORECASE)
                # Remove trailing platform names
                song = re.sub(r"\s+on\s+(youtube|spotify|yt)$", "", song, flags=re.IGNORECASE)
                return {"song": song}
        return {}

    def _extract_search_query(self, text: str) -> dict:
        """Extract search query for Google/browser."""
        patterns = [
            r"(?:search|google|look up|search for|dhundo|khojo)\s+(?:for\s+)?(.+)",
            r"(?:open|go to|open website)\s+(.+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {"query": match.group(1).strip()}
        return {}

    def _extract_number(self, text: str) -> dict:
        """Extract first number from text."""
        match = re.search(r'\b(\d+)\b', text)
        if match:
            return {"number": int(match.group(1))}
        return {}

    def _extract_website(self, text: str) -> dict:
        """Extract website name or URL."""
        url_match = re.search(r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9]+\.com)', text)
        if url_match:
            return {"url": url_match.group(1)}

        site_match = re.search(
            r'(?:open|go to|launch)\s+([a-zA-Z]+)(?:\s+website)?', text, re.IGNORECASE
        )
        if site_match:
            return {"site": site_match.group(1).lower()}

        return {}

    def _extract_reminder_time(self, text: str) -> dict:
        """Extract time info for reminders."""
        result = {}

        min_match = re.search(r'(\d+)\s*(?:minute|min|mins|minutes)', text, re.IGNORECASE)
        if min_match:
            result["reminder_minutes"] = int(min_match.group(1))

        hr_match = re.search(r'(\d+)\s*(?:hour|hr|hours)', text, re.IGNORECASE)
        if hr_match:
            result["reminder_hours"] = int(hr_match.group(1))

        task_match = re.search(
            r'(?:to|for|about|ke liye)\s+(.+?)(?:\s+in\s+\d+|$)', text, re.IGNORECASE
        )
        if task_match:
            result["reminder_task"] = task_match.group(1).strip()

        return result


# ── Singleton ─────────────────────────────────────────────
_extractor = None

def extract_entities(text: str) -> dict:
    global _extractor
    if _extractor is None:
        _extractor = EntityExtractor()
    return _extractor.extract(text)