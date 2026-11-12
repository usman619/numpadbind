"""Start-at-login via an XDG autostart entry."""
import shlex, shutil, sys

from .constants import AUTOSTART


def set_autostart(on):
    if not on:
        AUTOSTART.unlink(missing_ok=True)
        return
    exe = shutil.which("numpadbind") or f"{shlex.quote(sys.executable)} -m numpadbind"
    AUTOSTART.parent.mkdir(parents=True, exist_ok=True)
    AUTOSTART.write_text("[Desktop Entry]\nType=Application\nName=NumpadBind\n"
                         f"Exec={exe} --background\nX-GNOME-Autostart-enabled=true\n")
