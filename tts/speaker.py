import asyncio
import hashlib
import os

import edge_tts
import pygame

pygame.mixer.init()

VOICE = "en-US-JennyNeural"
RATE = "+35%"
# Repeated replies come from the cache and skip the network round trip
CACHE_DIR = os.path.join("data", "temp", "voice_cache")


async def _generate_and_save(text: str, file_path: str):
    # Voice selection
    communicate = edge_tts.Communicate(text, rate=RATE, voice=VOICE)
    await communicate.save(file_path)


def _cached_path(text: str) -> str:
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, f"{digest}.mp3")


def speak(text: str):
    print(f"Yukinon: {text}")
    file_path = _cached_path(text)

    # Generation and playback must never crash the assistant:
    # no network or no audio device only skips the spoken reply
    try:
        if not os.path.exists(file_path):
            os.makedirs(CACHE_DIR, exist_ok=True)
            asyncio.run(_generate_and_save(text, file_path))

        # Audio playback
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        # Playback completion wait
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(30)

        pygame.mixer.music.unload()
    except Exception as error:
        print(f"TTS unavailable: {error}")
