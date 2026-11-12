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
