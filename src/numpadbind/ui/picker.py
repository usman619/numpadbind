"""Searchable application chooser (apt, Snap, Flatpak, AppImage)."""
from ..gi_setup import Gtk, Gio
from ..apps import source_of


class AppPicker(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Choose application", transient_for=parent, modal=True, use_header_bar=1)
        self.set_default_size(420, 520)
        self.chosen = None
        box = self.get_content_area(); box.set_spacing(6)
        self.search = Gtk.SearchEntry(placeholder_text="Search apps (apt, Snap, Flatpak…)", margin=8)
        box.pack_start(self.search, False, False, 0)
        sw = Gtk.ScrolledWindow(vexpand=True); box.pack_start(sw, True, True, 0)
        self.lb = Gtk.ListBox(); sw.add(self.lb)
        apps = sorted((a for a in Gio.AppInfo.get_all() if a.should_show()), key=lambda a: a.get_name().casefold())
        for a in apps:
            row = Gtk.ListBoxRow(); row.info = a; src = source_of(a)
            row.text = (a.get_name() + " " + src).lower()
            h = Gtk.Box(spacing=10, margin=6)
            img = Gtk.Image.new_from_gicon(a.get_icon(), Gtk.IconSize.DND) if a.get_icon() else Gtk.Image()
            img.set_pixel_size(32)
            h.pack_start(img, False, False, 0)
            h.pack_start(Gtk.Label(label=a.get_name(), xalign=0), True, True, 0)
            tag = Gtk.Label(label=src); tag.get_style_context().add_class("npdim"); h.pack_end(tag, False, False, 0)
            row.add(h); self.lb.add(row)
        self.lb.set_filter_func(lambda r: self.search.get_text().lower() in r.text)
        self.search.connect("search-changed", lambda *_: self.lb.invalidate_filter())
        self.lb.connect("row-activated", self.pick)
        self.show_all()

    def pick(self, _lb, row):
        self.chosen = row.info
        self.response(Gtk.ResponseType.OK)

