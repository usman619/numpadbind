from numpadbind import config
from numpadbind.constants import DEFAULTS


def test_defaults_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CFG_FILE", tmp_path / "c.json")
    assert config.load_cfg() == DEFAULTS


def test_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CFG_FILE", tmp_path / "sub" / "c.json")
    cfg = config.load_cfg()
    cfg["bindings"]["1"]["KP_5"] = {"type": "command", "target": "echo hi"}
    config.save_cfg(cfg)
    assert config.load_cfg()["bindings"]["1"]["KP_5"]["target"] == "echo hi"


def test_corrupt_file_falls_back(tmp_path, monkeypatch):
    f = tmp_path / "c.json"; f.write_text("{not json")
    monkeypatch.setattr(config, "CFG_FILE", f)
    assert config.load_cfg()["layer2_modifier"] == "shift"


def test_swap_layers_is_reversible():
    cfg = {"bindings": {"1": {"KP_1": {"type": "command", "target": "a"}}, "2": {"KP_2": {"type": "command", "target": "b"}}}}
    config.swap_layers(cfg)
    assert "KP_2" in cfg["bindings"]["1"] and "KP_1" in cfg["bindings"]["2"]
    config.swap_layers(cfg)
    assert "KP_1" in cfg["bindings"]["1"] and "KP_2" in cfg["bindings"]["2"]


def test_normalize_repairs_bad_or_imported_data():
    cfg = {"bindings": {"1": "oops"}, "trigger_when": "sideways", "layer2_modifier": "hyper",
           "hold_ms": "abc", "double_ms": 99999, "overlay_secs": -5, "enabled": 0}
    config.normalize(cfg)
    assert cfg["bindings"] == {"1": {}, "2": {}}
    assert cfg["trigger_when"] == "off" and cfg["layer2_modifier"] == "shift"
    assert cfg["hold_ms"] == 350 and cfg["double_ms"] == 1500 and cfg["overlay_secs"] == 0
    assert cfg["enabled"] is False


def test_load_cfg_survives_wrong_json_shape(tmp_path, monkeypatch):
    f = tmp_path / "c.json"; f.write_text('["not", "a", "dict"]')
    monkeypatch.setattr(config, "CFG_FILE", f)
    assert config.load_cfg()["bindings"] == {"1": {}, "2": {}}