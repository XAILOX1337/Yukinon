import keyboard
import time
import pygetwindow as gw
import psutil
from pywinauto import Desktop

from config import APP_ALIASES




def switch_window():
    """
    Имитирует нажатие Alt + Tab для переключения между окнами.
    """
    print("Действие: Переключаю окно (Alt+Tab)")
    
    keyboard.press('alt')
    
    time.sleep(0.03) 
    
    keyboard.send('tab')
    
    keyboard.release('alt')


def switch_to_app(spoken_name: str):
    """
    Ищет приложение по словарю синонимов и переключается на него.
    """
    target_exe = APP_ALIASES.get(spoken_name)
    
    if not target_exe:
        print(f"Слово '{spoken_name}' нет в словаре APP_ALIASES")
        return False

    print(f"Ищу процессы: {target_exe}")
    
    # 1. Собираем все PID для данного приложения
    target_pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and proc.info['name'].lower() == target_exe.lower():
            target_pids.append(proc.info['pid'])
            
    if not target_pids:
        print(f"Запущенные процессы {target_exe} не найдены.")
        return False
        
    print(f"Найдены PID: {target_pids}")

    # 2. Ищем окно, которое принадлежит любому из этих PID
    desktop = Desktop(backend="uia")
    windows = desktop.windows()
    
    for win in windows:
        if win.process_id() in target_pids:
            print(f"Найдено окно! Заголовок: '{win.window_text()}', PID: {win.process_id()}")
            try:
                # Пробуем активировать. Если окно фоновое (без UI), 
                # pywinauto может выдать ошибку, поэтому ловим её и идем к след. окну
                if win.is_minimized():
                    win.restore()
                win.set_focus()
                return True
            except Exception as e:
                # Это мог быть фоновый процесс, у которого нет UI или он скрыт
                print(f"Не удалось активировать PID {win.process_id()} (возможно, фоновый). Ищем дальше...")
                continue
                
    print("Окно с UI не найдено среди процессов.")
    return False


def find_app_hwnd(spoken_name: str):
    """
    Ищет окно приложения по словарю синонимов и возвращает его ID (HWND).
    Не активирует окно. Возвращает None, если окно не найдено.
    """
    target_exe = APP_ALIASES.get(spoken_name)
    
    if not target_exe:
        return None

    # 1. Собираем все PID
    target_pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and proc.info['name'].lower() == target_exe.lower():
            target_pids.append(proc.info['pid'])
            
    if not target_pids:
        return None

    # 2. Ищем видимое окно
    desktop = Desktop(backend="uia")
    windows = desktop.windows()
    
    for win in windows:
        if win.process_id() in target_pids:
            # Проверяем, что окно видимое и имеет интерфейс
            if win.is_visible() and win.handle:
                return win.handle  # Возвращаем числовой ID окна (HWND)
                
    return None