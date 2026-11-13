"""Load / save the JSON configuration."""
import json

from .constants import CFG_FILE, DEFAULTS


def load_cfg():
    cfg = json.loads(json.dumps(DEFAULTS))
    try:
        data = json.loads(CFG_FILE.read_text())
        for k, v in data.items():
            cfg[k] = v
        cfg["bindings"].setdefault("1", {}); cfg["bindings"].setdefault("2", {})
    except (OSError, ValueError):
        pass
    return cfg


def save_cfg(cfg):
    CFG_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = CFG_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
    tmp.replace(CFG_FILE)



def swap_layers(cfg):
    """Layer 1 gets Layer 2's bindings and vice versa (pressing it again undoes it)."""
    b = cfg["bindings"]
    b["1"], b["2"] = b["2"], b["1"]
