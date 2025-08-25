import re
from datetime import datetime, timezone
from pathlib import Path
from .common import base_system, any_file_exists
from ..utils import run_cmd, parse_first_int_from_line

def machine_id():
    out, _, _ = run_cmd(["/usr/sbin/system_profiler", "SPHardwareDataType"])
    m = re.search(r"Hardware UUID:\s*([A-F0-9\-]+)", out)
    return m.group(1) if m else "DARWIN-UNKNOWN"

def disk_encryption():
    out, _, _ = run_cmd(["/usr/bin/fdesetup", "status"])
    status = None
    if "FileVault is On" in out: status = True
    elif "FileVault is Off" in out: status = False
    return {"supported": True, "status": status, "raw": out}

def os_update_status():
    out, _, _ = run_cmd(["/usr/sbin/softwareupdate", "-l"])
    up_to_date = ("No new software available" in out) or ("No updates available" in out)
    return {"supported": True, "up_to_date": up_to_date, "raw": out}

def antivirus_status():
    common_apps = ["Avast", "Norton", "McAfee", "Kaspersky", "Bitdefender",
                   "Sophos", "Malwarebytes", "ESET", "Trend Micro", "Intego"]
    found = []
    apps_dir = Path("/Applications")
    if apps_dir.exists():
        for app in apps_dir.iterdir():
            for name in common_apps:
                if name.lower() in app.name.lower():
                    found.append(app.name)
    apple_protection = {
        "xprotect": any_file_exists([
            "/Library/Apple/System/Library/CoreServices/XProtect.app",
            "/System/Library/CoreServices/XProtect.bundle"]),
        "mrt": Path("/System/Library/CoreServices/MRT.app").exists(),
        "gatekeeper": True,
    }
    present = bool(found) or any(apple_protection.values())
    return {"supported": True, "present": present, "third_party": found, "apple": apple_protection}

def inactivity_sleep():
    out, _, _ = run_cmd(["/usr/bin/pmset", "-g"])
    sleep_vals, display_vals = [], []
    for line in out.splitlines():
        if " sleep " in f" {line} ":
            v = parse_first_int_from_line(line)
            if v is not None: sleep_vals.append(v)
        if " displaysleep " in f" {line} ":
            v = parse_first_int_from_line(line)
            if v is not None: display_vals.append(v)
    def ok(vals): return all(v <= 10 for v in vals) if vals else None
    s_ok = ok(sleep_vals)
    d_ok = ok(display_vals)
    compliant = False if s_ok is False or d_ok is False else True
    return {"supported": True, "compliant": compliant,
            "sleep_values_minutes": sleep_vals or None,
            "display_sleep_values_minutes": display_vals or None,
            "raw": out}

def collect():
    base = base_system()
    return {
        **base,
        "machine_id": machine_id(),
        "checks": {
            "disk_encryption": disk_encryption(),
            "os_update": os_update_status(),
            "antivirus": antivirus_status(),
            "inactivity_sleep": inactivity_sleep(),
        },
        "checked_at": datetime.now(timezone.utc).isoformat()
    }
