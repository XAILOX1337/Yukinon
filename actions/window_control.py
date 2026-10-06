import time

import keyboard
import win32api
import win32con
import win32gui
import win32process

from actions.process_control import find_pids_by_exe
from config import APP_ALIASES


def switch_window():
    """Alt + Tab window switch simulation."""
    print("Action: Switching window (Alt+Tab)")

    keyboard.press("alt")
    time.sleep(0.03)
    keyboard.send("tab")
    keyboard.release("alt")


# Window lookup helpers shared with web_control


def find_windows_by_pids(target_pids):
    """Window handles of visible top-level windows for the given process IDs.

    Win32 enumeration instead of a UIA scan: ~0.2 ms instead of ~400 ms.
    Handles come back in z-order, topmost first.
    """
    wanted = set(target_pids)
    found = []

    def _collect(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid in wanted:
                found.append(hwnd)

    win32gui.EnumWindows(_collect, None)
    return found


def _wait_foreground(hwnd: int, timeout: float) -> bool:
    """Foreground switches are not synchronous — poll briefly before giving up."""
    deadline = time.perf_counter() + timeout
    while True:
        if win32gui.GetForegroundWindow() == hwnd:
            return True
        if time.perf_counter() >= deadline:
            return False
        time.sleep(0.02)


def focus_hwnd(hwnd: int) -> bool:
    """Restore a window and bring it to the front, verifying the result."""
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

    # 1. Plain request — works when this process holds the foreground rights
    granted = True
    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        granted = False
    if granted and _wait_foreground(hwnd, 0.15):
        return True

    # 2. Foreground lock: join the window's input queue briefly
    attached = True
    try:
        target_tid, _ = win32process.GetWindowThreadProcessId(hwnd)
        current_tid = win32api.GetCurrentThreadId()
        win32process.AttachThreadInput(current_tid, target_tid, True)
        try:
            win32gui.BringWindowToTop(hwnd)
            win32gui.SetForegroundWindow(hwnd)
        finally:
            win32process.AttachThreadInput(current_tid, target_tid, False)
    except Exception:
        attached = False
    if attached and _wait_foreground(hwnd, 0.15):
        return True

    # 3. Last resort: an Alt press releases the lock for one request
    try:
        keyboard.press("alt")
        try:
            win32gui.SetForegroundWindow(hwnd)
        finally:
            keyboard.release("alt")
    except Exception:
        pass
    return _wait_foreground(hwnd, 0.15)


def switch_to_app(spoken_name: str):
    """Alias lookup followed by a switch to the matching application."""
    target_exe = APP_ALIASES.get(spoken_name)

    if not target_exe:
        print(f"Word '{spoken_name}' is missing from APP_ALIASES")
        return False

    return focus_app_by_exe(target_exe)


def focus_app_by_exe(target_exe: str):
    """Switch to a running application identified by its executable name."""
    print(f"Process search: {target_exe}")

    # 1. Process ID collection
    target_pids = find_pids_by_exe(target_exe)

    if not target_pids:
        print(f"No running processes found for {target_exe}.")
        return False

    print(f"Found PID list: {target_pids}")

    # 2. Window search by process ID, topmost first
    for hwnd in find_windows_by_pids(target_pids):
        print(f"Window found. Handle: {hwnd}, Title: '{win32gui.GetWindowText(hwnd)}'")

        if focus_hwnd(hwnd):
            return True

        print(f"Activation failed for handle {hwnd}. Continuing search...")

    print("No visible window found among the target processes.")
    return False


def find_app_hwnd(spoken_name: str):
    """Return the window handle for an application without activating it."""
    target_exe = APP_ALIASES.get(spoken_name)

    if not target_exe:
        return None

    # 1. Process ID collection
    target_pids = find_pids_by_exe(target_exe)

    if not target_pids:
        return None

    # 2. Visible window search
    windows = find_windows_by_pids(target_pids)
    return windows[0] if windows else None


# Window state control


def minimize_active():
    """Minimize the currently focused window."""
    print("Action: Minimize active window")
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return False
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    return True


def toggle_maximize():
    """Maximize or restore the currently focused window."""
    print("Action: Toggle maximize")
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return False

    show_cmd = win32gui.GetWindowPlacement(hwnd)[1]
    if show_cmd == win32con.SW_SHOWMAXIMIZED:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    else:
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
    return True


def minimize_all():
    """Minimize all windows."""
    print("Action: Minimize all windows")
    keyboard.send("win+m")
    return True


def restore_all():
    """Undo 'minimize all'."""
    print("Action: Restore all windows")
    keyboard.send("win+shift+m")
    return True


def toggle_show_desktop():
    """Toggle the 'show desktop' state."""
    print("Action: Toggle show desktop")
    keyboard.send("win+d")
    return True
