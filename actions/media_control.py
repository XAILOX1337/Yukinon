import keyboard
import win32api

# Windows message codes
WM_APPCOMMAND = 0x0319

# Windows API media command codes
APPCOMMAND_MEDIA_PLAY_PAUSE = 14
APPCOMMAND_MEDIA_NEXTTRACK = 11
APPCOMMAND_MEDIA_PREVIOUSTRACK = 12

# Background command lookup by action key
MEDIA_COMMAND_CODES = {
    "play_pause": APPCOMMAND_MEDIA_PLAY_PAUSE,
    "next": APPCOMMAND_MEDIA_NEXTTRACK,
    "prev": APPCOMMAND_MEDIA_PREVIOUSTRACK,
}


def play_pause():
    """Playback toggle for the active window."""
    print("Action: Play/Pause (active window)")
    keyboard.send("play/pause")


def next_track():
    """Next track command for the active window."""
    print("Action: Next Track (active window)")
    keyboard.send("next track")


def prev_track():
    """Previous track command for the active window."""
    print("Action: Previous Track (active window)")
    keyboard.send("previous track")


# Background functions


def send_media_command_to_background(hwnd: int, action: str):
    """Send a media command directly to a background window by handle."""
    cmd = MEDIA_COMMAND_CODES.get(action)
    if cmd is None:
        return

    print(f"Sending background command '{action}' to HWND: {hwnd}")

    # Message structure: WM_APPCOMMAND, window handle, command code shifted left by 16 bits
    win32api.PostMessage(hwnd, WM_APPCOMMAND, hwnd, cmd << 16)
