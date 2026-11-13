"""Settings dialog."""
from ..gi_setup import Gtk
from ..constants import AUTOSTART, DEFAULTS, MOD_LABELS


class SettingsDialog(Gtk.Dialog):
    def __init__(self, win, app):
        super().__init__(title="Settings", transient_for=win, modal=True, use_header_bar=1)
        self.add_button("Close", Gtk.ResponseType.CLOSE)
        box = self.get_content_area(); box.set_spacing(10); box.set_border_width(16)
        cfg = app.cfg
        trow = Gtk.Box(spacing=10); trow.pack_start(Gtk.Label(label="Bindings work when NumLock is", xalign=0), True, True, 0)
        trig = Gtk.ComboBoxText(); trig.append("off", "Off (replaces arrows)"); trig.append("on", "On (replaces digits)")
        trig.set_active_id(cfg.get("trigger_when", "off")); trow.pack_end(trig, False, False, 0)
        box.pack_start(trow, False, False, 0)

        def trig_changed(c):
            cfg["trigger_when"] = c.get_active_id(); app.save(); win.refresh(); app.refresh_state()
        trig.connect("changed", trig_changed)

        row = Gtk.Box(spacing=10); row.pack_start(Gtk.Label(label="Hold for Layer 2", xalign=0), True, True, 0)
        mod = Gtk.ComboBoxText()
        for k, n in MOD_LABELS: mod.append(k, n)
        mod.set_active_id(cfg["layer2_modifier"]); row.pack_end(mod, False, False, 0); box.pack_start(row, False, False, 0)

        def mod_changed(c):
            cfg["layer2_modifier"] = c.get_active_id(); app.save(); win.refresh()
        mod.connect("changed", mod_changed)

        def check(text, key, tip=None):
            cb = Gtk.CheckButton(label=text); cb.set_active(cfg[key]); cb.set_tooltip_text(tip)
            def tog(c): cfg[key] = c.get_active(); app.save()
            cb.connect("toggled", tog); box.pack_start(cb, False, False, 0)
        check("Unbound numpad keys work normally", "passthrough",
              "Off = unbound numpad keys do nothing while bindings are active")
        check("Notify when a binding runs", "notify_trigger")
        check("Notify when the layer / NumLock changes", "notify_layer")
        def spin(text, key, lo, hi, step, tip):
            r = Gtk.Box(spacing=10); r.pack_start(Gtk.Label(label=text, xalign=0), True, True, 0)
            sp = Gtk.SpinButton.new_with_range(lo, hi, step); sp.set_value(cfg.get(key, DEFAULTS[key])); sp.set_tooltip_text(tip)
            sp.connect("value-changed", lambda w: (cfg.__setitem__(key, int(w.get_value())), app.save()))
            r.pack_end(sp, False, False, 0); box.pack_start(r, False, False, 0)
        spin("Hold time (ms)", "hold_ms", 150, 1000, 50, "How long to keep a key down for a Hold action")
        spin("Double-tap window (ms)", "double_ms", 150, 800, 50, "Max gap between the two taps")
        spin("Cheat sheet stays (seconds)", "overlay_secs", 0, 30, 1, "0 = until you click it or press a key")
        auto = Gtk.CheckButton(label="Start automatically at login"); auto.set_active(AUTOSTART.exists())
        auto.connect("toggled", lambda c: app.set_autostart(c.get_active()))
        box.pack_start(auto, False, False, 0)
        self.show_all()

