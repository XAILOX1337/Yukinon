import asyncio
from tts.speaker import speak
from core.listener import listen
from core.brain import process_command

def main():
    # Приветствие при запуске
    # speak("Системы запущены. Джарвис к вашим услугам, сэр.")
    
    print("Джарвис слушает... (Скажите 'выход' или 'стоп' для завершения)")
    
    # Главный цикл
    while True:
        
        command = listen()
        
        if command:
            
            should_exit = process_command(command)
            
            
            if should_exit:
                # speak("Выключаюсь. До встречи, сэр.")
                break

if __name__ == "__main__":
    main()