"""
WhatsApp diagnostic — run WHILE WhatsApp Desktop is already open.
This tells us:
1. Which WhatsApp window handles exist
2. Their exact title and position
3. Whether we can focus them
"""
import sys
sys.path.insert(0, ".")

import win32gui
import win32con
import time
import pyautogui

print("=" * 55)
print("  WHATSAPP WINDOW DIAGNOSTIC")
print("=" * 55)

# Step 1: Find all windows, list WhatsApp ones
print("\n[1] Scanning for WhatsApp windows...")
wa_windows = []

def cb(hwnd, _):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if title:  # Print ALL visible windows with titles
            wa_windows.append((hwnd, title))

win32gui.EnumWindows(cb, None)

# Filter and show WhatsApp windows
wa_only = [(h, t) for h, t in wa_windows if "whatsapp" in t.lower() or "WhatsApp" in t]
print(f"    Found {len(wa_only)} WhatsApp window(s):")
for hwnd, title in wa_only:
    rect = win32gui.GetWindowRect(hwnd)
    print(f"    - hwnd={hwnd} title='{title}' rect={rect}")

if not wa_only:
    print("\n    [!] NO WhatsApp windows found!")
    print("        Either WhatsApp is not open, or its window title doesn't contain 'WhatsApp'")
    print("\n    Top 30 visible windows:")
    for hwnd, title in wa_windows[:30]:
        print(f"        - '{title}'")
    sys.exit(1)

# Step 2: Use first WhatsApp window
hwnd, title = wa_only[0]
left, top, right, bottom = win32gui.GetWindowRect(hwnd)
win_w = right - left
win_h = bottom - top

print(f"\n[2] Using: hwnd={hwnd}, '{title}'")
print(f"    Position: left={left}, top={top}, right={right}, bottom={bottom}")
print(f"    Size: {win_w} x {win_h}")

# Step 3: Bring to foreground
print("\n[3] Bringing to foreground...")
win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
win32gui.SetForegroundWindow(hwnd)
time.sleep(1)
print("    Done.")

# Step 4: Calculate message box click position
click_x = left + win_w // 2
click_y = bottom - int(win_h * 0.07)  # 7% from bottom
print(f"\n[4] Message box click target: ({click_x}, {click_y})")
print(f"    (That's {win_h * 0.07:.0f}px from the bottom of WhatsApp window)")

# Step 5: Click and paste test message
print("\n[5] Clicking message box and typing test...")
pyautogui.click(click_x, click_y)
time.sleep(0.4)

import pyperclip
test_msg = "TEST from Aura - automated message"
pyperclip.copy(test_msg)
pyautogui.hotkey("ctrl", "v")
time.sleep(0.5)

print(f"    Pasted: '{test_msg}'")
print("\n    >>> Check WhatsApp — is the text visible in the message box? <<<")
print("    If YES: the fix works! The issue was timing.")
print("    If NO:  the click coordinates are wrong for your screen.")

# Show where we clicked on screen
sw, sh = pyautogui.size()
print(f"\n    Screen size: {sw}x{sh}")
print(f"    Click was at: ({click_x}, {click_y})")
print(f"    As % of screen: ({click_x/sw*100:.1f}%, {click_y/sh*100:.1f}%)")
print("\n    DO NOT press Enter — just check if text appeared in WhatsApp.")
print("=" * 55)
