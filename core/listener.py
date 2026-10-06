import json
import os
import threading

import pyaudio
from vosk import KaldiRecognizer, Model

from config import IDLE_TIMEOUT, VOCABULARY_LIST, WAKE_WORDS


model_path = "data/models/vosk-model-en-us"
if not os.path.exists(model_path):
    print(f"ERROR: Vosk model not found at {model_path}")
    exit()

model = Model(model_path)

VOCABULARY_JSON = json.dumps(VOCABULARY_LIST, ensure_ascii=False)
command_recognizer = KaldiRecognizer(model, 16000, VOCABULARY_JSON)

# 100 ms device batches: the recognizer gets fed steadily instead of
# 500 ms bursts, which shaves the endpoint detection delay
mic = pyaudio.PyAudio()
stream = mic.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=1600,
)
stream.start_stream()


# Idle / sleep state machine

_state = "ACTIVE"  # "ACTIVE" or "SLEEP"
_idle_timer = None


def _enter_sleep_mode():
    global _state
    if _state != "SLEEP":
        print("\n[Idle timeout. Entering sleep mode.]")
        print("[Say 'Jarvis' or 'Yukinon' to wake up.]")
        _state = "SLEEP"


def _exit_sleep_mode():
    global _state
    _state = "ACTIVE"
    _start_idle_timer()
    print("[Active mode: listening for commands.]")


def _start_idle_timer():
    """Start (or restart) the idle timer that flips state to SLEEP."""
    global _idle_timer
    if _idle_timer:
        _idle_timer.cancel()
    _idle_timer = threading.Timer(IDLE_TIMEOUT, _enter_sleep_mode)
    _idle_timer.daemon = True
    _idle_timer.start()


def ack_command():
    """Reset the idle timer after a successful command execution."""
    if _state == "ACTIVE":
        _start_idle_timer()


# Recognizer helpers


def _read_until_result(recognizer, state_guard):
    """Read audio and feed to the recognizer.

    Returns:
        str: the recognized text (may be empty if Vosk returned a silent
             final result).
        None: if state_guard() returned False (state changed during read).
    """
    # 1600 frames = 100 ms of audio per read: the utterance endpoint reacts
    # twice as fast as the old 4000-frame (250 ms) chunks
    while state_guard():
        data = stream.read(1600, exception_on_overflow=False)

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")
            if text:
                print(f"You said: {text}")
            return text
    return None


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
    """Idle-aware command listener.

    Active mode: listens for any command (no wake word required).
    Sleep mode: requires a wake word ('Yukinon' or 'Jarvis') to wake up.
    Switches to sleep mode after IDLE_TIMEOUT seconds with no successful
    command. Call ack_command(True) after a command is executed to reset
    the idle timer.
    """
    # Initialize timer on first call
    if _state == "ACTIVE" and _idle_timer is None:
        _start_idle_timer()

    while True:
        if _state == "SLEEP":
            text = _read_until_result(
                command_recognizer, lambda: _state == "SLEEP"
            )

            # State changed (should not happen in SLEEP, but defensive)
            if text is None:
                continue

            # Noise in sleep mode — keep listening
            if not text:
                continue

            wake = _detect_wake_word(text)
            if not wake:
                # Ignore utterances without a wake word in sleep mode
                print(f"[Ignored (sleep mode, no wake word)]: {text}")
                continue

            # Extract command after the wake word
            command = _strip_wake_prefix(text, wake)
            print(f"[Wake word detected: {wake}]")
            _exit_sleep_mode()

            if command:
                # Wake word + command in one utterance
                return command
            # Wake word alone — continue loop (now in ACTIVE mode)
            continue

        # ACTIVE mode: listen for any command
        text = _read_until_result(
            command_recognizer, lambda: _state == "ACTIVE"
        )

        # State changed (fell asleep during read) — re-evaluate at top
        if text is None:
            continue

        # Noise in active mode — keep listening
        if not text:
            continue

        return text
