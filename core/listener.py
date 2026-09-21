import json
import os
import pyaudio
from vosk import Model, KaldiRecognizer

model_path = "data/models/vosk-model-small-ru"
if not os.path.exists(model_path):
    print(f"ОШИБКА: Модель Vosk не найдена по пути {model_path}")
    exit()

model = Model(model_path)

from config import VOCABULARY_LIST


VOCABULARY_JSON = json.dumps(VOCABULARY_LIST, ensure_ascii=False)

recognizer = KaldiRecognizer(model, 16000, VOCABULARY_JSON)

mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, 
                  input=True, frames_per_buffer=8000)
stream.start_stream()

def listen():
    print("\n[Слушаю...]")
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")
            
            if text:
                print(f"Вы сказали: {text}")
                return text
            return ""