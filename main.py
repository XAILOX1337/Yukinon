import sys

from core.brain import CommandResult, process_command
from core.listener import ack_command, listen
from tts.speaker import speak

# Window titles and application names may contain emoji or other characters
# the console codepage cannot encode
sys.stdout.reconfigure(errors="replace")


def main():
    # Startup greeting
    speak("All systems online. Yukinon at your service.")

    print("Mai is listening... Say 'exit' or 'stop' to quit.")

    # Main loop
    while True:
        command = listen()

        if command:
            result = process_command(command)

            if result == CommandResult.EXIT:
                break
            elif result == CommandResult.EXECUTED:
                # Reset idle timer after a successful command
                ack_command()
            # CommandResult.UNKNOWN — leave timer running


if __name__ == "__main__":
    main()
