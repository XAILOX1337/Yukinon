import psutil

from config import APP_ALIASES

# Grace period for a process to exit after the terminate request
TERMINATE_TIMEOUT = 3.0  # seconds


def find_pids_by_exe(target_exe: str):
    """Collect process IDs of everything running under this executable name."""
    target_pids = []
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"] and proc.info["name"].lower() == target_exe.lower():
            target_pids.append(proc.info["pid"])
    return target_pids


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
    target_pids = find_pids_by_exe(target_exe)

    if not target_pids:
        print(f"No running processes found for {target_exe}.")
        return False

    print(f"Found PID list: {target_pids}")

    # 2. Terminate every match, then kill whatever ignored the request
    closed = 0
    for pid in target_pids:
        try:
            proc = psutil.Process(pid)
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
                print(f"Access denied for PID {pid}.")
        except psutil.AccessDenied:
            print(f"Access denied for PID {pid}.")
        except psutil.NoSuchProcess:
            # Gone before the terminate request landed
            closed += 1

    print(f"Closed {closed} of {len(target_pids)} process(es).")
    return closed > 0
