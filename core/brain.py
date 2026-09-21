import re
from tts.speaker import speak
from actions.window_control import switch_window, switch_to_app

def process_command(command: str) -> bool:
    command = command.lower()
    
    if "выход" in command or "стоп" in command:
        return True
        
    elif "привет" in command:
        speak("Здравствуйте, сэр!")
        
    elif "как дела" in command:
        speak("Все системы работают в штатном режиме. А как ваши?")
        
    elif command.startswith("свитч"):
        if command.strip() == "свитч":
            switch_window()
            return False
            
        # В brain.py
        match = re.search(r'свитч\s+(.+)', command)
        if match:
            app_name = match.group(1).replace(" ", "") # Склеиваем "с п о т и ф а й" в "спотифай" тк так он лучше распазнает, хз почему
            success = switch_to_app(app_name)
            
            if not success:
                
                speak(f"Не нашел запущенное приложение {app_name}. Проверьте словарь синонимов.")
        else:
            switch_window()
            
    else:
        speak("Я вас не совсем понял. Повторите, пожалуйста.")
        
    return False