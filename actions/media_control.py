import keyboard
import time
import win32api
import win32gui
import win32process

# Коды системных сообщений Windows
WM_APPCOMMAND = 0x0319

# Коды медиа-команд Windows API
APPCOMMAND_MEDIA_PLAY_PAUSE = 14
APPCOMMAND_MEDIA_NEXTTRACK = 11
APPCOMMAND_MEDIA_PREVIOUSTRACK = 12

def play_pause():
    """Обычная пауза для активного окна"""
    print("Действие: Play/Pause (активное окно)")
    keyboard.send('play/pause')
    time.sleep(0.1)

def next_track():
    """Обычный некст трек для активного окна"""
    print("Действие: Next Track (активное окно)")
    keyboard.send('next track')
    time.sleep(0.1)

def prev_track():
    """Обычный прев трек для активного окна"""
    print("Действие: Previous Track (активное окно)")
    keyboard.send('previous track')
    time.sleep(0.1)

# --- ФОНОВЫЕ ФУНКЦИИ ---

def send_media_command_to_background(hwnd: int, action: str):
    """
    Отправляет медиа-команду напрямую в фоновое окно по его дескриптору (HWND).
    """
    print(f"Отправляю фоновую команду '{action}' в окно HWND: {hwnd}")
    
    if action == "play_pause":
        cmd = APPCOMMAND_MEDIA_PLAY_PAUSE
    elif action == "next":
        cmd = APPCOMMAND_MEDIA_NEXTTRACK
    elif action == "prev":
        cmd = APPCOMMAND_MEDIA_PREVIOUSTRACK
    else:
        return
        
    # Структура сообщения: WM_APPCOMMAND, wParam (HWND окна), lParam (Код команды << 16)
    # Cmd сдвигается на 16 бит влево, так того требует WinAPI
    win32api.PostMessage(hwnd, WM_APPCOMMAND, hwnd, cmd << 16)