"""Small helpers without GUI dependencies."""
import os, shutil, subprocess

from evdev import ecodes as e


def spawn(argv, **kw):
    return subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, start_new_session=True,
                            cwd=os.path.expanduser("~"), **kw)



def notify(title, body):
    if shutil.which("notify-send"):
        spawn(["notify-send", "-a", "NumpadBind", "-i", "input-keyboard", title, body])


ALIASES = {"ctrl": "LEFTCTRL", "control": "LEFTCTRL", "shift": "LEFTSHIFT", "alt": "LEFTALT",
           "altgr": "RIGHTALT", "super": "LEFTMETA", "meta": "LEFTMETA", "win": "LEFTMETA",
           "return": "ENTER", "del": "DELETE", "play": "PLAYPAUSE", "volup": "VOLUMEUP",
           "voldown": "VOLUMEDOWN", "pgup": "PAGEUP", "pgdn": "PAGEDOWN"}


def parse_combo(text):
    codes = []
    for tok in text.lower().replace(" ", "").split("+"):
        code = e.ecodes.get("KEY_" + ALIASES.get(tok, tok.upper()))
        if code is None:
            raise ValueError(f"Unknown key “{tok}”")
        codes.append(code)
    if not codes:
        raise ValueError("Empty key combo")
    return codes

