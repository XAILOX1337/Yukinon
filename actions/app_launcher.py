import difflib
import os

import win32com.client

from actions.window_control import focus_app_by_exe
from config import APP_ALIASES

# Taskbar pins are plain .lnk shortcuts; this folder is the source of truth
PINNED_TASKBAR_DIR = os.path.join(
    os.environ["APPDATA"],
    "Microsoft",
    "Internet Explorer",
    "Quick Launch",
    "User Pinned",
    "TaskBar",
)


def _pinned_shortcuts():
    """List taskbar pins as (name, path, target exe) tuples."""
    if not os.path.isdir(PINNED_TASKBAR_DIR):
        print(f"Pinned taskbar folder not found: {PINNED_TASKBAR_DIR}")
        return []

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcuts = []

    for entry in sorted(os.listdir(PINNED_TASKBAR_DIR)):
        if not entry.lower().endswith(".lnk"):
            continue

        path = os.path.join(PINNED_TASKBAR_DIR, entry)
        try:
            target = shell.CreateShortcut(path).TargetPath
        except Exception:
            # Special shell shortcuts (File Explorer) report an empty target
            target = ""

        shortcuts.append((entry[:-4], path, os.path.basename(target)))

    return shortcuts


def _find_shortcut_by_exe(target_exe: str, shortcuts):
    """Return the pin whose executable matches, if there is one."""
    for shortcut in shortcuts:
        if shortcut[2] and shortcut[2].lower() == target_exe.lower():
            return shortcut
    return None


def _resolve(spoken_name: str):
    """Resolve the spoken name into a (shortcut, executable) pair."""
    glued_name = spoken_name.strip(" .").replace(" ", "").lower()

    if not glued_name:
        return None, None

    shortcuts = _pinned_shortcuts()
    pinned_names = [name.replace(" ", "").lower() for name, _, _ in shortcuts]
    aliases = {key.replace(" ", ""): value for key, value in APP_ALIASES.items()}
    alias_exe = aliases.get(glued_name)

    # 1. Exact pin name: "discord" -> Discord.lnk
    if glued_name in pinned_names:
        shortcut = shortcuts[pinned_names.index(glued_name)]
        # The alias dictionary knows the real process name, pins may point at launchers
        return shortcut, alias_exe or shortcut[2]

    # 2. Exact alias: "vs code" -> Code.exe, the pin is looked up by executable
    if alias_exe:
        return _find_shortcut_by_exe(alias_exe, shortcuts), alias_exe

    # 3. The spoken name is part of a pin: "lightroom" -> "Adobe Lightroom Classic.lnk"
    for index, name in enumerate(pinned_names):
        if glued_name in name:
            shortcut = shortcuts[index]
            return shortcut, shortcut[2]

    # 4. Fuzzy fallback for misheard names: pins first, alias dictionary second
    matches = difflib.get_close_matches(glued_name, pinned_names, n=1, cutoff=0.6)
    if matches:
        shortcut = shortcuts[pinned_names.index(matches[0])]
        return shortcut, shortcut[2]

    matches = difflib.get_close_matches(glued_name, list(aliases), n=1, cutoff=0.6)
    if matches:
        alias_exe = aliases[matches[0]]
        return _find_shortcut_by_exe(alias_exe, shortcuts), alias_exe

    return None, None


def open_app(spoken_name: str) -> bool:
    """Launch a pinned application, or focus it when it is already running."""
    shortcut, target_exe = _resolve(spoken_name)

    if not shortcut and not target_exe:
        print(f"No pin or alias found for: {spoken_name}")
        return False

    # 1. A running application is brought to the front instead of relaunched
    if target_exe and focus_app_by_exe(target_exe):
        return True

    # 2. Taskbar pin: start the .lnk itself, keeping arguments and shell targets
    if shortcut:
        print(f"Action: Open '{shortcut[0]}'")
        try:
            os.startfile(shortcut[1])
            return True
        except OSError as error:
            print(f"Could not start '{shortcut[0]}': {error}")

    # 3. Executable without a pin: "task manager", "explorer"
    if target_exe:
        print(f"Action: Open {target_exe}")
        try:
            os.startfile(target_exe)
            return True
        except OSError as error:
            print(f"Could not start {target_exe}: {error}")

    return False
