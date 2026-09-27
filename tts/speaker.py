import asyncio
import os

import edge_tts
import pygame

pygame.mixer.init()


async def _generate_and_save(text: str, file_path: str):
    # Voice selection
    communicate = edge_tts.Communicate(text, rate="+35%", voice="en-US-ChristopherNeural")
    await communicate.save(file_path)


def speak(text: str):
    print(f"Yukinon: {text}")

    file_path = "data/temp/voice.mp3"

    # Speech generation
    asyncio.run(_generate_and_save(text, file_path))

    # Audio playback
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    # Playback completion wait
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # Temporary file cleanup
    pygame.mixer.music.unload()
    if os.path.exists(file_path):
        os.remove(file_path)
