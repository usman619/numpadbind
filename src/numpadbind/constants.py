"""Static data: key layout, modifiers, system actions, paths and defaults."""
import os
from pathlib import Path

from evdev import ecodes as e

APP_ID = "io.github.numpadbind"
VNAME = "NumpadBind virtual"   # name prefix of our uinput devices (we never grab these)


def _xdg(var, default):
    return Path(os.environ.get(var) or Path.home() / default)


CFG_FILE = _xdg("XDG_CONFIG_HOME", ".config") / "numpadbind" / "config.json"
DATA_DIR = _xdg("XDG_DATA_HOME", ".local/share") / "numpadbind"
AUTOSTART = _xdg("XDG_CONFIG_HOME", ".config") / "autostart" / "numpadbind.desktop"

KEYS = [
    ("KP_DIV", "/", e.KEY_KPSLASH, 0, 1, 1, 1), ("KP_MUL", "*", e.KEY_KPASTERISK, 0, 2, 1, 1),
    ("KP_SUB", "−", e.KEY_KPMINUS, 0, 3, 1, 1),
    ("KP_7", "7", e.KEY_KP7, 1, 0, 1, 1), ("KP_8", "8", e.KEY_KP8, 1, 1, 1, 1),
    ("KP_9", "9", e.KEY_KP9, 1, 2, 1, 1), ("KP_ADD", "+", e.KEY_KPPLUS, 1, 3, 2, 1),
    ("KP_4", "4", e.KEY_KP4, 2, 0, 1, 1), ("KP_5", "5", e.KEY_KP5, 2, 1, 1, 1),
    ("KP_6", "6", e.KEY_KP6, 2, 2, 1, 1),
    ("KP_1", "1", e.KEY_KP1, 3, 0, 1, 1), ("KP_2", "2", e.KEY_KP2, 3, 1, 1, 1),
    ("KP_3", "3", e.KEY_KP3, 3, 2, 1, 1), ("KP_ENTER", "⏎", e.KEY_KPENTER, 3, 3, 2, 1),
    ("KP_0", "0", e.KEY_KP0, 4, 0, 1, 2), ("KP_DOT", ".", e.KEY_KPDOT, 4, 2, 1, 1),
]
CODE2NAME = {k[2]: k[0] for k in KEYS}
MODS = {
    "shift": [e.KEY_LEFTSHIFT, e.KEY_RIGHTSHIFT], "ctrl": [e.KEY_LEFTCTRL, e.KEY_RIGHTCTRL],
    "alt": [e.KEY_LEFTALT], "altgr": [e.KEY_RIGHTALT], "rctrl": [e.KEY_RIGHTCTRL],
    "super": [e.KEY_LEFTMETA, e.KEY_RIGHTMETA],
}
MOD_LABELS = [("shift", "Shift"), ("ctrl", "Ctrl"), ("alt", "Alt"), ("altgr", "Right Alt (AltGr)"),
              ("rctrl", "Right Ctrl"), ("super", "Super")]
MOD_NAME = dict(MOD_LABELS)

VOL = "wpctl set-volume -l 1.5 @DEFAULT_AUDIO_SINK@ 5%{s} 2>/dev/null || pactl set-sink-volume @DEFAULT_SINK@ {s}5%"
SYSTEM = {
    "play_pause": ("Play / Pause media", "playerctl play-pause"),
    "next": ("Next track", "playerctl next"),
    "prev": ("Previous track", "playerctl previous"),
    "vol_up": ("Volume up", VOL.format(s="+")),
    "vol_down": ("Volume down", VOL.format(s="-")),
    "mute": ("Mute / unmute speakers",
             "wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle || pactl set-sink-mute @DEFAULT_SINK@ toggle"),
    "mic": ("Mute / unmute microphone",
            "wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle || pactl set-source-mute @DEFAULT_SOURCE@ toggle"),
    "bright_up": ("Brightness up", "brightnessctl set 10%+"),
    "bright_down": ("Brightness down", "brightnessctl set 10%-"),
    "screenshot": ("Screenshot", "gnome-screenshot -i || flameshot gui || spectacle"),
    "lock": ("Lock screen", "loginctl lock-session"),
    "suspend": ("Suspend", "systemctl suspend"),
    "dark": ("Toggle dark mode",
             "c=$(gsettings get org.gnome.desktop.interface color-scheme); if [ \"$c\" = \"'prefer-dark'\" ]; "
             "then gsettings set org.gnome.desktop.interface color-scheme default; "
             "else gsettings set org.gnome.desktop.interface color-scheme prefer-dark; fi"),
}
# Handled by sending the real hardware key (desktop shows its OSD, works with any audio stack).
SYSTEM_KEYS = {"play_pause": "playpause", "next": "nextsong", "prev": "previoussong",
               "vol_up": "volumeup", "vol_down": "volumedown", "mute": "mute", "mic": "micmute",
               "bright_up": "brightnessup", "bright_down": "brightnessdown", "screenshot": "sysrq"}
TYPES = [("none", "Nothing"), ("app", "Application"), ("command", "Command or script"),
         ("open", "URL, file or folder"), ("keys", "Send keystrokes"),
         ("system", "System action"), ("layer", "Lock Layer 2 on / off")]
TYPE_ICON = {"command": "utilities-terminal", "open": "folder-open", "keys": "input-keyboard",
             "system": "preferences-system", "layer": "go-up"}

DEFAULTS = {"enabled": True, "layer2_modifier": "shift", "passthrough": True, "trigger_when": "off",  # bindings fire when NumLock is "off" or "on"
            "notify_trigger": False, "notify_layer": False, "bindings": {"1": {}, "2": {}}}

