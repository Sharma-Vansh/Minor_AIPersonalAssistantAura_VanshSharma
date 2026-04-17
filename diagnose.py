import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== FAILURE DIAGNOSIS ===\n")

# 1. Intent Detector
print("--- Intent Detector ---")
try:
    from commands.intent_detector import detect_intent
    tests = {
        "send message to akash": "whatsapp",
        "play honey singh song": "youtube",
        "open notepad": "open_app",
        "close excel": "close_app",
        "what is the weather": "weather",
        "latest news": "news",
        "remind me in 5 minutes": "reminder",
        "send email to akash": "email",
        "find my file": "file",
        "volume up": "system",
        "play on spotify": "spotify",
    }
    for text, expected in tests.items():
        got = detect_intent(text)
        status = "PASS" if got == expected else "FAIL"
        print(f"  [{status}] '{text}' -> '{got}' (expected '{expected}')")
except Exception as e:
    print(f"  [ERROR] {e}")

# 2. Entity Extractor
print("\n--- Entity Extractor ---")
try:
    from commands.entity_extractor import EntityExtractor
    ex = EntityExtractor()
    result = ex.extract("send message tu akash hello bhai", "whatsapp")
    print(f"  Result: {result}")
    if not result.get("contact"):
        print("  [FAIL] No contact extracted")
    else:
        print(f"  [PASS] contact={result['contact']} message={result.get('message')}")
except Exception as e:
    print(f"  [ERROR] {e}")

# 3. WhatsApp fuzzy Aakash
print("\n--- WhatsApp fuzzy 'Aakash' ---")
try:
    from automation.whatsapp import WhatsApp
    wa = WhatsApp()
    print(f"  Contacts keys: {list(wa.contacts.keys())[:8]}")
    num = wa._resolve_number("Aakash")
    print(f"  'Aakash' resolved to: {num}")
    if not num:
        print("  [FAIL] Double-A spelling not resolved")
    else:
        print("  [PASS]")
except Exception as e:
    print(f"  [ERROR] {e}")

# 4. Command Router
print("\n--- Command Router handlers ---")
try:
    from commands.command_router import CommandRouter
    router = CommandRouter()
    handlers = [
        "_handle_spotify", "_handle_whatsapp", "_handle_email",
        "_handle_file", "_handle_reminder", "_handle_youtube",
        "_handle_browser", "_handle_system", "_handle_weather",
        "_handle_news", "_handle_open_app", "_handle_close_app"
    ]
    for h in handlers:
        status = "PASS" if hasattr(router, h) else "FAIL"
        print(f"  [{status}] {h}")
except Exception as e:
    print(f"  [ERROR] {e}")

print("\n=== DONE ===")
