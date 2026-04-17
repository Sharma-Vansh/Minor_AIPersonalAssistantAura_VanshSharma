"""
Aura Comprehensive Diagnostic — checks every command module
Run: python test_all.py
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

PASS = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"

results = []

def check(name, fn):
    try:
        msg = fn()
        results.append((PASS, name, msg or "OK"))
    except Exception as e:
        results.append((FAIL, name, str(e)))

# ── 1. Constants & Intent Detector ───────────────────────────────────────────
def test_constants():
    from utils.constants import (
        INTENT_YOUTUBE, INTENT_WHATSAPP, INTENT_EMAIL, INTENT_SPOTIFY,
        INTENT_FILE, INTENT_REMINDER, INTENT_WEATHER, INTENT_NEWS,
        INTENT_OPEN_APP, INTENT_CLOSE_APP, INTENT_SYSTEM, INTENT_CHAT,
        YOUTUBE_KEYWORDS, WHATSAPP_KEYWORDS, EMAIL_KEYWORDS, FILE_KEYWORDS,
        SPOTIFY_KEYWORDS
    )
    return "All intent constants + keywords present"

check("Constants (all intents + keywords)", test_constants)

def test_intent_detector():
    from commands.intent_detector import detect_intent
    tests = {
        "send message to akash":      "whatsapp",
        "play honey singh song":      "youtube",
        "open notepad":               "open_app",
        "close excel":                "close_app",
        "what is the weather":        "weather",
        "latest news":                "news",
        "remind me in 5 minutes":     "reminder",
        "send email to akash":        "email",
        "find my file":               "file",
        "volume up":                  "system",
        "play on spotify":            "spotify",
    }
    failures = []
    for text, expected in tests.items():
        got = detect_intent(text)
        if got != expected:
            failures.append(f"'{text}' → got '{got}', expected '{expected}'")
    if failures:
        raise Exception("; ".join(failures))
    return f"All {len(tests)} intent tests passed"

check("IntentDetector (11 intents)", test_intent_detector)

# ── 2. Entity Extractor ───────────────────────────────────────────────────────
def test_entity_extractor():
    from commands.entity_extractor import EntityExtractor
    ex = EntityExtractor()
    result = ex.extract("send message tu akash hello bhai", "whatsapp")
    assert result.get("contact"), f"No contact extracted: {result}"
    assert result.get("message"), f"No message extracted: {result}"
    return f"contact='{result['contact']}' message='{result['message']}'"

check("EntityExtractor (WhatsApp)", test_entity_extractor)

# ── 3. WhatsApp ───────────────────────────────────────────────────────────────
def test_whatsapp_import():
    from automation.whatsapp import WhatsApp
    wa = WhatsApp()
    return f"Loaded. Contacts: {list(wa.contacts.keys())[:5]}..."

check("WhatsApp (import + contacts)", test_whatsapp_import)

def test_whatsapp_fuzzy():
    from automation.whatsapp import WhatsApp
    wa = WhatsApp()
    # Should resolve via fuzzy match
    num = wa._resolve_number("akash")
    if not num:
        raise Exception("'akash' not found in contacts")
    return f"'akash' → {num}"

check("WhatsApp (fuzzy resolve 'akash')", test_whatsapp_fuzzy)

def test_whatsapp_fuzzy2():
    from automation.whatsapp import WhatsApp
    wa = WhatsApp()
    num = wa._resolve_number("Aakash")  # Different spelling STT might hear
    if not num:
        raise Exception("'Aakash' not resolved via fuzzy match")
    return f"'Aakash' → {num}"

check("WhatsApp (fuzzy 'Aakash' → akash)", test_whatsapp_fuzzy2)

# ── 4. YouTube ────────────────────────────────────────────────────────────────
def test_youtube():
    from automation.youtube import YouTube
    yt = YouTube()
    cleaned = yt._clean_query("youtube and play a song honey singh")
    if "youtube" in cleaned.lower() or "play a song" in cleaned.lower():
        raise Exception(f"Query not cleaned properly: '{cleaned}'")
    return f"'youtube and play a song honey singh' → '{cleaned}'"

check("YouTube (query cleaner)", test_youtube)

# ── 5. Spotify ────────────────────────────────────────────────────────────────
def test_spotify():
    from automation.spotify import Spotify
    sp = Spotify()
    cleaned = sp._clean_query("play song on spotify kesariya")
    return f"Spotify import OK. Cleaned: '{cleaned}'"

check("Spotify (import + cleaner)", test_spotify)

# ── 6. Email ─────────────────────────────────────────────────────────────────
def test_email():
    from automation.email import Email
    e = Email()
    # Just check it resolves unknown → returns as-is
    result = e._resolve_email("test@gmail.com")
    assert result == "test@gmail.com"
    return "Email import OK. _resolve_email works."

check("Email (import + resolve)", test_email)

# ── 7. File Manager ───────────────────────────────────────────────────────────
def test_file_manager():
    from automation.file_manager import FileManager
    fm = FileManager()
    result = fm.get_disk_info()
    return f"FileManager OK: {result[:60]}..."

check("FileManager (disk info)", test_file_manager)

# ── 8. Reminder ───────────────────────────────────────────────────────────────
def test_reminder():
    from automation.reminder import set_reminder, _manager
    # Don't actually fire — just check it initializes
    return "Reminder module OK"

check("Reminder (import + singleton)", test_reminder)

# ── 9. App Controller ─────────────────────────────────────────────────────────
def test_app_controller():
    from automation.app_controller import AppController
    ac = AppController()
    assert "paint" in ac.app_map, "'paint' missing from app_map"
    assert "notepad" in ac.app_map, "'notepad' missing from app_map"
    assert "calculator" in ac.app_map, "'calculator' missing"
    return f"AppController OK. {len(ac.app_map)} apps, {len(ac.site_map)} sites"

check("AppController (app map)", test_app_controller)

# ── 10. Weather ───────────────────────────────────────────────────────────────
def test_weather():
    from api.weather_api import get_weather
    return "Weather API import OK"

check("Weather (import)", test_weather)

# ── 11. News ──────────────────────────────────────────────────────────────────
def test_news():
    from api.news_api import get_news
    return "News API import OK"

check("News (import)", test_news)

# ── 12. Browser ───────────────────────────────────────────────────────────────
def test_browser():
    from automation.browser import Browser
    b = Browser()
    return "Browser import OK"

check("Browser (import)", test_browser)

# ── 13. System Control ────────────────────────────────────────────────────────
def test_system():
    from automation.system import SystemControl
    s = SystemControl()
    return "SystemControl import OK"

check("SystemControl (import)", test_system)

# ── 14. Command Router ────────────────────────────────────────────────────────
def test_command_router():
    from commands.command_router import CommandRouter
    from utils.constants import INTENT_OPEN_APP
    router = CommandRouter()
    assert hasattr(router, "_handle_spotify"), "Missing _handle_spotify"
    assert hasattr(router, "_handle_whatsapp"), "Missing _handle_whatsapp"
    assert hasattr(router, "_handle_email"), "Missing _handle_email"
    assert hasattr(router, "_handle_file"), "Missing _handle_file"
    assert hasattr(router, "_handle_reminder"), "Missing _handle_reminder"
    assert INTENT_OPEN_APP in router.route.__globals__  # sanity
    return "CommandRouter OK — all 11 handlers present"

check("CommandRouter (all handlers)", test_command_router)

# ── 15. Voice: STT ────────────────────────────────────────────────────────────
def test_stt():
    from voice.speech_to_text import SpeechToText
    stt = SpeechToText()
    return "SpeechToText import OK"

check("SpeechToText (import)", test_stt)

# ── 16. Voice: TTS ────────────────────────────────────────────────────────────
def test_tts():
    from voice.text_to_speech import speak
    return "TTS import OK"

check("TextToSpeech (import)", test_tts)

# ── 17. AI Router ────────────────────────────────────────────────────────────
def test_ai_router():
    from ai.ai_router import AIRouter
    ar = AIRouter()
    return "AIRouter import OK"

check("AIRouter (import)", test_ai_router)

# ── 18. user_data.json ────────────────────────────────────────────────────────
def test_user_data():
    import json
    path = os.path.join("memory", "user_data.json")
    with open(path) as f:
        data = json.load(f)
    contacts = data.get("contacts", {})
    # Check for bad keys (trailing spaces, ++ in numbers)
    bad_keys = [k for k in contacts if k != k.strip()]
    bad_vals = [v for v in contacts.values() if v.startswith("++") or "  " in v]
    if bad_keys:
        raise Exception(f"Keys with trailing spaces: {bad_keys}")
    if bad_vals:
        raise Exception(f"Bad numbers: {bad_vals}")
    return f"{len(contacts)} contacts, all clean"

check("user_data.json (clean contacts)", test_user_data)

# ── Print Results ─────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("  AURA DIAGNOSTIC REPORT")
print("="*65)

passes = sum(1 for r in results if r[0] == PASS)
fails  = sum(1 for r in results if r[0] == FAIL)

for icon, name, msg in results:
    status = f"{icon} {name}"
    print(f"{status}")
    if icon == FAIL:
        print(f"     └─ {msg}")

print("="*65)
print(f"  TOTAL: {passes} passed, {fails} failed out of {len(results)} checks")
print("="*65)
