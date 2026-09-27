from tts.speaker import speak
from core.listener import listen
from core.brain import process_command


def main():
    # Startup greeting
    # speak("All systems online. Yukinon at your service.")

    print("Yukinon is listening... Say 'exit' or 'stop' to quit.")

    # Main loop
    while True:
        command = listen()

        if command:
            should_exit = process_command(command)

            if should_exit:
                # speak("Shutting down. Goodbye.")
                break


if __name__ == "__main__":
    main()
