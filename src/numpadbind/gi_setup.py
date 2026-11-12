"""Single place that configures PyGObject. Import GUI classes from here."""
import importlib, os

# Make Flatpak / Snap launchers visible to Gio (apt ones are already there).
# Must run before GLib reads XDG_DATA_DIRS for the first time.
_extra = ["/var/lib/flatpak/exports/share",
          os.path.expanduser("~/.local/share/flatpak/exports/share"),
          "/var/lib/snapd/desktop"]
_cur = os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":")
os.environ["XDG_DATA_DIRS"] = ":".join(_cur + [d for d in _extra if d not in _cur and os.path.isdir(d)])

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, Gio, GLib, Pango  # noqa: E402

AppIndicator = None   # tray support is optional
for _ns in ("AyatanaAppIndicator3", "AppIndicator3"):
    try:
        gi.require_version(_ns, "0.1")
        AppIndicator = importlib.import_module("gi.repository." + _ns)
        break
    except (ValueError, ImportError):
        pass

__all__ = ["Gtk", "Gdk", "GdkPixbuf", "Gio", "GLib", "Pango", "AppIndicator"]
