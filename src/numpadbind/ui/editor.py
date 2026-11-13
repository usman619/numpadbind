"""Dialog for editing one key: what a tap, a hold and a double-tap do."""
import shlex

from ..gi_setup import Gtk
from ..apps import app_info, source_of
from ..constants import SYSTEM, TYPES
from .picker import AppPicker


class ActionForm(Gtk.Box):
    """One action: a type chooser, the fields for that type, and an optional label."""

    def __init__(self, b):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10, border_width=12)
        b = b or {}
        self.app_id = b.get("target") if b.get("type") == "app" else None
        self.combo = Gtk.ComboBoxText()
        for k, n in TYPES: self.combo.append(k, n)
        self.pack_start(self.combo, False, False, 0)
        self.stack = Gtk.Stack(); self.pack_start(self.stack, False, False, 0)

        self.stack.add_named(Gtk.Label(label="Nothing happens.", xalign=0), "none")
        p = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)      # app
        self.app_btn = Gtk.Button(label="Choose application…"); self.app_btn.connect("clicked", self.choose_app)
        self.focus = Gtk.CheckButton(label="Raise the window if already running (X11, needs wmctrl)")
        self.focus.set_active(b.get("focus", False))
        p.pack_start(self.app_btn, False, False, 0); p.pack_start(self.focus, False, False, 0)
        self.stack.add_named(p, "app")
        p = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)      # command
        row = Gtk.Box(spacing=6); self.cmd = Gtk.Entry(placeholder_text="notify-send hi  or  ~/bin/backup.sh", hexpand=True)
        pick = Gtk.Button(label="Script…"); pick.connect("clicked", self.choose_file, self.cmd, True)
        row.pack_start(self.cmd, True, True, 0); row.pack_start(pick, False, False, 0)
        self.term = Gtk.CheckButton(label="Run in a terminal window"); self.term.set_active(b.get("terminal", False))
        p.pack_start(row, False, False, 0); p.pack_start(self.term, False, False, 0)
        self.stack.add_named(p, "command")
        row = Gtk.Box(spacing=6); self.open = Gtk.Entry(placeholder_text="https://…  or  ~/Documents", hexpand=True)   # open
        pick = Gtk.Button(label="File…"); pick.connect("clicked", self.choose_file, self.open, False)
        row.pack_start(self.open, True, True, 0); row.pack_start(pick, False, False, 0)
        self.stack.add_named(row, "open")
        p = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)      # keys
        self.keys = Gtk.Entry(placeholder_text="ctrl+alt+t")
        hint = Gtk.Label(label="Names like ctrl, alt, super, enter, f5, volumeup, playpause…\n"
                               "Note: your Layer 2 modifier is still held while this fires.", xalign=0)
        hint.get_style_context().add_class("npdim"); hint.set_line_wrap(True)
        p.pack_start(self.keys, False, False, 0); p.pack_start(hint, False, False, 0)
        self.stack.add_named(p, "keys")
        self.sys = Gtk.ComboBoxText()                                     # system
        for k, (n, _) in SYSTEM.items(): self.sys.append(k, n)
        self.sys.set_active(0)
        self.stack.add_named(self.sys, "system")
        self.stack.add_named(Gtk.Label(label="Makes Layer 2 stay on until you press this again.", xalign=0), "layer")
        self.stack.add_named(Gtk.Label(label="Shows what every key does. Tip: use it as a Hold action.", xalign=0), "overlay")

        self.label = Gtk.Entry(placeholder_text="Label (optional)", text=b.get("label", ""))
        self.pack_start(self.label, False, False, 0)

        t = b.get("type", "none")
        if t == "command": self.cmd.set_text(b.get("target", ""))
        elif t == "open": self.open.set_text(b.get("target", ""))
        elif t == "keys": self.keys.set_text(b.get("target", ""))
        elif t == "system": self.sys.set_active_id(b.get("target"))
        self.refresh_app_btn()
        self.combo.connect("changed", lambda c: self.stack.set_visible_child_name(c.get_active_id()))
        self.show_all()                      # stack children must be visible before one can be selected
        self.combo.set_active_id(t)

    def refresh_app_btn(self):
        info = app_info(self.app_id) if self.app_id else None
        self.app_btn.set_label(f"{info.get_name()}  ({source_of(info)})" if info else "Choose application…")

    def choose_app(self, _):
        dlg = AppPicker(self.get_toplevel())
        if dlg.run() == Gtk.ResponseType.OK and dlg.chosen:
            self.app_id = dlg.chosen.get_id(); self.refresh_app_btn()
        dlg.destroy()

    def choose_file(self, _b, entry, quote):
        dlg = Gtk.FileChooserDialog(title="Choose file", transient_for=self.get_toplevel(), action=Gtk.FileChooserAction.OPEN)
        dlg.add_buttons("Cancel", Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK)
        if dlg.run() == Gtk.ResponseType.OK:
            entry.set_text(shlex.quote(dlg.get_filename()) if quote else dlg.get_filename())
        dlg.destroy()

    def binding(self):
        t = self.combo.get_active_id()
        b = {"type": t, "label": self.label.get_text().strip()}
        if t == "app":
            if not self.app_id: return None
            b.update(target=self.app_id, focus=self.focus.get_active())
        elif t == "command":
            b.update(target=self.cmd.get_text().strip(), terminal=self.term.get_active())
        elif t == "open": b["target"] = self.open.get_text().strip()
        elif t == "keys": b["target"] = self.keys.get_text().strip()
        elif t == "system": b["target"] = self.sys.get_active_id()
        if t in ("command", "open", "keys") and not b["target"]: return None
        return None if t == "none" else b


class EditorDialog(Gtk.Dialog):
    TEST, CLEAR = 1, 2

    def __init__(self, win, app, layer, name, label):
        super().__init__(title=f"Layer {layer} · numpad {label}", transient_for=win, modal=True, use_header_bar=1)
        self.app, self.layer, self.name, self.win = app, layer, name, win
        b = app.cfg["bindings"][layer].get(name, {})
        self.set_default_size(440, -1)
        self.add_button("Clear", self.CLEAR).get_style_context().add_class("destructive-action")
        self.add_button("Test", self.TEST)
        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.add_button("Save", Gtk.ResponseType.OK).get_style_context().add_class("suggested-action")
        box = self.get_content_area(); box.set_spacing(8); box.set_border_width(10)
        self.forms = [ActionForm(b), ActionForm(b.get("hold")), ActionForm(b.get("double"))]
        self.nb = Gtk.Notebook()
        for form, title in zip(self.forms, ("Tap", "Hold", "Double-tap")):
            self.nb.append_page(form, Gtk.Label(label=title))
        box.pack_start(self.nb, False, False, 0)
        hint = Gtk.Label(label="Tap = quick press · Hold = keep it down · Double-tap = press twice quickly.\n"
                               "Keys with a Hold or Double-tap action wait a moment before the tap runs.", xalign=0)
        hint.get_style_context().add_class("npdim"); hint.set_line_wrap(True)
        box.pack_start(hint, False, False, 0)
        self.show_all()
        self.connect("response", self.on_response)

    def binding(self):
        tap, hold, dbl = (f.binding() for f in self.forms)
        if not (tap or hold or dbl): return None
        b = dict(tap) if tap else {"type": "none"}
        if hold: b["hold"] = hold
        if dbl: b["double"] = dbl
        return b

    def on_response(self, _d, resp):
        binds = self.app.cfg["bindings"][self.layer]
        if resp == self.TEST:
            b = self.forms[self.nb.get_current_page()].binding()      # runs the tab you are looking at
            if b: self.app.actions.run(b)
            return
        if resp == self.CLEAR:
            binds.pop(self.name, None)
        elif resp == Gtk.ResponseType.OK:
            b = self.binding()
            if b: binds[self.name] = b
            else: binds.pop(self.name, None)
        if resp in (self.CLEAR, Gtk.ResponseType.OK):
            self.app.save(); self.win.refresh()
        self.destroy()
