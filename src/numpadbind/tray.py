"""Status-area (top-right) indicator: bright when active, dim when off."""
from .constants import DATA_DIR
from .gi_setup import AppIndicator, Gtk


def write_icons():
    d = DATA_DIR / "icons"; d.mkdir(parents=True, exist_ok=True)

    def svg(opacity, accent=None):
        r = "".join(f'<rect x="{3 + c * 6}" y="{3 + rr * 6}" width="5" height="5" rx="1.3" '
                    f'fill="{accent if accent and rr == 2 and c == 2 else "#ffffff"}"/>'
                    for rr in range(3) for c in range(3))
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" '
                f'viewBox="0 0 22 22" opacity="{opacity}">{r}</svg>')
    for n, s in (("on", svg(1)), ("l2", svg(1, "#ff9f43")), ("off", svg(0.4))):
        (d / f"numpadbind-{n}.svg").write_text(s)
    return str(d)


class Tray:
    def __init__(self, app):
        self.app, self.ind = app, None
        if not AppIndicator:
            print("AppIndicator missing - install gir1.2-ayatanaappindicator3-0.1")
            return
        menu = Gtk.Menu()
        self.mi_status = Gtk.MenuItem(label="NumLock off", sensitive=False); menu.append(self.mi_status)
        menu.append(Gtk.SeparatorMenuItem())
        self.mi_enabled = Gtk.CheckMenuItem(label="Enabled"); self.mi_enabled.set_active(app.cfg["enabled"])
        self.mi_enabled.connect("toggled", lambda m: app.set_enabled(m.get_active())); menu.append(self.mi_enabled)
        mi = Gtk.CheckMenuItem(label="Lock Layer 2")
        mi.connect("toggled", lambda m: m.get_active() != app.engine.sticky and app.engine.toggle_sticky())
        menu.append(mi)
        mi = Gtk.MenuItem(label="Open NumpadBind"); mi.connect("activate", lambda *_: app.activate()); menu.append(mi)
        menu.append(Gtk.SeparatorMenuItem())
        mi = Gtk.MenuItem(label="Quit"); mi.connect("activate", lambda *_: app.quit()); menu.append(mi)
        menu.show_all()
        self.ind = AppIndicator.Indicator.new("numpadbind", "numpadbind-off",
                                              AppIndicator.IndicatorCategory.APPLICATION_STATUS)
        self.ind.set_icon_theme_path(write_icons())
        self.ind.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.ind.set_menu(menu)

    def update(self, numlock, layer2, enabled, text):
        if not self.ind: return
        name = "numpadbind-off" if not (numlock and enabled) else "numpadbind-l2" if layer2 else "numpadbind-on"
        self.ind.set_icon_full(name, text)
        self.mi_status.set_label(text)

    def set_enabled(self, v):
        if self.ind: self.mi_enabled.set_active(v)
