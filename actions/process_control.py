import psutil

from config import APP_ALIASES

# Grace period for a process to exit after the terminate request
TERMINATE_TIMEOUT = 3.0  # seconds


def _resolve_exe(spoken_name: str):
    """Alias lookup with a fallback to a raw executable name."""
    target_exe = APP_ALIASES.get(spoken_name)

    if target_exe:
        return target_exe

    if spoken_name.lower().endswith(".exe"):
        return spoken_name

    return f"{spoken_name}.exe"


def terminate_app(spoken_name: str) -> bool:
    """Fully close an application: terminate first, force kill the leftovers."""
    target_exe = _resolve_exe(spoken_name)
    print(f"Action: Terminate {target_exe}")

    # 1. Process collection by executable name
    targets = []
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"] and proc.info["name"].lower() == target_exe.lower():
            targets.append(proc)

    if not targets:
        print(f"No running processes found for {target_exe}.")
        return False

    print(f"Found PID list: {[proc.pid for proc in targets]}")

    # 2. Terminate every match, then kill whatever ignored the request
    closed = 0
    for proc in targets:
        try:
            proc.terminate()
            proc.wait(timeout=TERMINATE_TIMEOUT)
            closed += 1
        except psutil.TimeoutExpired:
            try:
                proc.kill()
                closed += 1
            except psutil.NoSuchProcess:
                # Gone before the kill request landed
                closed += 1
            except psutil.AccessDenied:
                print(f"Access denied for PID {proc.pid}.")
        except psutil.AccessDenied:
            print(f"Access denied for PID {proc.pid}.")
        except psutil.NoSuchProcess:
            # Gone before the terminate request landed
            closed += 1

    print(f"Closed {closed} of {len(targets)} process(es).")
    return True
