import json
import os

import pyaudio
from vosk import KaldiRecognizer, Model

from config import VOCABULARY_LIST


model_path = "data/models/vosk-model-en-us"
if not os.path.exists(model_path):
    print(f"ERROR: Vosk model not found at {model_path}")
    exit()

model = Model(model_path)

VOCABULARY_JSON = json.dumps(VOCABULARY_LIST, ensure_ascii=False)
recognizer = KaldiRecognizer(model, 16000, VOCABULARY_JSON)

mic = pyaudio.PyAudio()
stream = mic.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=8000,
)
stream.start_stream()


def listen():
    print("\n[Listening...]")
    while True:
        data = stream.read(4000, exception_on_overflow=False)

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")

            if text:
                print(f"You said: {text}")
                return text
            return ""
