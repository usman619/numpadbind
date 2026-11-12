"""Gtk.Application: wires engine, tray, actions and the main window together."""
import json
from pathlib import Path

from .actions import ActionRunner
from .autostart import set_autostart
from .config import load_cfg, save_cfg
from .constants import APP_ID, DEFAULTS
from .engine import Engine
from .gi_setup import Gdk, GLib, Gtk
from .tray import Tray
from .ui.css import CSS
from .ui.window import MainWindow
from .util import notify


class App(Gtk.Application):
    def __init__(self, background=False, debug=False):
        super().__init__(application_id=APP_ID)
        self.background, self.debug, self.win, self.cfg = background, debug, None, load_cfg()
        self.engine = self.tray = None
        self.state = (False, False)
        self.actions = ActionRunner(self.cfg, lambda: self.engine)
        self.set_autostart = set_autostart

    # lifecycle --------------------------------------------
    def do_startup(self):
        Gtk.Application.do_startup(self)
        self.hold()                      # keep running in the tray with no window
        prov = Gtk.CssProvider(); prov.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), prov,
                                                 Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.tray = Tray(self)
        self.engine = Engine(self.cfg, self.on_state, self.on_status, self.fire, GLib.idle_add)
        self.engine.debug = self.debug
        self.engine.start()

    def do_activate(self):
        if self.background:
            self.background = False; return
        if not self.win:
            self.win = MainWindow(self)
            self.win.show_status(self.engine.status)
            self.win.hb.set_subtitle(self.status_text())
        self.win.present()

    def do_shutdown(self):
        if self.engine: self.engine.stop()
        Gtk.Application.do_shutdown(self)

    # engine callbacks (run on the GTK thread) -------------
    def status_text(self):
        nl, l2 = self.state
        if not self.cfg["enabled"]: return "Paused"
        return f"NumLock on · Layer {2 if l2 else 1}" if nl else "NumLock off"

    def on_state(self, nl, l2):
        old, self.state = self.state, (nl, l2)
        self.tray.update(nl, l2, self.cfg["enabled"], self.status_text())
        if self.win:
            self.win.hb.set_subtitle(self.status_text())
            for p in self.win.pages.values(): p.set_numlock(nl)
        if self.cfg["notify_layer"] and old != self.state and old != (False, False):
            notify("NumpadBind", self.status_text())
        return False

    def on_status(self, st):
        if self.win: self.win.show_status(st)
        return False

    def fire(self, layer, name, b):
        if self.win: self.win.pages[layer].flash(name)
        self.actions.run(b)
        return False

    # settings ---------------------------------------------
    def set_enabled(self, v):
        if self.cfg["enabled"] == v: return
        self.cfg["enabled"] = v; self.save()
        if self.win: self.win.sw.set_active(v)
        self.tray.set_enabled(v)
        self.tray.update(*self.state, v, self.status_text())

    def save(self): save_cfg(self.cfg)

    def export_cfg(self, win):
        d = Gtk.FileChooserDialog(title="Export", transient_for=win, action=Gtk.FileChooserAction.SAVE)
        d.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "Export", Gtk.ResponseType.OK)
        d.set_current_name("numpadbind-config.json"); d.set_do_overwrite_confirmation(True)
        if d.run() == Gtk.ResponseType.OK:
            Path(d.get_filename()).write_text(json.dumps(self.cfg, indent=2, ensure_ascii=False))
        d.destroy()

    def import_cfg(self, win):
        d = Gtk.FileChooserDialog(title="Import", transient_for=win, action=Gtk.FileChooserAction.OPEN)
        d.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "Import", Gtk.ResponseType.OK)
        if d.run() == Gtk.ResponseType.OK:
            try:
                data = json.loads(Path(d.get_filename()).read_text())
                self.cfg.update({k: v for k, v in data.items() if k in DEFAULTS})   # in place: engine shares it
                self.save(); win.refresh()
            except (OSError, ValueError) as ex:
                notify("Import failed", str(ex))
        d.destroy()
