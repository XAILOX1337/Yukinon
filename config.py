WAKE_WORDS = ("mai", "jarvis")
IDLE_TIMEOUT = 5 * 60  # seconds; switches to sleep mode after this many seconds without a successful command

VOCABULARY_LIST = [
    "mai", "jarvis",
    "exit", "stop",
    "hello", "hi", "how are you",
    "switch",
    "pause", "play", "resume", "continue",
    "next", "previous", "prev", "back",
    "track", "song", "music",
    "open", "close", "site", "tab", "new", "reopen", "go", "to",
    "next tab", "previous tab", "new tab", "close tab", "reopen tab", "switch tab",
    "open site", "close site", "go to",
    "minimize", "maximize", "fullscreen", "full screen", "restore", "show", "desktop", "window", "all",
    "minimize window", "maximize window", "minimize all", "restore all", "show desktop",
    "terminate", "kill", "shut down", "shutdown",
    "spotify", "chrome", "google", "vs code", "code", "visual studio code",
    "telegram", "tg", "discord", "notepad", "hap", "firefox", "zen", "browser",
    "steam", "explorer", "task manager", "obsidian", "youtube"
]

APP_ALIASES = {
    "spotify": "spotify.exe",
    "chrome": "chrome.exe",
    "google": "chrome.exe",
    "vs code": "Code.exe",
    "code": "Code.exe",
    "visual studio code": "Code.exe",
    "telegram": "Telegram.exe",
    "tg": "Telegram.exe",
    "discord": "Discord.exe",
    "notepad": "Notepad.exe",
    "hap": "Happ.exe",
    "firefox": "firefox.exe",
    "browser": "zen.exe",
    "zen": "zen.exe",
    "steam": "steamwebhelper.exe",
    "explorer": "explorer.exe",
    "task manager": "taskmgr.exe",
    "obsidian": "obsidian.exe",
}
