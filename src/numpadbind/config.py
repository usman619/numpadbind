"""Load / save the JSON configuration."""
import json

from .constants import CFG_FILE, DEFAULTS, MODS


def load_cfg():
    cfg = json.loads(json.dumps(DEFAULTS))
    try:
        data = json.loads(CFG_FILE.read_text())
        for k, v in data.items():
            cfg[k] = v
    except (OSError, ValueError, AttributeError):
        pass
    return normalize(cfg)


def save_cfg(cfg):
    CFG_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = CFG_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
    tmp.replace(CFG_FILE)



def swap_layers(cfg):
    """Layer 1 gets Layer 2's bindings and vice versa (pressing it again undoes it)."""
    b = cfg["bindings"]
    b["1"], b["2"] = b["2"], b["1"]


def normalize(cfg):
    """Make any config (old, hand-edited or imported) safe for the engine and the UI."""
    b = cfg.get("bindings")
    cfg["bindings"] = b = b if isinstance(b, dict) else {}
    for layer in ("1", "2"):
        if not isinstance(b.get(layer), dict): b[layer] = {}
    if cfg.get("trigger_when") not in ("on", "off"): cfg["trigger_when"] = "off"
    if cfg.get("layer2_modifier") not in MODS: cfg["layer2_modifier"] = "shift"
    for key, (lo, hi) in {"hold_ms": (100, 2000), "double_ms": (100, 1500), "overlay_secs": (0, 60)}.items():
        try: v = int(cfg.get(key, DEFAULTS[key]))
        except (TypeError, ValueError): v = DEFAULTS[key]
        cfg[key] = max(lo, min(hi, v))
    for key in ("enabled", "passthrough", "notify_trigger", "notify_layer"):
        cfg[key] = bool(cfg.get(key, DEFAULTS[key]))
    return cfg