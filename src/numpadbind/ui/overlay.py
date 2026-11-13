"""Cheat-sheet overlay: a translucent numpad showing what every key does right now."""
from ..apps import key_summary
from ..constants import KEYS
from ..gi_setup import Gdk, Gio, GLib, Gtk, Pango


class CheatSheet(Gtk.Window):
    def __init__(self, app):
        super().__init__(decorated=False, resizable=False, accept_focus=False, focus_on_map=False,
                         skip_taskbar_hint=True, skip_pager_hint=True, window_position=Gtk.WindowPosition.CENTER)
        self.app, self.layer, self.gen = app, "1", 0
        self.set_keep_above(True)
        self.set_type_hint(Gdk.WindowTypeHint.SPLASHSCREEN)
        screen = self.get_screen(); visual = screen.get_rgba_visual()
        if visual and screen.is_composited(): self.set_visual(visual)      # translucent background
        self.set_app_paintable(True)
        self.get_style_context().add_class("npoverlay")
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, border_width=18)
        card.get_style_context().add_class("npcard"); self.add(card)
        self.title = Gtk.Label(); self.title.get_style_context().add_class("npotitle")
        self.grid = Gtk.Grid(row_spacing=8, column_spacing=8, halign=Gtk.Align.CENTER)
        foot = Gtk.Label(label="Click to close"); foot.get_style_context().add_class("npextra")
        for w in (self.title, self.grid, foot): card.pack_start(w, False, False, 0)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", lambda *_: self.hide_sheet())

    def build(self, layer):
        self.layer = layer
        for child in self.grid.get_children(): self.grid.remove(child)
        mod = self.app.cfg["layer2_modifier"]
        self.title.set_text(f"Layer {layer}" + ("" if layer == "2" else f"  ·  hold {mod} for Layer 2"))
        binds = self.app.cfg["bindings"][layer]
        for name, label, _c, r, c, rs, cs in KEYS:
            cell = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            ctx = cell.get_style_context(); ctx.add_class("npcell")
            num = Gtk.Label(label=label, xalign=0); num.get_style_context().add_class("npnum")
            cell.pack_start(num, False, False, 0)
            b = binds.get(name)
            if b:
                ctx.add_class("bound")
                text, icon, _tip, extras = key_summary(b)
                img = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.DIALOG) if isinstance(icon, Gio.Icon) \
                    else Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.DIALOG)
                img.set_pixel_size(28)
                lbl = Gtk.Label(label=text); lbl.set_ellipsize(Pango.EllipsizeMode.END); lbl.set_max_width_chars(11)
                cell.pack_start(img, True, True, 0); cell.pack_start(lbl, False, False, 0)
                for line in extras:
                    ex = Gtk.Label(label=line); ex.set_ellipsize(Pango.EllipsizeMode.END); ex.set_max_width_chars(13)
                    ex.get_style_context().add_class("npextra"); cell.pack_start(ex, False, False, 0)
            self.grid.attach(cell, c, r, cs, rs)
        self.show_all()

    def show_sheet(self, layer):
        self.build(layer)
        self.present()
        self.gen += 1
        secs = int(self.app.cfg.get("overlay_secs", 5))
        if secs > 0:
            GLib.timeout_add_seconds(secs, self._autohide, self.gen)

    def _autohide(self, gen):
        if gen == self.gen: self.hide_sheet()
        return False

    def update_layer(self, layer):
        if layer != self.layer: self.build(layer)

    def hide_sheet(self):
        self.gen += 1
        self.hide()
