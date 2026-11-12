"""Custom app icon for the window, dock and app menu (the tray keeps its own state icons)."""
from pathlib import Path

from .gi_setup import GLib, Gtk

ICON_NAME = "numpadbind"
REPO_ASSETS = Path(__file__).resolve().parents[2] / "assets"     # only exists when running from source


def source_icon_path():
    """assets/ when running from source, otherwise the icon the installer put in the icon theme."""
    if REPO_ASSETS.is_dir():
        for ext in ("svg", "png"):
            for c in [REPO_ASSETS / f"{ICON_NAME}.{ext}", *sorted(REPO_ASSETS.glob(f"*.{ext}"))]:
                if c.is_file():
                    return c
    info = Gtk.IconTheme.get_default().lookup_icon(ICON_NAME, 128, 0)
    return Path(info.get_filename()) if info and info.get_filename() else None


def apply_window_icon():
    if Gtk.IconTheme.get_default().has_icon(ICON_NAME):
        Gtk.Window.set_default_icon_name(ICON_NAME)
    else:
        path = source_icon_path()
        if path:
            try: Gtk.Window.set_default_icon_from_file(str(path))
            except GLib.Error: pass