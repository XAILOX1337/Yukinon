import re
import socket
import time
import webbrowser
from urllib.parse import quote

import keyboard
import psutil
from pywinauto import Desktop

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

# Gecko-based browsers are closed through the address bar, not tab search
GECKO_BROWSERS = {
    "firefox.exe",
    "zen.exe",
}

SEARCH_URL = "https://www.google.com/search?q={query}"


def _browser_processes():
    processes = {}
    for proc in psutil.process_iter(["pid", "name"]):
        name = proc.info.get("name")
        if name and name.lower() in BROWSER_EXE_NAMES:
            processes[proc.info["pid"]] = name.lower()
    return processes


def _focus_browser_window():
    """Focus the first visible browser window and return its process name."""
    processes = _browser_processes()
    if not processes:
        return None

    desktop = Desktop(backend="uia")
    for win in desktop.windows():
        process_name = processes.get(win.process_id())
        if process_name and win.is_visible():
            try:
                if win.is_minimized():
                    win.restore()
                win.set_focus()
                return process_name
            except Exception:
                continue
    return None


def focus_browser():
    """Focus the first visible browser window."""
    return _focus_browser_window() is not None


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


def _clean_site_query(query: str):
    query = query.strip().lower()
    query = re.sub(r"^https?://", "", query)
    query = re.sub(r"^www\.", "", query)
    query = re.sub(r"\b(open|close|site|website|go|to|the)\b", " ", query)
    query = re.sub(r"[^a-z0-9.\s-]", " ", query)
    query = re.sub(r"\s+", " ", query).strip(" .-")
    return query


def _domain_candidates(query: str):
    if not query:
        return []

    if "." in query:
        return [query]

    if " " in query:
        compact = query.replace(" ", "")
        hyphen = query.replace(" ", "-")
        return [
            f"{compact}.com",
            f"{hyphen}.com",
            f"{compact}.net",
            f"{hyphen}.net",
        ]

    return [f"{query}.com", f"{query}.net", f"{query}.org"]


def _resolves(domain: str):
    previous_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(1.0)
    try:
        socket.gethostbyname(domain)
        return True
    except OSError:
        return False
    finally:
        socket.setdefaulttimeout(previous_timeout)


def _site_url(query: str):
    candidates = _domain_candidates(query)
    for domain in candidates:
        if _resolves(domain):
            return f"https://{domain}"
    return SEARCH_URL.format(query=quote(query))


def open_site(query: str):
    """Open a site inferred from free-form speech."""
    query = _clean_site_query(query)
    if not query:
        return False

    url = _site_url(query)
    print(f"Action: Open site '{query}' -> {url}")
    webbrowser.open_new_tab(url)
    return True


def _close_through_tab_search(query: str):
    keyboard.send("ctrl+shift+a")
    time.sleep(0.4)
    keyboard.write(query.replace(" ", ""), delay=0.01)
    time.sleep(0.2)
    keyboard.send("enter")
    time.sleep(0.3)
    keyboard.send("ctrl+w")


def _close_through_address_bar(query: str):
    keyboard.send("ctrl+l")
    time.sleep(0.2)
    keyboard.write(f"% {query.replace(' ', '')}", delay=0.01)
    time.sleep(0.3)
    keyboard.send("down")
    time.sleep(0.1)
    keyboard.send("enter")
    time.sleep(0.3)
    keyboard.send("ctrl+w")


def close_site(query: str):
    """Close a matching open tab without any hardcoded site list."""
    query = _clean_site_query(query)
    browser = _focus_browser_window()
    if not query or not browser:
        return False

    print(f"Action: Close site '{query}' in {browser}")
    if browser in GECKO_BROWSERS:
        _close_through_address_bar(query)
    else:
        _close_through_tab_search(query)
    return True
