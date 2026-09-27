import time

import keyboard
import win32api
import win32gui
import win32process

# Windows message codes
WM_APPCOMMAND = 0x0319

# Windows API media command codes
APPCOMMAND_MEDIA_PLAY_PAUSE = 14
APPCOMMAND_MEDIA_NEXTTRACK = 11
APPCOMMAND_MEDIA_PREVIOUSTRACK = 12


def play_pause():
    """Playback toggle for the active window."""
    print("Action: Play/Pause (active window)")
    keyboard.send("play/pause")
    time.sleep(0.1)


def next_track():
    """Next track command for the active window."""
    print("Action: Next Track (active window)")
    keyboard.send("next track")
    time.sleep(0.1)


def prev_track():
    """Previous track command for the active window."""
    print("Action: Previous Track (active window)")
    keyboard.send("previous track")
    time.sleep(0.1)


# Background functions


def send_media_command_to_background(hwnd: int, action: str):
    """Send a media command directly to a background window by handle."""
    print(f"Sending background command '{action}' to HWND: {hwnd}")

    if action == "play_pause":
        cmd = APPCOMMAND_MEDIA_PLAY_PAUSE
    elif action == "next":
        cmd = APPCOMMAND_MEDIA_NEXTTRACK
    elif action == "prev":
        cmd = APPCOMMAND_MEDIA_PREVIOUSTRACK
    else:
        return

    # Message structure: WM_APPCOMMAND, window handle, command code shifted left by 16 bits
    win32api.PostMessage(hwnd, WM_APPCOMMAND, hwnd, cmd << 16)
