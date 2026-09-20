from tts.speaker import speak

def process_command(command: str) -> bool:
    """
    Обрабатывает команду.
    Возвращает True, если нужно завершить работу программы.
    """
    command = command.lower()
    
    if "выход" in command or "стоп" in command:
        return True
        
    elif "привет" in command:
        speak("Здравствуйте, сэр!")
        
    elif "как дела" in command:
        speak("Все системы работают в штатном режиме. А как ваши?")
        
    else:
        speak("Я вас не совсем понял. Повторите, пожалуйста.")
        
    return False