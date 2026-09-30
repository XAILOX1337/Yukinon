import json
import os

import pyaudio
from vosk import KaldiRecognizer, Model

from config import VOCABULARY_LIST, WAKE_WORDS


model_path = "data/models/vosk-model-en-us"
if not os.path.exists(model_path):
    print(f"ERROR: Vosk model not found at {model_path}")
    exit()

model = Model(model_path)

VOCABULARY_JSON = json.dumps(VOCABULARY_LIST, ensure_ascii=False)
command_recognizer = KaldiRecognizer(model, 16000, VOCABULARY_JSON)
free_recognizer = KaldiRecognizer(model, 16000)

mic = pyaudio.PyAudio()
stream = mic.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=8000,
)
stream.start_stream()


def _read_recognized_text(recognizer):
    while True:
        data = stream.read(4000, exception_on_overflow=False)

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")

            if text:
                print(f"You said: {text}")
                return text
            return ""


def _detect_wake_word(text):
    """Return the first wake word found in text (case-insensitive), or None."""
    text_lower = text.lower()
    for wake in WAKE_WORDS:
        if wake in text_lower:
            return wake
    return None


def _strip_wake_prefix(text, wake):
    """Remove everything up to and including the first wake word occurrence."""
    idx = text.lower().find(wake)
    if idx == -1:
        return text.strip(" .,")
    return text[idx + len(wake):].strip(" .,")


def listen():
    """Wake-word-activated command listener.

    Listens with the constrained command vocabulary. When a wake word is
    detected, returns the text after the wake word as the command.
    Utterances without a wake word are ignored. If the wake word is spoken
    alone, listens again for the follow-up command.
    """
    print("\n[Listening for wake word...]")
    while True:
        text = _read_recognized_text(command_recognizer)
        if not text:
            continue

        wake = _detect_wake_word(text)
        if not wake:
            # Ignore utterances without a wake word
            print(f"[Ignored (no wake word)]: {text}")
            continue

        # Extract command after the wake word
        command = _strip_wake_prefix(text, wake)

        if command:
            print(f"[Command]: {command}")
            return command

        # Wake word alone — wait for follow-up command
        print("[Wake word detected, listening for command...]")
        follow_up = _read_recognized_text(command_recognizer)
        if follow_up:
            print(f"[Command]: {follow_up}")
            return follow_up


def listen_free():
    print("\n[Listening free-form...]")
    return _read_recognized_text(free_recognizer)
