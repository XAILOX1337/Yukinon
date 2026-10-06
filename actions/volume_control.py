import time

import keyboard
import psutil
from pycaw.pycaw import AudioUtilities

from config import APP_ALIASES

# Per-application volume step, part of a session volume (0.0 - 1.0)
APP_VOLUME_STEP = 0.1


# System volume (handled by the OS, so it works regardless of the focused window)


def volume_up():
    """Raise the system volume."""
    print("Action: Volume up")
    keyboard.send("volume up")
    time.sleep(0.01)


def volume_down():
    """Lower the system volume."""
    print("Action: Volume down")
    keyboard.send("volume down")
    time.sleep(0.01)


def toggle_mute():
    """Mute or unmute the system volume."""
    print("Action: Toggle mute")
    keyboard.send("volume mute")
    time.sleep(0.01)


# Background functions (per-application audio session)


def send_volume_to_background(spoken_name: str, action: str) -> bool:
    """Adjust one application's own audio session without focusing it."""
    target_exe = APP_ALIASES.get(spoken_name)

    if not target_exe:
        print(f"Word '{spoken_name}' is missing from APP_ALIASES")
        return False

    print(f"Audio session search: {target_exe}")

    # 1. Process ID collection
    target_pids = []
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"] and proc.info["name"].lower() == target_exe.lower():
            target_pids.append(proc.info["pid"])

    if not target_pids:
        print(f"No running processes found for {target_exe}.")
        return False

    # 2. Audio session search by process ID
    adjusted = 0
    for session in AudioUtilities.GetAllSessions():
        try:
            if not session.Process or session.Process.pid not in target_pids:
                continue

            volume = session.SimpleAudioVolume
            if action == "mute":
                volume.SetMute(0 if volume.GetMute() else 1, None)
            elif action == "volume_up":
                volume.SetMasterVolume(min(volume.GetMasterVolume() + APP_VOLUME_STEP, 1.0), None)
            elif action == "volume_down":
                volume.SetMasterVolume(max(volume.GetMasterVolume() - APP_VOLUME_STEP, 0.0), None)
            else:
                continue
            adjusted += 1
        except Exception:
            # Protected or dying sessions can refuse the call
            continue

    if not adjusted:
        print(f"No audio session found for {target_exe}.")
        return False

    print(f"Adjusted {adjusted} audio session(s) for {target_exe}.")
    return True
