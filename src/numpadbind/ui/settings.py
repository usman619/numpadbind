"""Settings dialog."""
from ..gi_setup import Gtk
from ..constants import AUTOSTART, MOD_LABELS


class SettingsDialog(Gtk.Dialog):
    def __init__(self, win, app):
        super().__init__(title="Settings", transient_for=win, modal=True, use_header_bar=1)
        self.add_button("Close", Gtk.ResponseType.CLOSE)
        box = self.get_content_area(); box.set_spacing(10); box.set_border_width(16)
        cfg = app.cfg
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
              "Off = unbound numpad keys do nothing while NumLock is on")
        check("Notify when a binding runs", "notify_trigger")
        check("Notify when the layer / NumLock changes", "notify_layer")
        auto = Gtk.CheckButton(label="Start automatically at login"); auto.set_active(AUTOSTART.exists())
        auto.connect("toggled", lambda c: app.set_autostart(c.get_active()))
        box.pack_start(auto, False, False, 0)
        self.show_all()

