import subprocess
import re

def run_cmd(cmd):
    """Run a system command and return (stdout, stderr, exitcode)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def parse_first_int_from_line(line):
    m = re.search(r"(\d+)", line)
    return int(m.group(1)) if m else None
