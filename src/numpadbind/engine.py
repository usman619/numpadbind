"""Key engine: grabs keyboards via evdev, swallows bound numpad keys and
re-emits everything else through uinput. No GUI dependencies."""
import glob, select, threading, time

from evdev import InputDevice, UInput, ecodes as e

from .constants import CODE2NAME, MODS, VNAME
from .util import notify, parse_combo


class Engine(threading.Thread):
    """Grabs keyboards, swallows bound numpad keys, forwards everything else."""

    def __init__(self, cfg, on_state, on_status, on_fire, call_main=lambda fn, *a: fn(*a)):
        """cfg: live config dict. Callbacks are invoked through call_main
        (GLib.idle_add in the app) so the GUI is only touched from its own thread."""
        super().__init__(daemon=True)
        self.cfg = cfg
        self.on_state, self.on_status, self.on_fire, self.call_main = on_state, on_status, on_fire, call_main
        self.devs = {}          # path -> (InputDevice, UInput)
        self.bad = {}           # path -> retry-after timestamp
        self.pressed, self.swallowed = set(), set()
        self.numlock, self.sticky, self.last, self.status = None, False, None, None
        self.debug = False
        self.leds = {}          # uinput device -> sysfs file holding the desktop's real NumLock state
        self.injector, self.running = None, True

    # state -------------------------------------------------
    def layer2_active(self):
        return self.sticky or any(c in self.pressed for c in MODS.get(self.cfg["layer2_modifier"], []))

    def emit(self):
        st = (bool(self.numlock), self.layer2_active())
        if st != self.last:
            self.last = st
            self.call_main(self.on_state, *st)

    def toggle_sticky(self):
        self.sticky = not self.sticky
        self.emit()

    def bindings_active(self):
        """Bindings fire in the NumLock state chosen in Settings (default: NumLock OFF);
        in the other state the numpad keeps its normal behaviour."""
        return self.numlock is not None and bool(self.numlock) == (self.cfg.get("trigger_when", "off") == "on")

    def dbg(self, msg):
        if self.debug: print("[numpadbind]", msg, flush=True)

    def sync_numlock(self, ui=None):
        """Read the desktop's real NumLock state. The compositor writes it to our virtual
        keyboard, and the kernel exposes it in sysfs - so it can't drift like a counter would."""
        for u in ([ui] if ui in self.leds else list(self.leds)):
            try:
                with open(self.leds[u]) as f:
                    val = int(f.read().strip()) > 0
            except (OSError, ValueError):
                continue
            if val != self.numlock:
                self.numlock = val
                for dev, _ in list(self.devs.values()):        # keep the physical LED honest
                    try: dev.set_led(e.LED_NUML, 1 if val else 0)
                    except Exception: pass
                self.emit()
            return

    @staticmethod
    def find_led_file(ui):
        try:
            node = ui.device.path.rsplit("/", 1)[-1]
            hits = glob.glob(f"/sys/class/input/{node}/device/*numlock/brightness")
            return hits[0] if hits else None
        except Exception:
            return None

    def toggle_numlock(self):
        self.numlock = not self.numlock
        for dev, _ in list(self.devs.values()):
            try: dev.set_led(e.LED_NUML, 1 if self.numlock else 0)
            except Exception: pass

    def set_status(self, s):
        if s != self.status:
            self.status = s
            self.call_main(self.on_status, s)

    # devices -----------------------------------------------
    def scan(self):
        perm = uin = False
        for path in glob.glob("/dev/input/event*"):
            if path in self.devs or time.time() < self.bad.get(path, 0):
                continue
            try:
                dev = InputDevice(path)
            except PermissionError:
                perm = True; continue
            except OSError:
                continue
            if dev.name.startswith(VNAME) or e.KEY_KP5 not in dev.capabilities().get(e.EV_KEY, []):
                dev.close(); continue
            try:
                ui = UInput.from_device(dev, name=(VNAME + " " + dev.name)[:79])
            except Exception:
                uin = True; dev.close(); self.bad[path] = time.time() + 10; continue
            try:
                dev.grab()
            except OSError:
                ui.close(); dev.close(); self.bad[path] = time.time() + 10; continue
            self.devs[path] = (dev, ui)
            led = self.find_led_file(ui)
            if led: self.leds[ui] = led
            if self.numlock is None:
                self.numlock = e.LED_NUML in dev.leds()
                self.emit()
        self.set_status("ok" if self.devs else "uinput" if uin else "perm" if perm else "nodev")

    def drop(self, path):
        dev, ui = self.devs.pop(path, (None, None))
        self.leds.pop(ui, None)
        for x in (ui, dev):
            try: x.close()
            except Exception: pass

    def run(self):
        last_scan = 0
        while self.running:
            if time.time() - last_scan > 3:
                self.scan(); last_scan = time.time()
            fds = {d.fd: p for p, (d, _) in self.devs.items()}
            if not fds:
                time.sleep(1); continue
            ready, _, _ = select.select(list(fds), [], [], 1.0)
            self.sync_numlock()
            for fd in ready:
                path = fds[fd]
                dev, ui = self.devs[path]
                try:
                    for ev in dev.read():
                        self.handle(ui, ev)
                except BlockingIOError:
                    pass
                except OSError:
                    self.drop(path)

    def handle(self, ui, ev):
        if ev.type != e.EV_KEY:
            ui.write_event(ev); return
        code, val = ev.code, ev.value
        if val == 1: self.pressed.add(code)
        elif val == 0: self.pressed.discard(code)
        if val != 2: self.emit()
        if code == e.KEY_NUMLOCK and val == 1:
            if ui in self.leds:
                threading.Timer(0.15, self.sync_numlock, [ui]).start()
            else:
                self.toggle_numlock(); self.emit()
        elif code in CODE2NAME:
            if code in self.swallowed:               # release / repeat of a bound key
                if val == 0: self.swallowed.discard(code)
                return
            if val == 1: self.sync_numlock(ui)
            if val == 1:
                self.dbg(f"{CODE2NAME[code]} pressed: numlock={'ON' if self.numlock else 'off'} bindings_active={self.bindings_active()} "
                         f"({'sysfs' if ui in self.leds else 'counted'}) enabled={self.cfg['enabled']} "
                         f"layer={'2' if self.layer2_active() else '1'}")
            if val == 1 and self.cfg["enabled"] and self.bindings_active():
                layer = "2" if self.layer2_active() else "1"
                name = CODE2NAME[code]
                b = self.cfg["bindings"][layer].get(name)
                if not b:      # the "Lock Layer 2" key must work from either layer, or you could get stuck
                    b1 = self.cfg["bindings"]["1" if layer == "2" else "2"].get(name)
                    if b1 and b1.get("type") == "layer": b = b1
                if b and b.get("type") not in (None, "none"):
                    self.dbg(f"  -> bound, running {b.get('type')}")
                    self.swallowed.add(code)
                    self.call_main(self.on_fire, layer, name, b)
                    return
                if not self.cfg["passthrough"]:
                    self.swallowed.add(code); return
        ui.write_event(ev)

    # key injection -----------------------------------------
    def send_keys(self, combo):
        codes = parse_combo(combo)

        def work():
            try:
                if not self.injector:
                    self.injector = UInput({e.EV_KEY: list(range(1, 249))}, name=VNAME + " injector")
                    time.sleep(0.4)
                for c in codes: self.injector.write(e.EV_KEY, c, 1)
                self.injector.syn(); time.sleep(0.03)
                for c in reversed(codes): self.injector.write(e.EV_KEY, c, 0)
                self.injector.syn()
            except Exception as ex:
                notify("NumpadBind: key send failed", str(ex))
        threading.Thread(target=work, daemon=True).start()

    def stop(self):
        self.running = False
        for p in list(self.devs): self.drop(p)