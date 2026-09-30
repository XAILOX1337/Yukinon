import difflib
import re
from enum import Enum

from actions.media_control import (
    next_track,
    play_pause,
    prev_track,
    send_media_command_to_background,
)
from actions.web_control import (
    close_current_tab,
    close_site,
    new_tab,
    next_tab,
    open_site,
    previous_tab,
    reopen_tab,
)
from actions.window_control import (
    find_app_hwnd,
    minimize_active,
    minimize_all,
    restore_all,
    switch_to_app,
    switch_window,
    toggle_maximize,
    toggle_show_desktop,
)
from config import APP_ALIASES
from core.listener import listen_free
from tts.speaker import speak


class CommandResult(Enum):
    """Outcome of command processing."""
    EXECUTED = "executed"  # Command recognized and run.
    UNKNOWN = "unknown"    # Command not recognized.
    EXIT = "exit"          # Exit signal received.


OPEN_SITE_MARKERS = ("open site", "go to", "open")
CLOSE_SITE_MARKERS = ("close site", "close")


def _extract_marker_query(command: str, markers):
    for marker in markers:
        if command.startswith(marker):
            return command[len(marker):].strip(" .")
    return ""


def _site_command_query(command: str, markers):
    query = _extract_marker_query(command, markers)
    if query:
        return query

    speak("Which site?")
    return listen_free()


def process_command(command: str) -> CommandResult:
    command = command.lower()

    if "exit" in command:
        return CommandResult.EXIT

    if "mai" in command or "jarvis" in command:
        return CommandResult.EXECUTED

    if "hello" in command or "hi" in command:
        speak("Greetings.")
        return CommandResult.EXECUTED

    if "how are you" in command:
        speak("All systems are operating normally.")
        return CommandResult.EXECUTED

    # Browser tab command block

    if command in ("next tab", "switch tab"):
        next_tab()
        return CommandResult.EXECUTED

    if command in ("previous tab", "prev tab"):
        previous_tab()
        return CommandResult.EXECUTED

    if command == "new tab":
        new_tab()
        return CommandResult.EXECUTED

    if command == "close tab":
        close_current_tab()
        return CommandResult.EXECUTED

    if command == "reopen tab":
        reopen_tab()
        return CommandResult.EXECUTED

    # Website command block

    if command == "open" or command.startswith("open site") or command.startswith("go to"):
        query = _site_command_query(command, OPEN_SITE_MARKERS)
        if query:
            open_site(query)
        else:
            speak("No site name received.")
        return CommandResult.EXECUTED

    if command == "close" or command.startswith("close site"):
        query = _site_command_query(command, CLOSE_SITE_MARKERS)
        if query:
            close_site(query)
        else:
            speak("No site name received.")
        return CommandResult.EXECUTED

    # Media command block

    if any(word in command for word in ("next", "previous", "prev", "back", "pause", "play", "resume", "continue")):
        MEDIA_ACTIONS = {
            "next": (["next"], next_track),
            "prev": (["previous", "prev", "back"], prev_track),
            "play_pause": (["pause", "play", "resume", "continue"], play_pause),
        }

        # 1. Action selection
        action_key = "play_pause"
        for key, (words, func) in MEDIA_ACTIONS.items():
            if any(w in command for w in words):
                action_key = key
                break

        # 2. Media keyword removal and application name extraction
        stop_words = [word for words, _ in MEDIA_ACTIONS.values() for word in words]
        stop_words += ["track", "song", "music", "on", "to", "the"]
        app_part = command
        for word in stop_words:
            app_part = app_part.replace(word, "")

        app_part = app_part.replace("  ", " ").strip()

        # 3. Empty remainder means the active window is the target
        if not app_part:
            print("Command targets the active window")
            dict(MEDIA_ACTIONS)[action_key][1]()
            return CommandResult.EXECUTED

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

        return CommandResult.EXECUTED

    # Alt + Tab block

    if command.startswith("switch"):
        if command.strip() == "switch":
            switch_window()
            return CommandResult.EXECUTED

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

        return CommandResult.EXECUTED

    # Window state control block

    if command in ("minimize", "minimize window"):
        minimize_active()
        return CommandResult.EXECUTED

    if command in ("maximize", "maximize window", "fullscreen", "full screen"):
        toggle_maximize()
        return CommandResult.EXECUTED

    if command == "minimize all":
        minimize_all()
        return CommandResult.EXECUTED

    if command == "restore all":
        restore_all()
        return CommandResult.EXECUTED

    if command == "show desktop":
        toggle_show_desktop()
        return CommandResult.EXECUTED

    # Fallback

    speak("I did not quite understand. Please repeat.")
    return CommandResult.UNKNOWN
