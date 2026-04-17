"""
automation/whatsapp.py
✅ FIXED: ChromeDriver 146 manually set (matches Chrome 146.0.7680.178)
✅ Persistent WhatsApp Web session
✅ Phonetic matching (Aakash = Akash)
"""

import os
import json
import time
import urllib.parse
from utils.logger import get_logger

logger = get_logger(__name__)

_wa_busy = False

# ✅ ChromeDriver 146 path — matches your Chrome version (146.0.7680.178)
CHROMEDRIVER_PATH = r"C:\ChromeDriver\chromedriver-win64\chromedriver.exe"


def _normalize(text: str) -> str:
    t = text.lower().strip()
    t = t.replace("aa", "a").replace("ee", "i").replace("oo", "u")
    return t


class WhatsApp:
    def __init__(self):
        self.contacts = self._load_contacts()
        self._driver = None

    def _load_contacts(self) -> dict:
        path = os.path.join(os.path.dirname(__file__), "..", "memory", "user_data.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data.get("contacts", {})
            except Exception as e:
                logger.warning(f"Could not load contacts: {e}")
        return {}

    def _clean_number(self, number: str) -> str:
        return "".join(filter(str.isdigit, number))

    def _resolve_number(self, name_or_number: str) -> str | None:
        if name_or_number.startswith("+") or name_or_number.isdigit():
            return name_or_number

        search = name_or_number.lower().strip()
        search_norm = _normalize(search)

        for key, number in self.contacts.items():
            if key.lower().strip() == search:
                logger.info(f"Exact match: {key}")
                return self._clean_number(number)

        for key, number in self.contacts.items():
            first = key.split()[0].lower().strip()
            if _normalize(first) == search_norm:
                logger.info(f"Phonetic match: '{name_or_number}' -> '{key}'")
                return self._clean_number(number)

        for key, number in self.contacts.items():
            first = key.split()[0].lower().strip()
            fn = _normalize(first)
            if fn.startswith(search_norm) or search_norm.startswith(fn):
                logger.info(f"Prefix match: '{name_or_number}' -> '{key}'")
                return self._clean_number(number)

        for key, number in self.contacts.items():
            if search in key.lower().strip():
                logger.info(f"Contains match: '{name_or_number}' in '{key}'")
                return self._clean_number(number)

        logger.warning(f"Contact not found: {name_or_number}")
        return None

    def _get_driver(self):
        """Get or create Chrome WebDriver with persistent session."""
        if self._driver:
            try:
                _ = self._driver.current_url
                return self._driver
            except Exception:
                self._driver = None

        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service

        options = Options()

        # Persistent profile — QR scan only once
        profile_dir = os.path.join(
            os.path.dirname(__file__), "..", "memory", "whatsapp_session"
        )
        os.makedirs(profile_dir, exist_ok=True)
        options.add_argument(f"--user-data-dir={os.path.abspath(profile_dir)}")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1200,800")

        # ✅ Verify ChromeDriver exists before starting
        if not os.path.exists(CHROMEDRIVER_PATH):
            raise FileNotFoundError(
                f"\n\nChromeDriver not found at:\n{CHROMEDRIVER_PATH}\n\n"
                "Run this command to download it:\n\n"
                "python -c \""
                "import urllib.request, zipfile, os; "
                "os.makedirs('C:/ChromeDriver', exist_ok=True); "
                "urllib.request.urlretrieve("
                "'https://storage.googleapis.com/chrome-for-testing-public/146.0.7680.178/win64/chromedriver-win64.zip', "
                "'C:/ChromeDriver/chromedriver.zip'); "
                "zipfile.ZipFile('C:/ChromeDriver/chromedriver.zip').extractall('C:/ChromeDriver/'); "
                "print('Done!')\""
            )

        service = Service(CHROMEDRIVER_PATH)
        self._driver = webdriver.Chrome(service=service, options=options)
        logger.info("Chrome started with ChromeDriver 146.")
        return self._driver

    def _wait_for_msgbox(self, driver, timeout=60):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        wait = WebDriverWait(driver, timeout)
        return wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                '//div[@contenteditable="true"][@data-tab="10"]'
            ))
        )

    def send_message(self, contact: str, message: str) -> str:
        global _wa_busy

        if not message or not message.strip():
            return "What should I say in the message?"
        if _wa_busy:
            return "I am still sending the last message. Please wait."

        number = self._resolve_number(contact)
        if not number:
            return f"I don't have {contact}'s number saved."

        _wa_busy = True
        try:
            from selenium.webdriver.common.keys import Keys

            clean_number = self._clean_number(number)
            encoded_msg  = urllib.parse.quote(message)
            url = f"https://web.whatsapp.com/send?phone={clean_number}&text={encoded_msg}"

            driver = self._get_driver()
            logger.info(f"Opening WhatsApp Web for {contact}...")
            driver.get(url)

            msg_box = self._wait_for_msgbox(driver)
            time.sleep(1)
            msg_box.click()
            time.sleep(0.5)
            msg_box.send_keys(Keys.ENTER)
            time.sleep(1)

            logger.info(f"Message sent to {contact}")
            return f"Done! Message sent to {contact} on WhatsApp!"

        except Exception as e:
            logger.error(f"WhatsApp send error: {e}")
            self._driver = None
            return f"Sorry, couldn't send the message. Error: {str(e)}"
        finally:
            _wa_busy = False

    def send_photo(self, contact: str, image_path: str, caption: str = "") -> str:
        if not os.path.exists(image_path):
            return f"Image not found: {image_path}"

        global _wa_busy
        if _wa_busy:
            return "I am still busy. Please wait."

        number = self._resolve_number(contact)
        if not number:
            return f"I don't have {contact}'s number saved."

        _wa_busy = True
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            clean_number = self._clean_number(number)
            driver = self._get_driver()
            driver.get(f"https://web.whatsapp.com/send?phone={clean_number}")

            wait = WebDriverWait(driver, 60)
            self._wait_for_msgbox(driver)
            time.sleep(1)

            attach_btn = wait.until(EC.presence_of_element_located((
                By.XPATH, '//span[@data-icon="attach-menu-plus"]'
            )))
            attach_btn.click()
            time.sleep(1)

            photo_input = wait.until(EC.presence_of_element_located((
                By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'
            )))
            photo_input.send_keys(os.path.abspath(image_path))
            time.sleep(2)

            if caption:
                try:
                    cap_box = driver.find_element(
                        By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'
                    )
                    cap_box.send_keys(caption)
                    time.sleep(0.5)
                except Exception:
                    pass

            send_btn = wait.until(EC.presence_of_element_located((
                By.XPATH, '//span[@data-icon="send"]'
            )))
            send_btn.click()
            time.sleep(1)

            logger.info(f"Photo sent to {contact}")
            return f"Done! Photo sent to {contact} on WhatsApp!"

        except Exception as e:
            logger.error(f"WhatsApp photo error: {e}")
            self._driver = None
            return f"Sorry, couldn't send the photo."
        finally:
            _wa_busy = False

    def send_file(self, contact: str, file_path: str, caption: str = "") -> str:
        if not os.path.exists(file_path):
            return f"File not found: {file_path}"

        global _wa_busy
        if _wa_busy:
            return "I am still busy. Please wait."

        number = self._resolve_number(contact)
        if not number:
            return f"I don't have {contact}'s number saved."

        _wa_busy = True
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            clean_number = self._clean_number(number)
            driver = self._get_driver()
            driver.get(f"https://web.whatsapp.com/send?phone={clean_number}")

            wait = WebDriverWait(driver, 60)
            self._wait_for_msgbox(driver)
            time.sleep(1)

            attach_btn = wait.until(EC.presence_of_element_located((
                By.XPATH, '//span[@data-icon="attach-menu-plus"]'
            )))
            attach_btn.click()
            time.sleep(1)

            doc_input = wait.until(EC.presence_of_element_located((
                By.XPATH, '//input[@accept="*"]'
            )))
            doc_input.send_keys(os.path.abspath(file_path))
            time.sleep(2)

            if caption:
                try:
                    cap_box = driver.find_element(
                        By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'
                    )
                    cap_box.send_keys(caption)
                    time.sleep(0.5)
                except Exception:
                    pass

            send_btn = wait.until(EC.presence_of_element_located((
                By.XPATH, '//span[@data-icon="send"]'
            )))
            send_btn.click()
            time.sleep(1)

            logger.info(f"File sent to {contact}")
            return f"Done! File sent to {contact} on WhatsApp!"

        except Exception as e:
            logger.error(f"WhatsApp file error: {e}")
            self._driver = None
            return f"Sorry, couldn't send the file."
        finally:
            _wa_busy = False

    def open_chat(self, contact: str) -> str:
        number = self._resolve_number(contact)
        if not number:
            return f"I don't have {contact}'s number saved."
        try:
            clean_number = self._clean_number(number)
            driver = self._get_driver()
            driver.get(f"https://web.whatsapp.com/send?phone={clean_number}")
            return f"Opening {contact}'s chat on WhatsApp!"
        except Exception as e:
            self._driver = None
            return f"Couldn't open chat: {str(e)}"

    def add_contact(self, name: str, number: str) -> str:
        path = os.path.join(os.path.dirname(__file__), "..", "memory", "user_data.json")
        data = {}
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        if "contacts" not in data:
            data["contacts"] = {}
        data["contacts"][name.lower().strip()] = number
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        self.contacts[name.lower().strip()] = number
        return f"Got it! Saved {name} with number {number}."


# ── Singleton ─────────────────────────────────────────────
_wa = None

def send_whatsapp(contact: str, message: str) -> str:
    global _wa
    if _wa is None:
        _wa = WhatsApp()
    return _wa.send_message(contact, message)


if __name__ == "__main__":
    wa = WhatsApp()
    print(wa.send_message("akash", "Hello from Aura! Testing WhatsApp Web."))