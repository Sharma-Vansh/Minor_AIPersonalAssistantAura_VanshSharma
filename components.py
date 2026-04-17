"""
gui/components.py — Reusable UI widgets for Aura
All custom components used across the GUI are defined here.
Import these in app_ui.py to keep the code clean and modular.
"""

import tkinter as tk
import customtkinter as ctk
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Design tokens ─────────────────────────────────────────
BG_DEEP   = "#0a0a0f"
BG_PANEL  = "#0f0f1a"
BG_CARD   = "#13131f"
ACCENT    = "#6c63ff"
ACCENT2   = "#00d4ff"
TEXT_PRI  = "#e8e8ff"
TEXT_SEC  = "#8888aa"
SUCCESS   = "#00ff88"
WARNING   = "#ffaa00"
DANGER    = "#ff4455"
USER_CLR  = "#00d4ff"
AURA_CLR  = "#6c63ff"


# ═══════════════════════════════════════════════════════════
#  1. Chat Bubble — single message in the conversation
# ═══════════════════════════════════════════════════════════

class ChatBubble(ctk.CTkFrame):
    """
    A styled message bubble for the chat panel.
    role = "user" → right-aligned cyan bubble
    role = "aura" → left-aligned purple bubble
    """
    def __init__(self, parent, text: str, role: str = "aura", **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        is_user  = role == "user"
        name     = "You" if is_user else "✦ Aura"
        clr      = USER_CLR if is_user else AURA_CLR
        bg       = "#1a2035" if is_user else "#1a1535"
        anchor   = "e"      if is_user else "w"
        side     = "right"  if is_user else "left"
        wrap     = 360

        # Sender + timestamp
        ctk.CTkLabel(
            self,
            text=f"{name}  •  {datetime.now().strftime('%I:%M %p')}",
            font=ctk.CTkFont(size=10),
            text_color=clr,
            anchor=anchor
        ).pack(anchor=anchor, padx=8, pady=(2, 0))

        # Bubble
        bubble = ctk.CTkFrame(self, fg_color=bg, corner_radius=14)
        bubble.pack(anchor=anchor, padx=8, pady=(2, 6))

        ctk.CTkLabel(
            bubble,
            text=text,
            wraplength=wrap,
            font=ctk.CTkFont(size=13),
            text_color=TEXT_PRI,
            justify="left",
            anchor="w"
        ).pack(padx=14, pady=10)


# ═══════════════════════════════════════════════════════════
#  2. StatusBar — bottom strip showing current Aura state
# ═══════════════════════════════════════════════════════════

class StatusBar(ctk.CTkFrame):
    """
    Bottom status bar showing:
    - Current state (Ready / Listening / Processing)
    - Last command
    - Module indicators
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=BG_PANEL, height=32, corner_radius=0, **kwargs)

        self.state_label = ctk.CTkLabel(
            self, text="●  Ready",
            font=ctk.CTkFont(size=11),
            text_color=SUCCESS
        )
        self.state_label.pack(side="left", padx=16, pady=6)

        # Divider
        ctk.CTkLabel(self, text="|", text_color=TEXT_SEC,
                     font=ctk.CTkFont(size=11)).pack(side="left")

        self.msg_label = ctk.CTkLabel(
            self, text="All systems operational.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_SEC
        )
        self.msg_label.pack(side="left", padx=10)

        # Module dots (right side)
        self.module_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.module_frame.pack(side="right", padx=16)

        self.module_dots = {}
        for mod in ["AI", "Voice", "Memory", "Net"]:
            dot = ctk.CTkLabel(
                self.module_frame,
                text=f"● {mod}",
                font=ctk.CTkFont(size=10),
                text_color=SUCCESS
            )
            dot.pack(side="left", padx=6)
            self.module_dots[mod] = dot

    def set_state(self, state: str, color: str = SUCCESS):
        self.state_label.configure(text=f"●  {state}", text_color=color)

    def set_message(self, msg: str):
        # Trim long messages
        if len(msg) > 60:
            msg = msg[:57] + "..."
        self.msg_label.configure(text=msg)

    def set_module(self, module: str, active: bool):
        if module in self.module_dots:
            color = SUCCESS if active else DANGER
            self.module_dots[module].configure(text_color=color)

    def listening(self):
        self.set_state("Listening...", WARNING)

    def processing(self):
        self.set_state("Processing...", ACCENT2)

    def ready(self):
        self.set_state("Ready", SUCCESS)


# ═══════════════════════════════════════════════════════════
#  3. OrbWidget — animated pulsing orb canvas
# ═══════════════════════════════════════════════════════════

class OrbWidget(tk.Canvas):
    """
    Animated orb that pulses when Aura is active.
    Idle = dark purple, Active = bright glowing purple/cyan.
    """
    def __init__(self, parent, size: int = 140, **kwargs):
        super().__init__(
            parent,
            width=size, height=size,
            bg=BG_PANEL,
            highlightthickness=0,
            **kwargs
        )
        self.size     = size
        self.cx       = size // 2
        self.cy       = size // 2
        self.active   = False
        self._job     = None
        self._step    = 0
        self.draw(active=False)

    def draw(self, active: bool = False, radius: int = 50):
        self.delete("all")
        cx, cy = self.cx, self.cy

        # Outer glow rings
        ring_clr = ACCENT2 if active else "#1a1a35"
        self.create_oval(cx-65, cy-65, cx+65, cy+65, outline=ring_clr, width=1)
        self.create_oval(cx-55, cy-55, cx+55, cy+55, outline=ACCENT if active else "#2a2a45", width=1)

        # Core orb
        fill = ACCENT if active else "#1e1e3a"
        self.create_oval(
            cx-radius, cy-radius, cx+radius, cy+radius,
            fill=fill, outline=ACCENT2 if active else ACCENT, width=2
        )

        # Inner shine
        self.create_oval(
            cx - radius//3, cy - radius//2,
            cx + radius//4, cy - radius//4,
            fill="#555577" if active else "#222233",
            outline=""
        )

        # Center label
        label = "ACTIVE" if active else "IDLE"
        color = TEXT_PRI if active else TEXT_SEC
        self.create_text(cx, cy, text=label, fill=color, font=("Courier New", 9, "bold"))

    def start_pulse(self):
        """Start the pulsing animation."""
        self.active = True
        self._pulse()

    def stop_pulse(self):
        """Stop pulsing and return to idle."""
        self.active = False
        if self._job:
            self.after_cancel(self._job)
        self.draw(active=False)

    def _pulse(self):
        if not self.active:
            return
        sizes = [46, 50, 54, 58, 54, 50]
        self.draw(active=True, radius=sizes[self._step % len(sizes)])
        self._step += 1
        self._job = self.after(250, self._pulse)


# ═══════════════════════════════════════════════════════════
#  4. MetricCard — small stat display card
# ═══════════════════════════════════════════════════════════

class MetricCard(ctk.CTkFrame):
    """
    Small card showing a label + value.
    Used for: CPU %, RAM, Battery, etc.
    """
    def __init__(self, parent, label: str, value: str = "—",
                 icon: str = "", accent: str = ACCENT, **kwargs):
        super().__init__(parent, fg_color=BG_CARD, corner_radius=12, **kwargs)

        # Icon + Label row
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(10, 2))

        if icon:
            ctk.CTkLabel(top, text=icon, font=ctk.CTkFont(size=14)).pack(side="left")

        ctk.CTkLabel(
            top, text=label.upper(),
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT_SEC
        ).pack(side="left", padx=(4 if icon else 0, 0))

        # Value
        self.value_label = ctk.CTkLabel(
            self, text=value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=accent
        )
        self.value_label.pack(padx=12, pady=(2, 10))

    def update_value(self, value: str):
        self.value_label.configure(text=value)


# ═══════════════════════════════════════════════════════════
#  5. SystemStatsBar — live CPU / RAM / Battery cards row
# ═══════════════════════════════════════════════════════════

class SystemStatsBar(ctk.CTkFrame):
    """
    A row of MetricCards showing live system stats.
    Auto-refreshes every 3 seconds.
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.cpu_card     = MetricCard(self, "CPU",     icon="⚡", accent=WARNING)
        self.ram_card     = MetricCard(self, "RAM",     icon="💾", accent=ACCENT)
        self.battery_card = MetricCard(self, "Battery", icon="🔋", accent=SUCCESS)

        self.cpu_card.pack(side="left",  expand=True, fill="x", padx=(0, 6))
        self.ram_card.pack(side="left",  expand=True, fill="x", padx=3)
        self.battery_card.pack(side="left", expand=True, fill="x", padx=(6, 0))

        self._refresh()

    def _refresh(self):
        """Update stats every 3 seconds."""
        try:
            import psutil

            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            bat = psutil.sensors_battery()

            self.cpu_card.update_value(f"{cpu}%")
            self.ram_card.update_value(f"{ram}%")

            if bat:
                plug = "⚡" if bat.power_plugged else ""
                self.battery_card.update_value(f"{int(bat.percent)}% {plug}")
            else:
                self.battery_card.update_value("N/A")

        except Exception as e:
            logger.debug(f"Stats refresh error: {e}")

        # Schedule next refresh
        self.after(3000, self._refresh)


# ═══════════════════════════════════════════════════════════
#  6. QuickActionButton — styled shortcut button
# ═══════════════════════════════════════════════════════════

class QuickActionButton(ctk.CTkButton):
    """
    A pre-styled quick action button for the left panel.
    Passes command text to sendPrompt-style callback.
    """
    def __init__(self, parent, label: str, command_text: str,
                 callback, **kwargs):
        super().__init__(
            parent,
            text=label,
            font=ctk.CTkFont(size=12),
            fg_color=BG_CARD,
            hover_color="#1e1e33",
            text_color=TEXT_PRI,
            corner_radius=10,
            height=36,
            command=lambda: callback(command_text),
            **kwargs
        )


# ═══════════════════════════════════════════════════════════
#  7. NotificationToast — popup notification inside GUI
# ═══════════════════════════════════════════════════════════

class NotificationToast(ctk.CTkFrame):
    """
    A small in-app notification that auto-dismisses after N seconds.
    type = "success" | "warning" | "error" | "info"
    """
    def __init__(self, parent, message: str,
                 kind: str = "info", duration_ms: int = 3000, **kwargs):
        colors = {
            "success": (SUCCESS, "#0a2a1a"),
            "warning": (WARNING, "#2a1f0a"),
            "error":   (DANGER,  "#2a0a0f"),
            "info":    (ACCENT2, "#0a1a2a"),
        }
        text_color, bg = colors.get(kind, colors["info"])

        super().__init__(parent, fg_color=bg, corner_radius=10,
                         border_width=1, border_color=text_color, **kwargs)

        icons = {"success": "✅", "warning": "⚠️", "error": "❌", "info": "ℹ️"}
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(padx=14, pady=10)

        ctk.CTkLabel(row, text=icons.get(kind, "ℹ️"),
                     font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(row, text=message,
                     font=ctk.CTkFont(size=12),
                     text_color=text_color,
                     wraplength=260).pack(side="left")

        # Auto-dismiss
        self.after(duration_ms, self.destroy)

    @classmethod
    def show(cls, parent, message: str, kind: str = "info"):
        """Show a toast notification at the bottom-right of parent."""
        toast = cls(parent, message, kind)
        toast.place(relx=0.98, rely=0.95, anchor="se")
        return toast