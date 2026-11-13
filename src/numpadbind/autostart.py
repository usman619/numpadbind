"""Start-at-login via an XDG autostart entry."""
import configparser, os, shlex, shutil, sys
from pathlib import Path

from .constants import AUTOSTART

LAUNCHER = Path.home() / ".local" / "bin" / "numpadbind"

ENTRY = """[Desktop Entry]
Type=Application
Name=NumpadBind
Comment=Bind apps and scripts to your numpad
Exec={exec} --background
Terminal=false
NoDisplay=true
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=5
"""


def _quote(arg):
    return '"' + arg.replace("\\", "\\\\").replace('"', '\\"') + '"' if any(c in arg for c in " \t\"'") else arg


def exec_command():
    """Absolute command: the session PATH at login often does not include ~/.local/bin."""
    if LAUNCHER.is_file() and os.access(LAUNCHER, os.X_OK):
        return _quote(str(LAUNCHER))
    found = shutil.which("numpadbind")
    if found:
        return _quote(found)
    return f"{_quote(sys.executable)} -m numpadbind"


def is_enabled():
    """True only if the entry exists, is not disabled (e.g. by GNOME Tweaks) and its program exists."""
    cp = configparser.ConfigParser(interpolation=None, strict=False)
    cp.optionxform = str
    try:
        cp.read(AUTOSTART, encoding="utf-8")
        sec = cp["Desktop Entry"]
        if sec.get("Hidden", "false").lower() == "true": return False
        if sec.get("X-GNOME-Autostart-enabled", "true").lower() == "false": return False
        cmd = shlex.split(sec.get("Exec", ""))
    except (KeyError, ValueError, OSError, configparser.Error):
        return False
    return bool(cmd) and shutil.which(cmd[0]) is not None


def set_autostart(on):
    """-> (ok, message). Verifies the result instead of assuming it worked."""
    try:
        if on:
            AUTOSTART.parent.mkdir(parents=True, exist_ok=True)
            AUTOSTART.write_text(ENTRY.format(exec=exec_command()), encoding="utf-8")
        else:
            AUTOSTART.unlink(missing_ok=True)
    except OSError as ex:
        return False, f"{AUTOSTART}: {ex.strerror or ex}"
    if is_enabled() != on:
        return False, f"Could not verify {AUTOSTART}" if on else f"Could not remove {AUTOSTART}"
    return True, ""