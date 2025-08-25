import platform
from datetime import datetime, timezone

def base_system():
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "arch": platform.machine(),
        "checked_at": datetime.now(timezone.utc).isoformat()
    }

def any_file_exists(paths):
    from pathlib import Path
    return any(Path(p).exists() for p in paths)
