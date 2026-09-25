import re
import difflib

from tts.speaker import speak
from actions.window_control import switch_window, switch_to_app, find_app_hwnd
from actions.media_control import play_pause, next_track, prev_track, send_media_command_to_background
from config import APP_ALIASES

def process_command(command: str) -> bool:
    command = command.lower()
    
    if "выход" in command or "стоп" in command:
        return True
        
    elif "привет" in command:
        speak("Здравствуйте, сэр!")
        
    elif "как дела" in command:
        speak("Все системы работают в штатном режиме. А как ваши?")
        
    # --- блок пауза/некст ---
    
    MEDIA_ACTIONS = {
        "play_pause": (["пауза", "плей", "поставить", "продолжить"], play_pause),
        "next": (["следующий", "следущую", "некст"], next_track),
        "prev": (["предыдущий", "предыдущую", "прев"], prev_track)
    }
    
    all_media_words = [word for words, _ in MEDIA_ACTIONS.values() for word in words]
    
    if any(word in command for word in all_media_words):
        
        # 1. Определение действия и сразу получение нужной функции
        action_key = "play_pause" 
        for key, (words, func) in MEDIA_ACTIONS.items():
            if any(w in command for w in words):
                action_key = key
                break
                
        # 2. Вырезаем все медиа-слова и мусор, чтобы осталось только название приложения
        stop_words = all_media_words + ["трек", "песня", "музыку", "на", "в"]
        app_part = command
        for w in stop_words:
            app_part = app_part.replace(w, "")
            
        app_part = app_part.replace("  ", " ").strip()
        
        # 3. Если осталась пустота — команда для активного окна
        if not app_part:
            print("Команда для активного окна")
            dict(MEDIA_ACTIONS)[action_key][1]() 
            return False
            
        # 4. Если осталось слово — это фоновая команда (например "пауза спотифай")
        glued_app = app_part.replace(" ", "")
        matches = difflib.get_close_matches(glued_app, list(APP_ALIASES.keys()), n=1, cutoff=0.6)
        
        if matches:
            app_name = matches[0]
            print(f"[Фазз-поиск] Фоновая команда для: {app_name}")
            
            hwnd = find_app_hwnd(app_name)
            if hwnd:
                send_media_command_to_background(hwnd, action_key)
            else:
                speak(f"Приложение {app_name} не запущено.")
        else:
            print(f"Не распознал приложение в фразе: {app_part}")
            
        return False
        
    # --- БЛОК АЛЬТТАБА ---
    elif command.startswith("свитч") or command.startswith("свишь"):
        cmd_word = "свитч" if command.startswith("свитч") else "свишь"
        
        if command.strip() == cmd_word:
            switch_window()
            return False
            
        match = re.search(rf'{cmd_word}\s+(.+)', command)
        if match:
            raw_app_name = match.group(1)
            glued_name = raw_app_name.replace(" ", "")
            
            known_apps = list(APP_ALIASES.keys())
            matches = difflib.get_close_matches(glued_name, known_apps, n=1, cutoff=0.6)
            
            if matches:
                app_name = matches[0]
                print(f"[Фазз-поиск] Услышал '{raw_app_name}', исправил на '{app_name}'")
            else:
                app_name = glued_name 
                
            success = switch_to_app(app_name)
            
            if not success:
                speak(f"Не нашел запущенное приложение {app_name}. Проверьте словарь синонимов.")
        else:
            switch_window()
            
    else:
        speak("Я вас не совсем понял. Повторите, пожалуйста.")
        
    return False