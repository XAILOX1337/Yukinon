import asyncio
import edge_tts
import pygame
import os

pygame.mixer.init()

async def _generate_and_save(text: str, file_path: str):
    # можно поменять на ru-RU-SvetlanaNeural
    communicate = edge_tts.Communicate(text, rate="+35%", voice="ru-RU-DmitryNeural")
    await communicate.save(file_path)

def speak(text: str):
    print(f"Джарвис: {text}")
    
    file_path = "data/temp/voice.mp3"
    
    # запуск асинхронной генерации речи
    asyncio.run(_generate_and_save(text, file_path))
    
    # проигрывание аудиофайла
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    
    # Ожидание пока аудио не закончится проигрываться
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
        
    # Удаление временного файла
    pygame.mixer.music.unload()
    if os.path.exists(file_path):
        os.remove(file_path)