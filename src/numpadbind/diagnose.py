"""`numpadbind --diagnose`: read-only report on how NumLock is detected. Grabs nothing."""
import glob, os, subprocess

from evdev import InputDevice, ecodes as e


def _sh(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
        return (r.stdout or r.stderr).strip() or "(empty)"
    except Exception as ex:
        return f"(failed: {ex})"


def _read(path):
    try:
        with open(path) as f: return f.read().strip()
    except OSError as ex:
        return f"(unreadable: {ex.strerror})"


def run():
    print("== Keyboards in /dev/input ==")
    for path in sorted(glob.glob("/dev/input/event*"), key=lambda p: int(p.rsplit("event", 1)[1])):
        try:
            d = InputDevice(path)
        except PermissionError:
            print(f"{path}: NO PERMISSION"); continue
        except OSError:
            continue
        keys = d.capabilities().get(e.EV_KEY, [])
        if e.KEY_A in keys or e.KEY_KP5 in keys:
            print(f"{path}: {d.name!r} keypad={'yes' if e.KEY_KP5 in keys else 'NO'} "
                  f"numlock_key={'yes' if e.KEY_NUMLOCK in keys else 'NO'} "
                  f"physical_numlock_led={'on' if e.LED_NUML in d.leds() else 'off'}")
        d.close()
    print("\n== NumLock LEDs exposed by the kernel (the app reads the 'NumpadBind virtual' one) ==")
    for f in sorted(glob.glob("/sys/class/leds/*numlock/brightness")):
        base = os.path.dirname(f)
        print(f"{os.path.basename(base)}: {_read(f)}   device={_read(os.path.join(base, 'device/name'))!r}")
    print("\n== Desktop's own idea of NumLock ==")
    print("gsettings numlock-state:", _sh("gsettings get org.gnome.desktop.peripherals.keyboard numlock-state"))
    print("xset (X11/XWayland):", _sh("xset q | grep -i 'num lock'"))
    print("session type:", os.environ.get("XDG_SESSION_TYPE", "?"))
    from . import autostart
    print("\n== Autostart ==")
    print("entry:", autostart.AUTOSTART, "| enabled:", autostart.is_enabled())
    print(_read(autostart.AUTOSTART) if autostart.AUTOSTART.exists() else "(no entry)")
    print("\nRun this once with NumLock ON and once with it OFF and compare.")