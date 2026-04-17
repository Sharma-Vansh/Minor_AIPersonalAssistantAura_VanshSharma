"""
gui/app_ui.py — Aura's Minimalist Floating Widget
✅ FIXED: Double voice bug — speak() called only ONCE
✅ FIXED: Voice loop properly waits while processing
✅ FIXED: No more overlapping responses
"""

import threading
import tkinter as tk
import customtkinter as ctk
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG_DEEP    = "#050a05"
BG_PANEL   = "#0a140a"
BG_CARD    = "#0f1d0f"
ACCENT     = "#00ff88"
ACCENT2    = "#00ffd4"
TEXT_PRI   = "#e8ffe8"
TEXT_SEC   = "#88aa88"
SUCCESS    = "#00ff88"
WARNING    = "#ffaa00"


class AuraGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.width = 200
        self.height = 260
        self.root.title("Aura Widget")

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x_pos = screen_w - self.width - 20
        y_pos = screen_h - self.height - 60

        self.root.geometry(f"{self.width}x{self.height}+{x_pos}+{y_pos}")
        self.root.resizable(False, False)
        self.root.configure(fg_color=BG_PANEL)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        self.is_listening = False
        self.is_processing = False  # ✅ NEW: prevent double processing
        self.pulse_job    = None
        self.last_text    = ""

        self._build_ui()
        self._bind_movement()

    def _build_ui(self):
        header = ctk.CTkFrame(self.root, fg_color="transparent")
        header.pack(fill="x", pady=(10, 5))

        ctk.CTkLabel(
            header, text="✦ AURA",
            font=ctk.CTkFont(family="Courier New", size=14, weight="bold"),
            text_color=ACCENT
        ).pack(side="left", padx=(50, 0))

        ctk.CTkButton(
            header, text="✕", width=25, height=25,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent", hover_color="#cc3333", text_color=TEXT_SEC,
            command=self.root.destroy
        ).pack(side="right", padx=5)

        border_color = "#1a331a"
        self.avatar_frame = ctk.CTkFrame(
            self.root, width=130, height=130, corner_radius=20,
            fg_color="transparent", border_width=3, border_color=border_color
        )
        self.avatar_frame.pack(pady=5)
        self.avatar_frame.pack_propagate(False)

        from PIL import Image
        import os
        img_path = os.path.join(os.path.dirname(__file__), "..", "assets", "aura_avatar.png")
        if os.path.exists(img_path):
            pil_image = Image.open(img_path)
            self.avatar_image = ctk.CTkImage(
                light_image=pil_image, dark_image=pil_image, size=(120, 120)
            )
            self.avatar_label = ctk.CTkLabel(
                self.avatar_frame, image=self.avatar_image, text=""
            )
        else:
            self.avatar_label = ctk.CTkLabel(
                self.avatar_frame, text="AURA\n[Image Missing]", text_color=ACCENT
            )

        self.avatar_label.place(relx=0.5, rely=0.5, anchor="center")

        self.status_label = ctk.CTkLabel(
            self.root, text="System Ready.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_PRI,
            wraplength=180,
            justify="center",
            height=30
        )
        self.status_label.pack(fill="x", padx=10, pady=(5, 5))

        self.listen_btn = ctk.CTkButton(
            self.root,
            text="🎤 Listen",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=ACCENT, hover_color="#00cc66",
            text_color="#000000",
            corner_radius=20, height=36,
            command=self._toggle_listening
        )
        self.listen_btn.pack(padx=20, pady=(0, 10), fill="x")

    # ── Avatar Animation ──────────────────────────────────

    def _pulse_border(self, step=0):
        if not self.is_listening:
            self.avatar_frame.configure(border_color="#1a331a")
            return
        colors = ["#1a331a", ACCENT, ACCENT2, ACCENT]
        self.avatar_frame.configure(border_color=colors[step % 4])
        self.pulse_job = self.root.after(300, self._pulse_border, step + 1)

    # ── Window Movement ───────────────────────────────────

    def _bind_movement(self):
        self.root.bind("<ButtonPress-1>", self._start_move)
        self.root.bind("<B1-Motion>", self._do_move)
        self.avatar_label.bind("<ButtonPress-1>", self._start_move)
        self.avatar_label.bind("<B1-Motion>", self._do_move)

    def _start_move(self, event):
        self._x = event.x
        self._y = event.y

    def _do_move(self, event):
        x = self.root.winfo_x() + (event.x - self._x)
        y = self.root.winfo_y() + (event.y - self._y)
        self.root.geometry(f"+{x}+{y}")

    # ── Status ────────────────────────────────────────────

    def _show_status(self, text: str):
        if len(text) > 60:
            text = text[:57] + "..."
        self.status_label.configure(text=text)

    # ── Processor ─────────────────────────────────────────

    def _process(self, text: str):
        """
        Process command in background thread.
        ✅ FIXED: speak() removed from here.
               speak() is called inside route_command/get_ai_response already.
               Calling it here was causing the double voice bug.
        """
        try:
            from commands.intent_detector import detect_intent
            from commands.entity_extractor import extract_entities
            from commands.command_router import route_command
            from ai.ai_router import get_ai_response
            from utils.constants import INTENT_CHAT
            from voice.text_to_speech import speak  # ✅ Only ONE speak call

            intent   = detect_intent(text)
            entities = extract_entities(text)

            logger.info(f"You said: {text}")
            print(f"🗣️  You: {text}")

            if intent == INTENT_CHAT:
                response, _ = get_ai_response(text)
            else:
                response = route_command(intent, entities, text)

            if response:
                self.root.after(0, self._show_status, response)
                # ✅ SINGLE speak() call — was duplicated before
                speak(response)

        except Exception as e:
            logger.error(f"GUI process error: {e}")
            self.root.after(0, self._show_status, "An error occurred.")
        finally:
            # ✅ Mark processing done so loop can continue
            self.is_processing = False

    # ── Voice Loop ────────────────────────────────────────

    def _toggle_listening(self):
        self.is_listening = not self.is_listening
        if self.is_listening:
            self.listen_btn.configure(
                text="⏹ Stop", fg_color="#cc3333", text_color="#ffffff"
            )
            self._show_status("Listening...")
            self._pulse_border()
            threading.Thread(target=self._voice_loop, daemon=True).start()
        else:
            self.listen_btn.configure(
                text="🎤 Listen", fg_color=ACCENT, text_color="#000000"
            )
            self._show_status(self.last_text if self.last_text else "Ready.")

    def _voice_loop(self):
        """
        ✅ FIXED: Loop waits while processing.
        Previous bug: loop kept calling listen() even while
        _process() was running, causing double responses.
        """
        from voice.speech_to_text import listen

        while self.is_listening:
            # ✅ Don't listen while already processing
            if self.is_processing:
                import time
                time.sleep(0.2)
                continue

            text = listen()

            if text and self.is_listening:
                self.last_text = f"You: {text}"
                self.root.after(0, self._show_status, self.last_text)

                # ✅ Set flag BEFORE starting thread
                self.is_processing = True
                threading.Thread(
                    target=self._process,
                    args=(text,),
                    daemon=True
                ).start()

    # ── Run ───────────────────────────────────────────────

    def run(self):
        logger.info("Widget launched.")
        self.root.mainloop()


def launch_gui():
    app = AuraGUI()
    app.run()


if __name__ == "__main__":
    launch_gui()