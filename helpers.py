"""
utils/helpers.py — General utility functions used across Aura
"""

import re
import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


def clean_text(text: str) -> str:
    """Remove extra spaces, newlines, and special chars from text."""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text


def truncate(text: str, max_chars: int = 300) -> str:
    """Truncate text to max_chars for TTS — keeps responses short."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(' ', 1)[0] + "..."


def get_greeting() -> str:
    """Returns Good Morning / Afternoon / Evening based on time."""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 21:
        return "Good evening"
    else:
        return "Good night"


def get_current_time() -> str:
    """Returns current time as a readable string e.g. '3:45 PM'"""
    return datetime.datetime.now().strftime("%I:%M %p")


def get_current_date() -> str:
    """Returns current date e.g. 'Sunday, March 29, 2026'"""
    return datetime.datetime.now().strftime("%A, %B %d, %Y")


def contains_any(text: str, keywords: list) -> bool:
    """Check if text contains any keyword from a list (case-insensitive)."""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


def extract_number(text: str) -> int | None:
    """Extract the first number found in a string. E.g. 'set timer 5 minutes' → 5"""
    match = re.search(r'\d+', text)
    return int(match.group()) if match else None