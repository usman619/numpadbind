import time
"""Engine key-handling logic with fake devices (no /dev access needed)."""
from types import SimpleNamespace as Ev
from evdev import ecodes as e
from numpadbind.engine import Engine


class FakeUI:
    def __init__(self): self.out = []
    def write_event(self, ev): self.out.append((ev.code, ev.value))


def make(numlock=True, **cfg):
    c = {"enabled": True, "layer2_modifier": "shift", "passthrough": True, "trigger_when": "on", "hold_ms": 60, "double_ms": 80,
         "bindings": {"1": {"KP_5": {"type": "command", "target": "a"}},
                      "2": {"KP_5": {"type": "command", "target": "b"}}}}
    c.update(cfg)
    fired = []
    eng = Engine(c, lambda *a: None, lambda *a: None, lambda *a: fired.append(a))
    eng.numlock = numlock
    return eng, FakeUI(), fired


def key(code, val): return Ev(type=e.EV_KEY, code=code, value=val)


def test_bound_key_is_swallowed_and_fires():
    eng, ui, fired = make()
    for v in (1, 2, 0): eng.handle(ui, key(e.KEY_KP5, v))
    assert ui.out == [] and [f[0:2] for f in fired] == [("1", "KP_5")]


def test_layer2_with_shift():
    eng, ui, fired = make()
    eng.handle(ui, key(e.KEY_LEFTSHIFT, 1)); eng.handle(ui, key(e.KEY_KP5, 1))
    assert fired[0][2]["target"] == "b"
    assert ui.out == [(e.KEY_LEFTSHIFT, 1)]       # shift passes, bound key doesn't


def test_numlock_off_passes_through():
    eng, ui, fired = make(numlock=False)
    eng.handle(ui, key(e.KEY_KP5, 1))
    assert fired == [] and ui.out == [(e.KEY_KP5, 1)]


def test_unbound_key_passthrough_toggle():
    eng, ui, fired = make()
    eng.handle(ui, key(e.KEY_KP1, 1)); assert ui.out == [(e.KEY_KP1, 1)]
    eng2, ui2, _ = make(passthrough=False)
    eng2.handle(ui2, key(e.KEY_KP1, 1)); assert ui2.out == []


def test_paused_passes_everything():
    eng, ui, fired = make(enabled=False)
    eng.handle(ui, key(e.KEY_KP5, 1))
    assert fired == [] and ui.out == [(e.KEY_KP5, 1)]


def test_sticky_layer():
    eng, ui, fired = make()
    eng.toggle_sticky(); eng.handle(ui, key(e.KEY_KP5, 1))
    assert fired[0][0] == "2"


def test_lock_key_works_from_layer2_to_unlock():
    eng, ui, fired = make()
    eng.cfg["bindings"]["1"]["KP_0"] = {"type": "layer"}
    eng.toggle_sticky()
    eng.handle(ui, key(e.KEY_KP0, 1))
    assert fired and fired[0][2]["type"] == "layer" and ui.out == []


def test_real_numlock_state_wins_over_internal_counter(tmp_path):
    eng, ui, fired = make(numlock=True)          # counter thinks ON ...
    f = tmp_path / "brightness"; f.write_text("0\n")   # ... desktop says OFF
    eng.leds[ui] = str(f)
    eng.handle(ui, key(e.KEY_KP5, 1))
    assert fired == [] and ui.out == [(e.KEY_KP5, 1)]      # key behaves normally
    f.write_text("1\n")
    eng.handle(ui, key(e.KEY_KP5, 0)); eng.handle(ui, key(e.KEY_KP5, 1))
    assert len(fired) == 1


def test_default_trigger_is_numlock_off_digits_stay_normal_when_on():
    eng, ui, fired = make(numlock=False, trigger_when="off")
    eng.handle(ui, key(e.KEY_KP5, 1)); eng.handle(ui, key(e.KEY_KP5, 0))
    assert [f[1] for f in fired] == ["KP_5"] and ui.out == []              # NumLock off: binding fires
    eng2, ui2, fired2 = make(numlock=True, trigger_when="off")
    eng2.handle(ui2, key(e.KEY_KP5, 1))
    assert fired2 == [] and ui2.out == [(e.KEY_KP5, 1)]                    # NumLock on: normal digit


def test_unbound_key_with_numlock_off_stays_arrow():
    eng, ui, fired = make(numlock=False, trigger_when="off")
    eng.handle(ui, key(e.KEY_KP8, 1))
    assert fired == [] and ui.out == [(e.KEY_KP8, 1)]


def test_unknown_numlock_state_never_fires():
    eng, ui, fired = make(numlock=None, trigger_when="off")
    eng.handle(ui, key(e.KEY_KP5, 1))
    assert fired == []


def test_lock_key_works_when_it_lives_in_layer2_after_a_swap():
    eng, ui, fired = make()
    eng.cfg["bindings"]["1"] = {}
    eng.cfg["bindings"]["2"]["KP_0"] = {"type": "layer"}
    eng.handle(ui, key(e.KEY_KP0, 1))                 # pressed from Layer 1
    assert fired and fired[0][2]["type"] == "layer"


def cmd(t, **extra): return {"type": "command", "target": t, **extra}


def targets(fired): return [f[2]["target"] for f in fired]


def bind5(eng, b): eng.cfg["bindings"]["1"]["KP_5"] = b


def test_plain_binding_still_fires_instantly_on_press():
    eng, ui, fired = make()
    eng.handle(ui, key(e.KEY_KP5, 1))
    assert targets(fired) == ["a"]                       # no release needed, no delay


def test_hold_fires_hold_action_not_tap():
    eng, ui, fired = make(); bind5(eng, cmd("tap", hold=cmd("hold")))
    eng.handle(ui, key(e.KEY_KP5, 1)); time.sleep(0.2); eng.handle(ui, key(e.KEY_KP5, 0))
    assert targets(fired) == ["hold"] and ui.out == []


def test_quick_tap_with_hold_defined_fires_tap_on_release():
    eng, ui, fired = make(); bind5(eng, cmd("tap", hold=cmd("hold")))
    eng.handle(ui, key(e.KEY_KP5, 1)); assert fired == []          # waits to see if it becomes a hold
    eng.handle(ui, key(e.KEY_KP5, 0)); time.sleep(0.15)
    assert targets(fired) == ["tap"]


def test_double_tap_fires_only_double():
    eng, ui, fired = make(); bind5(eng, cmd("tap", double=cmd("dbl")))
    for v in (1, 0, 1, 0): eng.handle(ui, key(e.KEY_KP5, v)); time.sleep(0.01)
    time.sleep(0.2)
    assert targets(fired) == ["dbl"]


def test_single_tap_with_double_defined_fires_tap_after_the_window():
    eng, ui, fired = make(); bind5(eng, cmd("tap", double=cmd("dbl")))
    eng.handle(ui, key(e.KEY_KP5, 1)); eng.handle(ui, key(e.KEY_KP5, 0))
    assert fired == []
    time.sleep(0.25)
    assert targets(fired) == ["tap"]


def test_hold_only_key_with_empty_tap_does_nothing_on_quick_tap():
    eng, ui, fired = make(); bind5(eng, {"type": "none", "hold": cmd("hold")})
    eng.handle(ui, key(e.KEY_KP5, 1)); eng.handle(ui, key(e.KEY_KP5, 0)); time.sleep(0.15)
    assert fired == [] and ui.out == []                   # swallowed, nothing fired


def test_shift_does_not_cause_state_updates_while_bindings_are_inactive():
    states = []
    eng = Engine({"enabled": True, "layer2_modifier": "shift", "passthrough": True, "trigger_when": "off",
                  "bindings": {"1": {}, "2": {}}}, lambda *a: states.append(a), lambda *a: None, lambda *a: None)
    eng.numlock = True                                   # NumLock ON = normal typing mode
    ui = FakeUI()
    eng.handle(ui, key(e.KEY_LEFTSHIFT, 1)); eng.handle(ui, key(e.KEY_LEFTSHIFT, 0))
    assert states == [(True, False)]                     # one initial state, nothing per capital letter
    eng.numlock = False                                  # bindings active: Shift now means Layer 2
    eng.handle(ui, key(e.KEY_LEFTSHIFT, 1))
    assert states[-1] == (False, True)


def test_scan_looks_at_each_device_node_only_once(monkeypatch):
    from numpadbind import engine as eng_mod
    opened = []

    class FakeDev:
        def __init__(self, path): opened.append(path); self.name = "mouse"
        def capabilities(self): return {e.EV_KEY: [e.BTN_LEFT]}
        def close(self): pass

    monkeypatch.setattr(eng_mod, "InputDevice", FakeDev)
    monkeypatch.setattr(eng_mod.glob, "glob", lambda pat: ["/dev/input/event1", "/dev/input/event2"])
    eng, ui, _ = make()
    eng.scan(); eng.scan(); eng.scan()
    assert sorted(opened) == ["/dev/input/event1", "/dev/input/event2"]      # not re-opened every 3 s
    monkeypatch.setattr(eng_mod.glob, "glob", lambda pat: ["/dev/input/event2"])
    eng.scan()                                           # event1 unplugged...
    monkeypatch.setattr(eng_mod.glob, "glob", lambda pat: ["/dev/input/event1", "/dev/input/event2"])
    eng.scan()                                           # ...and a new device reuses its number
    assert opened.count("/dev/input/event1") == 2