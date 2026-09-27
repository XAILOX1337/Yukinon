import difflib
import re

from actions.media_control import (
    next_track,
    play_pause,
    prev_track,
    send_media_command_to_background,
)
from actions.window_control import find_app_hwnd, switch_to_app, switch_window
from config import APP_ALIASES
from tts.speaker import speak


def process_command(command: str) -> bool:
    command = command.lower()

    if "exit" in command or "stop" in command:
        return True

    elif "hello" in command or "hi" in command:
        speak("Greetings.")

    elif "how are you" in command:
        speak("All systems are operating normally.")

    # Media command block

    MEDIA_ACTIONS = {
        "next": (["next"], next_track),
        "prev": (["previous", "prev", "back"], prev_track),
        "play_pause": (["pause", "play", "resume", "continue"], play_pause),
    }

    all_media_words = [word for words, _ in MEDIA_ACTIONS.values() for word in words]

    if any(word in command for word in all_media_words):
        # 1. Action selection
        action_key = "play_pause"
        for key, (words, func) in MEDIA_ACTIONS.items():
            if any(w in command for w in words):
                action_key = key
                break

        # 2. Media keyword removal and application name extraction
        stop_words = all_media_words + ["track", "song", "music", "on", "to", "the"]
        app_part = command
        for word in stop_words:
            app_part = app_part.replace(word, "")

        app_part = app_part.replace("  ", " ").strip()

        # 3. Empty remainder means the active window is the target
        if not app_part:
            print("Command targets the active window")
            dict(MEDIA_ACTIONS)[action_key][1]()
            return False

        # 4. Remaining text means a background application is the target
        glued_app = app_part.replace(" ", "")
        matches = difflib.get_close_matches(glued_app, list(APP_ALIASES.keys()), n=1, cutoff=0.6)

        if matches:
            app_name = matches[0]
            print(f"[Fuzzy match] Background command for: {app_name}")

            hwnd = find_app_hwnd(app_name)
            if hwnd:
                send_media_command_to_background(hwnd, action_key)
            else:
                speak(f"Application {app_name} is not running.")
        else:
            print(f"Could not recognize an application in phrase: {app_part}")

        return False

    # Alt + Tab block
    elif command.startswith("switch"):
        if command.strip() == "switch":
            switch_window()
            return False

        match = re.search(r"switch\s+(.+)", command)
        if match:
            raw_app_name = match.group(1)
            glued_name = raw_app_name.replace(" ", "")

            known_apps = list(APP_ALIASES.keys())
            matches = difflib.get_close_matches(glued_name, known_apps, n=1, cutoff=0.6)

            if matches:
                app_name = matches[0]
                print(f"[Fuzzy match] Heard '{raw_app_name}', corrected to '{app_name}'")
            else:
                app_name = glued_name

            success = switch_to_app(app_name)

            if not success:
                speak(f"Could not find running application {app_name}. Check the alias dictionary.")
        else:
            switch_window()

    else:
        speak("I did not quite understand. Please repeat.")

    return False
