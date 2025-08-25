import re
from datetime import datetime, timezone
from .common import base_system
from ..utils import run_cmd

POWERSHELL = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command"]

def machine_id():
    out, _, _ = run_cmd(["wmic", "csproduct", "get", "UUID"])
    lines = [l.strip() for l in out.splitlines() if l.strip()]
    return lines[1] if len(lines) > 1 else "WINDOWS-UNKNOWN"

def disk_encryption():
    out, err, _ = run_cmd(["manage-bde", "-status", "C:"])
    status = None
    if re.search(r"Protection Status:\s*Protection On", out):
        status = True
    elif re.search(r"Protection Status:\s*Protection Off", out):
        status = False
    return {"supported": True, "status": status, "raw": out or err}

def os_update_status():
    ps = r"(New-Object -ComObject Microsoft.Update.Session).CreateUpdateSearcher().Search(\"IsInstalled=0 and Type='Software'\").Updates.Count"
    out, err, _ = run_cmd(POWERSHELL + [ps])
    try:
        pending = int(out.strip())
        return {"supported": True, "up_to_date": pending == 0, "pending_count": pending, "raw": out or err}
    except Exception:
        return {"supported": True, "up_to_date": None, "raw": out or err}

def antivirus_status():
    ps = "Get-MpComputerStatus | Select-Object AMServiceEnabled,AntivirusEnabled,RealTimeProtectionEnabled | ConvertTo-Json"
    out, err, _ = run_cmd(POWERSHELL + [ps])
    present = True if out else None
    return {"supported": True, "present": present, "raw": out or err}

def inactivity_sleep():
    """Check Windows power settings for inactivity sleep timers."""
    # Get active power scheme
    out, _, _ = run_cmd(POWERSHELL + ["powercfg /getactivescheme"])
    scheme_guid = None
    for line in out.splitlines():
        if 'Power Scheme GUID' in line:
            scheme_guid = line.split()[-1]
            break
    
    if not scheme_guid:
        return {"supported": False, "compliant": None, "raw": "Could not determine active power scheme"}
    
    # Query relevant power settings
    out, _, _ = run_cmd(["powercfg", "/query", scheme_guid, "SUB_SLEEP"])
    
    # Parse the output to find sleep timers
    sleep_ac = None
    sleep_dc = None
    
    for line in out.splitlines():
        line = line.strip()
        if 'Sleep after' in line and 'AC Setting' in line:
            sleep_ac = int(line.split()[-2]) if line.split()[-2].isdigit() else None
        elif 'Sleep after' in line and 'DC Setting' in line:
            sleep_dc = int(line.split()[-2]) if line.split()[-2].isdigit() else None
    
   
    ac_ok = sleep_ac is not None and sleep_ac <= 600
    dc_ok = sleep_dc is not None and sleep_dc <= 600
    
    return {
        "supported": True,
        "compliant": ac_ok and dc_ok,
        "sleep_ac_seconds": sleep_ac,
        "sleep_dc_seconds": sleep_dc,
        "raw": out
    }

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
