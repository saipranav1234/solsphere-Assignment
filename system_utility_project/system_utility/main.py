
import platform
from system_utility.checks import macos, linux, windows

def run_checks():
    system = platform.system()
    if system == "Darwin":
        return macos.collect()
    elif system == "Linux":
        return linux.collect()
    elif system == "Windows":
        return windows.collect()
    else:
        raise NotImplementedError(f"Unsupported system: {system}")


def get_system_report():
    """
    Returns system info dictionary for daemon reporting
    """
    return run_checks()

if __name__ == "__main__":
    results = run_checks()
    from pprint import pprint
    pprint(results)
