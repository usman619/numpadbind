"""Runs a binding: launch app, command, open, keystrokes, system action."""
import os, shutil, subprocess, threading

from .apps import app_info, describe
from .constants import SYSTEM, SYSTEM_KEYS
from .gi_setup import Gdk
from .util import notify, spawn

TERMINALS = (("gnome-terminal", ["--"]), ("ptyxis", ["--"]), ("konsole", ["-e"]), ("xfce4-terminal", ["-x"]),
             ("x-terminal-emulator", ["-e"]), ("xterm", ["-e"]))


class ActionRunner:
    def __init__(self, cfg, engine_getter):
        self.cfg, self.engine = cfg, engine_getter

    def run(self, b):
        t = b.get("type")
        try:
            if t == "app": self.launch_app(b)
            elif t == "command": self.run_cmd(b["target"], b.get("terminal"))
            elif t == "open": spawn(["xdg-open", os.path.expanduser(b["target"])])
            elif t == "keys": self.engine().send_keys(b["target"])
            elif t == "system":
                key = SYSTEM_KEYS.get(b["target"])
                if key: self.engine().send_keys(key)
                else: self.run_cmd(SYSTEM[b["target"]][1])
            elif t == "layer": self.engine().toggle_sticky()
            if self.cfg["notify_trigger"] and t != "layer":
                notify("NumpadBind", describe(b)[0] or t)
        except Exception as ex:
            notify("NumpadBind — action failed", str(ex))

    def launch_app(self, b):
        info = app_info(b["target"])
        if not info:
            raise RuntimeError(f"{b['target']} is not installed")
        if b.get("focus") and os.environ.get("XDG_SESSION_TYPE") == "x11" and shutil.which("wmctrl"):
            cls = info.get_string("StartupWMClass") or os.path.basename((info.get_executable() or "").strip())
            if cls and subprocess.run(["wmctrl", "-x", "-a", cls], capture_output=True).returncode == 0:
                return
        info.launch([], Gdk.Display.get_default().get_app_launch_context())

    def run_cmd(self, cmd, terminal=False):
        if not terminal:
            p = subprocess.Popen(["/bin/sh", "-c", cmd], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.PIPE, text=True, start_new_session=True,
                                 cwd=os.path.expanduser("~"))

            def watch():                     # surface failures instead of failing silently
                err = (p.communicate()[1] or "").strip()
                if p.returncode > 0:
                    why = "command not found" if p.returncode == 127 else err[-200:] or "no output"
                    notify(f"NumpadBind: command failed (exit {p.returncode})", f"{cmd[:60]}\n{why}")
            threading.Thread(target=watch, daemon=True).start()
            return
        wrapped = cmd + '; echo; read -n1 -rsp "Done — press any key to close"'
        for term, flag in TERMINALS:
            if shutil.which(term):
                spawn([term, *flag, "bash", "-c", wrapped]); return
        raise RuntimeError("No terminal emulator found")
