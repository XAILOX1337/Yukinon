import difflib
import re
from enum import Enum

from actions.app_launcher import open_app
from actions.media_control import (
    next_track,
    play_pause,
    prev_track,
    send_media_command_to_background,
)
from actions.process_control import terminate_app
from actions.volume_control import (
    send_volume_to_background,
    toggle_mute,
    volume_down,
    volume_up,
)
from actions.web_control import (
    close_current_tab,
    new_tab,
    next_tab,
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
from config import APP_ALIASES, WAKE_WORDS
from tts.speaker import speak


class CommandResult(Enum):
    """Outcome of command processing."""
    EXECUTED = "executed"  # Command recognized and run.
    UNKNOWN = "unknown"    # Command not recognized.
    EXIT = "exit"          # Exit signal received.


TERMINATE_MARKERS = ("terminate", "kill", "shut down", "close")
# Trailing space keeps "opening" out of the query
OPEN_MARKERS = ("open ", "launch ", "run ")
ALIAS_KEYS = list(APP_ALIASES)


def _extract_marker_query(command: str, markers):
    for marker in markers:
        if command.startswith(marker):
            return command[len(marker):].strip(" .")
    return ""


def _fuzzy_app_name(raw_name: str, cutoff: float = 0.6):
    """Correct a misheard application name against the alias dictionary."""
    glued_name = raw_name.replace(" ", "")
    matches = difflib.get_close_matches(glued_name, ALIAS_KEYS, n=1, cutoff=cutoff)

    if matches:
        print(f"[Fuzzy match] Heard '{raw_name}', corrected to '{matches[0]}'")
        return matches[0]
    return None


def process_command(command: str) -> CommandResult:
    command = command.lower()
    words = command.split()

    # A wake word is stripped from an active command instead of swallowing it
    if any(word in WAKE_WORDS for word in words):
        words = [word for word in words if word not in WAKE_WORDS]
        if not words:
            return CommandResult.EXECUTED
        command = " ".join(words)

    # Exit only when the utterance carries nothing else, otherwise
    # "open exit lag" would quit the assistant
    if words and set(words) <= {"exit", "stop"}:
        return CommandResult.EXIT

    if set(words) & {"hello", "hi"}:
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

    # Application launch block

    if command in ("open", "launch", "run"):
        speak("Which application?")
        return CommandResult.EXECUTED

    launch_query = _extract_marker_query(command, OPEN_MARKERS)
    if launch_query:
        if not open_app(launch_query):
            print(f"Could not open {launch_query}.")

        return CommandResult.EXECUTED

    # Process termination block

    terminate_query = _extract_marker_query(command, TERMINATE_MARKERS)
    if terminate_query:
        # Killing is destructive: a stricter cutoff keeps a garbage word from
        # fuzzy-matching a real application ("site" would become "steam")
        app_name = _fuzzy_app_name(terminate_query, cutoff=0.7)
        if app_name is None:
            app_name = terminate_query.replace(" ", "")

        if not terminate_app(app_name):
            speak(f"Could not find running application {app_name}.")

        return CommandResult.EXECUTED

    # Media command block

    if any(word in command for word in ("next", "previous", "prev", "back", "pause", "play", "resume", "continue")):
        MEDIA_ACTIONS = {
            "next": (["next"], next_track),
            "prev": (["previous", "prev", "back"], prev_track),
            "play_pause": (["pause", "play", "resume", "continue"], play_pause),
        }

        # 1. Action selection
        action_key, action_func = "play_pause", play_pause
        for key, (words, func) in MEDIA_ACTIONS.items():
            if any(word in command for word in words):
                action_key, action_func = key, func
                break

        # 2. Media keyword removal and application name extraction
        stop_words = [word for words, _ in MEDIA_ACTIONS.values() for word in words]
        stop_words += ["track", "song", "music", "on", "to", "the"]

        # Token filtering keeps substrings safe: replace() would mangle names
        app_part = " ".join(word for word in command.split() if word not in stop_words)

        # 3. Empty remainder means the active window is the target
        if not app_part:
            print("Command targets the active window")
            action_func()
            return CommandResult.EXECUTED

        # 4. Remaining text means a background application is the target
        app_name = _fuzzy_app_name(app_part)

        if app_name:
            hwnd = find_app_hwnd(app_name)
            if hwnd:
                send_media_command_to_background(hwnd, action_key)
            else:
                print(f"Application {app_name} is not running.")
        else:
            print(f"Could not recognize an application in phrase: {app_part}")

        return CommandResult.EXECUTED

    # Volume control block

    if any(word in command for word in ("volume", "louder", "quieter", "mute")):
        VOLUME_ACTIONS = {
            "volume_up": (["louder", "up"], volume_up),
            "volume_down": (["quieter", "down"], volume_down),
            "mute": (["mute"], toggle_mute),
        }

        # 1. Action selection
        action_key, action_func = None, None
        for key, (words, func) in VOLUME_ACTIONS.items():
            if any(word in command for word in words):
                action_key, action_func = key, func
                break

        if action_key is None:
            speak("Louder or quieter?")
            return CommandResult.EXECUTED

        # 2. Volume keyword removal and application name extraction
        stop_words = [word for words, _ in VOLUME_ACTIONS.values() for word in words]
        stop_words += ["volume", "for", "the", "on", "to"]

        # Token filtering keeps substrings safe: replace() would turn "discord" into "dscord"
        app_part = " ".join(word for word in command.split() if word not in stop_words)

        # 3. Empty remainder means the system volume is the target
        if not app_part:
            action_func()
            return CommandResult.EXECUTED

        # 4. Remaining text means a background application is the target
        app_name = _fuzzy_app_name(app_part)

        if app_name:
            if not send_volume_to_background(app_name, action_key):
                speak(f"Could not change volume for {app_name}.")
        else:
            print(f"Could not recognize an application in phrase: {app_part}")

        return CommandResult.EXECUTED

    # Alt + Tab block

    if command.startswith("switch"):
        if command.strip() == "switch":
            switch_window()
            return CommandResult.EXECUTED

        match = re.search(r"switch\s+(?:to\s+)?(.+)", command)
        if match:
            raw_app_name = match.group(1)
            app_name = _fuzzy_app_name(raw_app_name)
            if app_name is None:
                app_name = raw_app_name.replace(" ", "")

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

    return CommandResult.UNKNOWN
