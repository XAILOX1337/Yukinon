import keyboard
import psutil

from actions.window_control import find_windows_by_pids, focus_hwnd

# Browser process names are not a site list; they identify tab-capable windows
BROWSER_EXE_NAMES = {
    "chrome.exe",
    "firefox.exe",
    "zen.exe",
    "msedge.exe",
    "brave.exe",
    "opera.exe",
    "vivaldi.exe",
}


def _browser_pids():
    """Process IDs of every running browser window host."""
    pids = set()
    for proc in psutil.process_iter(["pid", "name"]):
        name = proc.info.get("name")
        if name and name.lower() in BROWSER_EXE_NAMES:
            pids.add(proc.info["pid"])
    return pids


def focus_browser() -> bool:
    """Focus the topmost visible browser window."""
    pids = _browser_pids()
    if not pids:
        return False

    for hwnd in find_windows_by_pids(pids):
        if focus_hwnd(hwnd):
            return True
    return False


def next_tab():
    """Switch to the next browser tab."""
    if focus_browser():
        print("Action: Next browser tab")
        keyboard.send("ctrl+tab")


def previous_tab():
    """Switch to the previous browser tab."""
    if focus_browser():
        print("Action: Previous browser tab")
        keyboard.send("ctrl+shift+tab")


def new_tab():
    """Open a new browser tab."""
    if focus_browser():
        print("Action: New browser tab")
        keyboard.send("ctrl+t")


def close_current_tab():
    """Close the current browser tab."""
    if focus_browser():
        print("Action: Close current browser tab")
        keyboard.send("ctrl+w")


def reopen_tab():
    """Reopen the last closed browser tab."""
    if focus_browser():
        print("Action: Reopen browser tab")
        keyboard.send("ctrl+shift+t")
