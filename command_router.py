"""
commands/command_router.py — WhatsApp handler updated
✅ send photo → wa.send_photo()
✅ send file  → wa.send_file()
✅ open chat  → wa.open_chat()
(rest of file unchanged — only _handle_whatsapp updated)
"""

from utils.logger import get_logger
from utils.constants import *

logger = get_logger(__name__)

_WAKE_WORDS = ["aura", "hey aura", "ok aura", "oi aura"]


def _strip_wake(text: str) -> str:
    t = text.lower().strip()
    for w in sorted(_WAKE_WORDS, key=len, reverse=True):
        if t.startswith(w):
            t = t[len(w):].strip()
            break
    return t


class CommandRouter:

    def route(self, intent: str, entities: dict, raw_text: str) -> str:
        logger.info(f"Routing intent='{intent}' entities={entities}")

        routes = {
            INTENT_YOUTUBE:   self._handle_youtube,
            INTENT_BROWSER:   self._handle_browser,
            INTENT_WHATSAPP:  self._handle_whatsapp,
            INTENT_SYSTEM:    self._handle_system,
            INTENT_WEATHER:   self._handle_weather,
            INTENT_NEWS:      self._handle_news,
            INTENT_REMINDER:  self._handle_reminder,
            INTENT_EMAIL:     self._handle_email,
            INTENT_FILE:      self._handle_file,
            INTENT_OPEN_APP:  self._handle_open_app,
            INTENT_CLOSE_APP: self._handle_close_app,
            INTENT_SPOTIFY:   self._handle_spotify,
        }

        handler = routes.get(intent)
        if handler:
            return handler(entities, raw_text)
        return "I'm not sure what to do with that. Could you rephrase?"

    # ── WhatsApp ──────────────────────────────────────────

    def _handle_whatsapp(self, entities: dict, text: str) -> str:
        import threading
        from automation.whatsapp import WhatsApp
        wa = WhatsApp()

        t = _strip_wake(text.lower())
        contact = entities.get("contact")
        message = entities.get("message", "")

        # ── Open chat only ────────────────────────────────
        if any(w in t for w in ["open chat", "open whatsapp", "show chat"]):
            if not contact:
                return "Which contact's chat should I open?"
            return wa.open_chat(contact)

        # ── Send Photo ────────────────────────────────────
        if any(w in t for w in ["send photo", "send image", "photo bhejo",
                                  "image bhejo", "send picture", "tasveer bhejo"]):
            if not contact:
                return "Who should I send the photo to?"

            # Get file path from entities or ask
            file_path = entities.get("file_path") or entities.get("query")
            if not file_path:
                return f"Which photo should I send to {contact}? Please say the file name."

            caption = message or ""

            def _send_photo():
                result = wa.send_photo(contact, file_path, caption)
                logger.info(f"Photo result: {result}")

            threading.Thread(target=_send_photo, daemon=True).start()
            return f"Sending photo to {contact} on WhatsApp!"

        # ── Send File / Document ──────────────────────────
        if any(w in t for w in ["send file", "send document", "send pdf",
                                  "file bhejo", "document bhejo", "pdf bhejo"]):
            if not contact:
                return "Who should I send the file to?"

            file_path = entities.get("file_path") or entities.get("query")
            if not file_path:
                return f"Which file should I send to {contact}? Please say the file name."

            caption = message or ""

            def _send_file():
                result = wa.send_file(contact, file_path, caption)
                logger.info(f"File result: {result}")

            threading.Thread(target=_send_file, daemon=True).start()
            return f"Sending file to {contact} on WhatsApp!"

        # ── Send Text Message (default) ───────────────────
        if not contact:
            return "Who should I send the WhatsApp message to?"
        if not message:
            return f"What should I say to {contact}?"

        number = wa._resolve_number(contact)
        if not number:
            return (
                f"I don't have {contact}'s number saved. "
                f"Please add them to memory/user_data.json first."
            )

        def _send():
            result = wa.send_message(contact, message)
            logger.info(f"WhatsApp result: {result}")

        threading.Thread(target=_send, daemon=True).start()
        return f"Ok! Sending your message to {contact} on WhatsApp right now!"

    # ── YouTube ───────────────────────────────────────────

    def _handle_youtube(self, entities: dict, text: str) -> str:
        from automation.youtube import YouTube
        yt = YouTube()
        t = _strip_wake(text)

        if any(w in t for w in ["skip ad", "ad skip"]):
            return yt.skip_ad_now()
        if any(w in t for w in ["pause", "stop", "ruko"]):
            return yt.pause_video()
        if any(w in t for w in ["next", "agla", "skip song"]):
            return yt.skip_forward()
        if any(w in t for w in ["back", "previous", "pichla"]):
            return yt.skip_backward()
        if any(w in t for w in ["fullscreen", "full screen"]):
            return yt.fullscreen()
        if any(w in t for w in ["bollywood", "hindi songs"]):
            return yt.play_bollywood()
        if any(w in t for w in ["lofi", "study music", "chill"]):
            return yt.play_lofi()

        song = entities.get("song") or entities.get("query")
        if song:
            song = yt._clean_query(song)
            return yt.play(song)
        return yt.open_youtube()

    # ── Spotify ───────────────────────────────────────────

    def _handle_spotify(self, entities: dict, text: str) -> str:
        from automation.spotify import Spotify
        sp = Spotify()
        t = _strip_wake(text)

        if any(w in t for w in ["pause", "ruk", "rok", "band kar"]):
            return sp.pause()
        if any(w in t for w in ["resume", "chalu", "play karo", "shuru"]):
            return sp.resume()
        if any(w in t for w in ["next", "agla", "skip"]):
            return sp.next_track()
        if any(w in t for w in ["previous", "pichla", "back"]):
            return sp.previous_track()
        if "volume" in t or "awaaz" in t:
            if any(w in t for w in ["up", "increase", "badha"]):
                return sp.volume_up()
            if any(w in t for w in ["down", "decrease", "kam"]):
                return sp.volume_down()
            if "mute" in t:
                return sp.mute()

        song = entities.get("song") or entities.get("query")
        if song:
            song = sp._clean_query(song)
            return sp.play(song)
        return sp.open_spotify()

    # ── Browser ───────────────────────────────────────────

    def _handle_browser(self, entities: dict, text: str) -> str:
        from automation.browser import Browser
        b = Browser()

        if "url" in entities:
            return b.open_website(entities["url"])
        if "site" in entities:
            return b.open_common_site(entities["site"])
        query = entities.get("query")
        if query:
            return b.google_search(query)

        t = text.lower()
        if "back" in t:        return b.go_back()
        if "forward" in t:     return b.go_forward()
        if "refresh" in t:     return b.refresh_page()
        if "close tab" in t:   return b.close_tab()
        if "new tab" in t:     return b.open_new_tab()
        if "scroll down" in t: return b.scroll_down()
        if "scroll up" in t:   return b.scroll_up()
        if "map" in t or "location" in t:
            return b.search_maps(entities.get("query", "India"))
        if "wikipedia" in t or "wiki" in t:
            return b.search_wikipedia(entities.get("query", ""))
        return b.google_search(text)

    # ── System ────────────────────────────────────────────

    def _handle_system(self, entities: dict, text: str) -> str:
        from automation.system import SystemControl
        s = SystemControl()
        number = entities.get("number")

        if "volume" in text or "awaaz" in text:
            if any(w in text for w in ["up", "increase", "badha"]):
                return s.volume_up(number or 10)
            if any(w in text for w in ["down", "decrease", "kam"]):
                return s.volume_down(number or 10)
            if "mute" in text:
                return s.mute()
            if number is not None:
                return s.set_volume(number)
            return s.volume_up()

        if "brightness" in text or "screen" in text:
            if any(w in text for w in ["up", "increase", "badha"]):
                return s.brightness_up(number or 10)
            if any(w in text for w in ["down", "decrease", "kam"]):
                return s.brightness_down(number or 10)
            if number is not None:
                return s.set_brightness(number)
            return s.brightness_up()

        if "battery" in text or "charging" in text:
            return s.get_battery()
        if "cpu" in text or "ram" in text or "system" in text:
            return s.get_system_info()
        if "shutdown" in text:
            return s.shutdown(number or 60)
        if "restart" in text or "reboot" in text:
            return s.restart(number or 60)
        if "cancel shutdown" in text:
            return s.cancel_shutdown()
        if "sleep" in text:
            return s.sleep()
        if "lock" in text:
            return s.lock_screen()
        return s.get_system_info()

    # ── Weather ───────────────────────────────────────────

    def _handle_weather(self, entities: dict, text: str) -> str:
        try:
            from api.weather_api import get_weather
            city = entities.get("query") or entities.get("site") or None
            return get_weather(city)
        except Exception as e:
            return "I couldn't fetch the weather right now."

    # ── News ──────────────────────────────────────────────

    def _handle_news(self, entities: dict, text: str) -> str:
        try:
            from api.news_api import get_news
            return get_news()
        except Exception as e:
            return "I couldn't fetch the news right now."

    # ── Reminder ──────────────────────────────────────────

    def _handle_reminder(self, entities: dict, text: str) -> str:
        try:
            from automation.reminder import set_reminder, _manager

            if any(w in text for w in ["cancel", "stop", "hatao"]):
                if _manager and _manager.active_reminders:
                    count = len(_manager.active_reminders)
                    _manager.active_reminders.clear()
                    return f"Cancelled {count} active reminder(s)."
                return "No active reminders to cancel."

            minutes = entities.get("reminder_minutes", 0)
            hours   = entities.get("reminder_hours", 0)
            task    = entities.get("reminder_task", "your reminder")
            total   = minutes + (hours * 60)
            if total <= 0:
                return "How many minutes should I set the reminder for?"
            return set_reminder(task, total)
        except Exception as e:
            logger.error(f"Reminder error: {e}")
            return "I couldn't set the reminder. Try again."

    # ── Email ─────────────────────────────────────────────

    def _handle_email(self, entities: dict, text: str) -> str:
        try:
            import threading
            from automation.email import Email
            e = Email()
            t = text.lower()

            if any(w in t for w in ["inbox", "check", "read", "open"]):
                return e.check_inbox()
            if any(w in t for w in ["compose", "new email"]):
                return e.compose_new()

            contact = entities.get("contact")
            message = entities.get("message")
            subject = entities.get("subject", "Message from Aura")

            if contact and message:
                def _send():
                    result = e.send_email(contact, subject, message)
                    logger.info(f"Email result: {result}")
                threading.Thread(target=_send, daemon=True).start()
                return f"Ok! Sending email to {contact} via Outlook!"

            return "Who should I email and what should I say?"
        except Exception as ex:
            logger.error(f"Email handler error: {ex}")
            return "Email module error."

    # ── File ──────────────────────────────────────────────

    def _handle_file(self, entities: dict, text: str) -> str:
        try:
            from automation.file_manager import FileManager
            fm = FileManager()
            if "open folder" in text:
                folder = entities.get("query")
                return fm.open_folder(folder) if folder else "Which folder?"
            if "open" in text and "file" in text:
                f = entities.get("query")
                return fm.open_file(f) if f else "Which file?"
            if any(w in text for w in ["create", "make", "new"]):
                if "folder" in text:
                    return fm.create_folder(entities.get("query") or "New Folder")
                return fm.create_text_file(entities.get("query") or "New File")
            if any(w in text for w in ["find", "search"]):
                q = entities.get("query")
                return fm.search_file(q) if q else "What file?"
            if any(w in text for w in ["delete", "remove"]):
                f = entities.get("query")
                return fm.delete_file(f) if f else "Which file to delete?"
            if any(w in text for w in ["disk", "space", "storage"]):
                return fm.get_disk_info()
            return "I can list, search, open, or delete files."
        except Exception as e:
            return "Something went wrong with file manager."

    # ── Open App ──────────────────────────────────────────

    def _handle_open_app(self, entities: dict, text: str) -> str:
        from automation.app_controller import AppController
        ac = AppController()
        app_name = entities.get("app") or entities.get("site") or entities.get("query")
        if not app_name:
            app_name = self._strip_trigger_words(
                _strip_wake(text),
                ["open", "launch", "start", "run", "load",
                 "boot", "fire up", "chalu karo", "kholo", "shuru karo"]
            )
        if not app_name:
            return "Which app should I open?"
        logger.info(f"Open app handler: app_name='{app_name}'")
        return ac.open_app(app_name.strip())

    # ── Close App ─────────────────────────────────────────

    def _handle_close_app(self, entities: dict, text: str) -> str:
        from automation.app_controller import AppController
        ac = AppController()
        app_name = entities.get("app") or entities.get("site") or entities.get("query")
        if not app_name:
            app_name = self._strip_trigger_words(
                _strip_wake(text),
                ["close", "shut", "exit", "quit", "kill",
                 "terminate", "end", "stop", "shut down",
                 "band karo", "band kar do", "hat jao"]
            )
        if not app_name:
            return "Which app should I close?"
        logger.info(f"Close app handler: app_name='{app_name}'")
        return ac.close_app(app_name.strip())

    # ── Helper ────────────────────────────────────────────

    def _strip_trigger_words(self, text: str, trigger_words: list) -> str:
        text = text.lower().strip()
        for word in sorted(trigger_words, key=len, reverse=True):
            if text.startswith(word):
                text = text[len(word):].strip()
                break
            elif text.endswith(word):
                text = text[:-len(word)].strip()
                break
        filler = ["please", "now", "for me", "quickly", "bhai",
                  "yaar", "jaldi", "abhi", "kar do"]
        for f in filler:
            if text.endswith(f):
                text = text[:-len(f)].strip()
        return text.strip()


# ── Singleton ─────────────────────────────────────────────
_router = None

def route_command(intent: str, entities: dict, raw_text: str) -> str:
    global _router
    if _router is None:
        _router = CommandRouter()
    return _router.route(intent, entities, raw_text)