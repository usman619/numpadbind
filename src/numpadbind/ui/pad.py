"""The numpad grid shown inside the main window."""
from ..gi_setup import Gtk, Gio, GLib, Pango
from ..apps import describe
from ..constants import KEYS
from .editor import EditorDialog


class NumpadPage(Gtk.Grid):
    def __init__(self, app, layer, win):
        super().__init__(row_spacing=8, column_spacing=8, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER, margin=16)
        self.app, self.layer, self.win, self.buttons = app, layer, win, {}
        self.numind = Gtk.Label(label="Num\nLock"); self.numind.get_style_context().add_class("npind")
        self.attach(self.numind, 0, 0, 1, 1)
        for name, label, _c, r, c, rs, cs in KEYS:
            btn = Gtk.Button(); btn.get_style_context().add_class("npkey")
            btn.connect("clicked", lambda _b, n=name, l=label: EditorDialog(self.win, self.app, self.layer, n, l))
            self.attach(btn, c, r, cs, rs); self.buttons[name] = btn
        self.refresh()

    def refresh(self):
        for name, label, *_ in KEYS:
            btn = self.buttons[name]
            if btn.get_child(): btn.remove(btn.get_child())
            b = self.app.cfg["bindings"][self.layer].get(name)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
            num = Gtk.Label(label=label, xalign=0); num.get_style_context().add_class("npnum")
            box.pack_start(num, False, False, 0)
            ctx = btn.get_style_context()
            if b:
                text, icon, tip = describe(b)
                img = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.DIALOG) if isinstance(icon, Gio.Icon) \
                    else Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.DIALOG)
                lbl = Gtk.Label(label=text); lbl.set_ellipsize(Pango.EllipsizeMode.END); lbl.set_max_width_chars(10)
                lbl.get_style_context().add_class("nplabel")
                img.set_pixel_size(32)
                box.pack_start(img, True, True, 0); box.pack_start(lbl, False, False, 0)
                btn.set_tooltip_text(tip); ctx.add_class("bound")
            else:
                img = Gtk.Image.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
                img.get_style_context().add_class("npdim")
                box.pack_start(img, True, True, 0)
                btn.set_tooltip_text("Click to bind"); ctx.remove_class("bound")
            btn.add(box)
        self.show_all()

    def set_numlock(self, on):
        ctx = self.numind.get_style_context()
        (ctx.add_class if on else ctx.remove_class)("on")

    def flash(self, name):
        ctx = self.buttons[name].get_style_context(); ctx.add_class("flash")
        GLib.timeout_add(250, lambda: ctx.remove_class("flash") and False)

