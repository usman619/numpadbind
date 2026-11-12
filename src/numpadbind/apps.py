"""Desktop-entry helpers (Gio sees apt, Snap and Flatpak launchers)."""
from .gi_setup import Gio
from .constants import SYSTEM, TYPE_ICON
import os


def source_of(info):
    fn = info.get_filename() or ""
    if "/flatpak/" in fn: return "Flatpak"
    if "/snapd/" in fn: return "Snap"
    if "appimage" in fn.lower(): return "AppImage"
    if fn.startswith(os.path.expanduser("~")): return "User"
    return "System / apt"


def app_info(desktop_id):
    try:
        return Gio.DesktopAppInfo.new(desktop_id)
    except Exception:
        return None


def describe(b):
    """-> (label, gicon-or-icon-name, tooltip)"""
    t = b.get("type")
    label = b.get("label", "")
    if t == "app":
        info = app_info(b.get("target", ""))
        return (label or (info.get_name() if info else "Missing app"),
                info.get_icon() if info else "dialog-warning", b.get("target", ""))
    tip = b.get("target", "")
    if t == "system":
        name = SYSTEM.get(b.get("target"), ("?", ""))[0]
        return label or name, TYPE_ICON[t], name
    if t == "layer":
        return label or "Lock Layer 2", TYPE_ICON[t], "Toggle sticky Layer 2"
    return label or tip, TYPE_ICON.get(t, "list-add-symbolic"), tip

