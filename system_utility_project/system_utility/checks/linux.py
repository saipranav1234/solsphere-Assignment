"""Linux system checks implementation."""
import re
import os
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from .common import base_system
from ..utils import run_cmd

def machine_id() -> str:
    """Get system machine ID."""
    try:
      
        if os.path.exists("/etc/machine-id"):
            with open("/etc/machine-id", "r") as f:
                return f.read().strip()
      
        hostname, _, _ = run_cmd(["hostname"])
        return hostname.strip() or "LINUX-UNKNOWN"
    except Exception as e:
        return f"LINUX-ERROR-{str(e)}"

def disk_encryption() -> Dict[str, Any]:
    """Check disk encryption status."""
    try:
       
        out, err, _ = run_cmd(["lsblk", "-o", "FSTYPE,LABEL,MOUNTPOINT", "-l", "-n"])
        
      
        luks_encrypted = any(
            "crypto_LUKS" in line or 
            any(marker in line.lower() for marker in ["crypt", "luks", "encrypted"])
            for line in out.splitlines()
        )
     
        root_encrypted = False
        try:
            root_dev = subprocess.check_output(
                ["findmnt", "-n", "-o", "SOURCE", "/"],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            if root_dev:
                out, _, _ = run_cmd(["lsblk", "-o", "FSTYPE", "-n", "-l", root_dev])
                root_encrypted = "crypto_LUKS" in out
        except Exception:
            pass
            
        return {
            "supported": True,
            "status": luks_encrypted or root_encrypted,
            "root_encrypted": root_encrypted,
            "raw": out or err
        }
    except Exception as e:
        return {"supported": False, "status": None, "error": str(e), "raw": str(e)}

def os_update_status() -> Dict[str, Any]:
    """Check for available OS updates."""
    pkg_managers = [
   
        ("apt", "apt list --upgradable 2>/dev/null | wc -l", 
         lambda x: int(x.strip()) == 1),  # Header line means no updates
        ("dnf", "dnf check-update --quiet 2>/dev/null; echo $?", 
         lambda x: x.strip() == "100"),  # 100 means updates available
        ("yum", "yum check-update --quiet 2>/dev/null; echo $?", 
         lambda x: x.strip() == "100"),  # 100 means updates available
        ("pacman", "pacman -Qu | wc -l", 
         lambda x: int(x.strip()) == 0),  # 0 means no updates
        ("zypper", "zypper list-updates 2>&1 | grep -v 'No updates' | wc -l", 
         lambda x: int(x.strip()) == 0)   # 0 means no updates
    ]
    
    for pkg, check_cmd, parse_func in pkg_managers:
        try:
            out, _, _ = run_cmd(["bash", "-lc", f"command -v {pkg} >/dev/null && ({check_cmd}) || echo 'not_found'"])
            if "not_found" not in out:
                return {
                    "supported": True,
                    "up_to_date": parse_func(out),
                    "package_manager": pkg,
                    "raw": out.strip()
                }
        except Exception as e:
            continue
            
    return {
        "supported": False, 
        "up_to_date": None, 
        "error": "No supported package manager found",
        "raw": ""
    }

def antivirus_status() -> Dict[str, Any]:
    """Check for active antivirus software."""
    # Common Linux antivirus services
    av_services = [
        "clamav-daemon", "clamd", "clamd@.service",
        "esets", "esets.service",
        "f-prot", "fprot",
        "sophos", "sophos.service",
        "sav-protect", "sav-protect.service",
        "mcafee", "mcafee.service",
        "kaspersky", "kav4fs"
    ]
    
    # Check running services
    active_av = []
    for service in av_services:
        try:
            out, _, _ = run_cmd(["systemctl", "is-active", service])
            if "active" in out.lower():
                active_av.append(service)
        except Exception:
            continue
    
    # Check for AppArmor/SELinux
    security_modules = {}
    try:
        # Check AppArmor
        out, _, _ = run_cmd(["aa-status", "--enabled"])
        security_modules["apparmor"] = out.strip().lower() == "apparmor is enabled."
    except Exception:
        security_modules["apparmor"] = False
    
    try:
        # Check SELinux
        out, _, _ = run_cmd(["getenforce"])
        security_modules["selinux"] = out.strip().lower() in ("enforcing", "permissive")
    except Exception:
        security_modules["selinux"] = False
    
    return {
        "supported": True,
        "present": len(active_av) > 0 or any(security_modules.values()),
        "antivirus_services": active_av,
        "security_modules": security_modules,
        "raw": {"services": active_av, "security_modules": security_modules}
    }

def inactivity_sleep() -> Dict[str, Any]:
    """Check system inactivity sleep settings."""
    def check_systemd_sleep() -> Tuple[Optional[int], Optional[int]]:
        """Check systemd sleep settings."""
        try:
            # Check systemd sleep settings
            out, _, _ = run_cmd(["systemd-inhibit", "--list"])
            if "idle" in out.lower():
                return 0, 0  # Systemd is preventing idle sleep
            return None, None
        except Exception:
            return None, None
    
    def check_gnome_settings() -> Tuple[Optional[int], Optional[int]]:
        """Check GNOME power settings."""
        try:
            out_ac, _, _ = run_cmd([
                "gsettings", "get", 
                "org.gnome.settings-daemon.plugins.power", 
                "sleep-inactive-ac-timeout"
            ])
            out_dc, _, _ = run_cmd([
                "gsettings", "get",
                "org.gnome.settings-daemon.plugins.power",
                "sleep-inactive-battery-timeout"
            ])
            
            ac = int(out_ac) if out_ac.strip().isdigit() else None
            dc = int(out_dc) if out_dc.strip().isdigit() else None
            return ac, dc
        except Exception:
            return None, None
    
    def check_xfce_power() -> Tuple[Optional[int], Optional[int]]:
        """Check XFCE power settings."""
        try:
            out, _, _ = run_cmd(["xfconf-query", "-c", "xfce4-power-manager", "-p", "/xfce4-power-manager/dpms-on-ac-sleep", "-v"])
            ac = int(out.strip()) if out.strip().isdigit() else None
            out, _, _ = run_cmd(["xfconf-query", "-c", "xfce4-power-manager", "-p", "/xfce4-power-manager/dpms-on-battery-sleep", "-v"])
            dc = int(out.strip()) if out.strip().isdigit() else None
            return ac, dc
        except Exception:
            return None, None
    
    # Try different methods to get sleep settings
    ac, dc = check_gnome_settings()
    if ac is None or dc is None:
        ac, dc = check_xfce_power()
    if ac is None or dc is None:
        ac, dc = check_systemd_sleep()
    
    # Check if settings are compliant (≤ 10 minutes = 600 seconds)
    ac_ok = ac is not None and ac <= 600
    dc_ok = dc is not None and dc <= 600
    
    return {
        "supported": ac is not None or dc is not None,
        "compliant": ac_ok and dc_ok if (ac is not None or dc is not None) else None,
        "sleep_ac_seconds": ac,
        "sleep_dc_seconds": dc,
        "raw": f"ac={ac} dc={dc}"
    }

def collect() -> Dict[str, Any]:
    """Collect all system information."""
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
