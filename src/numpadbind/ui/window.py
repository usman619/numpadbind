"""Main window."""
from ..gi_setup import Gtk
from ..constants import MOD_NAME
from .pad import NumpadPage
from .settings import SettingsDialog


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="NumpadBind", default_width=500, default_height=560)
        self.app = app
        hb = Gtk.HeaderBar(show_close_button=True, title="NumpadBind"); self.hb = hb
        self.set_titlebar(hb)
        self.sw = Gtk.Switch(active=app.cfg["enabled"], valign=Gtk.Align.CENTER)
        self.sw.set_tooltip_text("Enable / pause all bindings")
        self.sw.connect("notify::active", lambda s, _p: app.set_enabled(s.get_active()))
        hb.pack_start(self.sw)
        swap = Gtk.Button(label="⇄ Swap")
        swap.set_tooltip_text("Swap layers: Layer 1 gets Layer 2's bindings and Layer 2 gets Layer 1's")
        swap.connect("clicked", lambda *_: app.flip_layers())
        hb.pack_start(swap)
        menu = Gtk.Menu()
        for text, cb in (("Settings…", lambda *_: SettingsDialog(self, app)), ("Import config…", lambda *_: app.import_cfg(self)),
                         ("Export config…", lambda *_: app.export_cfg(self)), ("Quit NumpadBind", lambda *_: app.quit())):
            mi = Gtk.MenuItem(label=text); mi.connect("activate", cb); menu.append(mi)
        menu.show_all()
        mb = Gtk.MenuButton(); mb.add(Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON))
        mb.set_popup(menu); hb.pack_end(mb)
        hb.show_all()          # the titlebar is not shown by outer.show_all(); without this the window has no bar to drag

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL); self.add(outer)
        self.bar = Gtk.InfoBar(message_type=Gtk.MessageType.WARNING, no_show_all=True)
        self.bar_lbl = Gtk.Label(wrap=True, xalign=0); self.bar.get_content_area().add(self.bar_lbl)
        outer.pack_start(self.bar, False, False, 0)
        self.stack = Gtk.Stack(); self.pages = {}
        for layer in ("1", "2"):
            page = NumpadPage(app, layer, self); self.pages[layer] = page
            self.stack.add_titled(page, layer, f"Layer {layer}")
        tabs = Gtk.StackSwitcher(stack=self.stack, halign=Gtk.Align.CENTER, margin_top=10)   # Layer 1 | Layer 2
        outer.pack_start(tabs, False, False, 0)
        outer.pack_start(self.stack, True, True, 0)
        self.hint = Gtk.Label(); self.hint.get_style_context().add_class("npdim"); self.hint.set_margin_bottom(10)
        outer.pack_start(self.hint, False, False, 0)
        self.connect("delete-event", lambda w, _e: w.hide() or True)   # close = hide to tray
        self.refresh()
        outer.show_all(); self.bar.hide()

    def refresh(self):
        m = MOD_NAME[self.app.cfg["layer2_modifier"]]
        self.stack.child_set_property(self.pages["2"], "title", f"Layer 2 · {m}")
        self.hint.set_text(f"With NumLock {self.app.cfg.get('trigger_when', 'off')}, press a key for Layer 1 — hold {m} for Layer 2.")
        for p in self.pages.values(): p.refresh()

    def show_status(self, st):
        msgs = {"perm": "No access to keyboards. Run install.sh (adds you to the ‘input’ group), then log out and in.",
                "uinput": "Can’t open /dev/uinput. Run install.sh, then log out and in.",
                "nodev": "No keyboard with a numpad was found."}
        if st in msgs: self.bar_lbl.set_text(msgs[st]); self.bar_lbl.show(); self.bar.show()
        else: self.bar.hide()