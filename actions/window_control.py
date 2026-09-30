import time

import keyboard
import psutil
import pygetwindow as gw
import win32con
import win32gui
from pywinauto import Desktop

from config import APP_ALIASES


def switch_window():
    """Alt + Tab window switch simulation."""
    print("Action: Switching window (Alt+Tab)")

    keyboard.press("alt")
    time.sleep(0.03)
    keyboard.send("tab")
    keyboard.release("alt")


def switch_to_app(spoken_name: str):
    """Alias lookup followed by a switch to the matching application."""
    target_exe = APP_ALIASES.get(spoken_name)

    if not target_exe:
        print(f"Word '{spoken_name}' is missing from APP_ALIASES")
        return False

    print(f"Process search: {target_exe}")

    # 1. Process ID collection
    target_pids = []
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"] and proc.info["name"].lower() == target_exe.lower():
            target_pids.append(proc.info["pid"])

    if not target_pids:
        print(f"No running processes found for {target_exe}.")
        return False

    print(f"Found PID list: {target_pids}")

    # 2. Window search by process ID
    desktop = Desktop(backend="uia")
    windows = desktop.windows()

    for win in windows:
        if win.process_id() in target_pids:
            print(f"Window found. Title: '{win.window_text()}', PID: {win.process_id()}")
            try:
                if win.is_minimized():
                    win.restore()
                win.set_focus()
                return True
            except Exception:
                # Background or hidden windows can fail activation
                print(f"Activation failed for PID {win.process_id()}. Continuing search...")
                continue

    print("No UI window found among the target processes.")
    return False


def find_app_hwnd(spoken_name: str):
    """Return the window handle for an application without activating it."""
    target_exe = APP_ALIASES.get(spoken_name)

    if not target_exe:
        return None

    # 1. Process ID collection
    target_pids = []
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"] and proc.info["name"].lower() == target_exe.lower():
            target_pids.append(proc.info["pid"])

    if not target_pids:
        return None

    # 2. Visible window search
    desktop = Desktop(backend="uia")
    windows = desktop.windows()

    for win in windows:
        if win.process_id() in target_pids:
            # Visibility and interface check
            if win.is_visible() and win.handle:
                return win.handle  # Numeric window handle

    return None


# Window state control


def minimize_active():
    """Minimize the currently focused window."""
    print("Action: Minimize active window")
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return False
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    time.sleep(0.05)
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
    time.sleep(0.05)
    return True


def minimize_all():
    """Minimize all windows."""
    print("Action: Minimize all windows")
    keyboard.send("win+m")
    time.sleep(0.05)
    return True


def restore_all():
    """Undo 'minimize all'."""
    print("Action: Restore all windows")
    keyboard.send("win+shift+m")
    time.sleep(0.05)
    return True


def toggle_show_desktop():
    """Toggle the 'show desktop' state."""
    print("Action: Toggle show desktop")
    keyboard.send("win+d")
    time.sleep(0.05)
    return True
