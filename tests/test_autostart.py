from numpadbind import autostart


def setup(tmp_path, monkeypatch, name="numpadbind"):
    launcher = tmp_path / "bin dir" / name                  # space in the path on purpose
    launcher.parent.mkdir(); launcher.write_text("#!/bin/sh\n"); launcher.chmod(0o755)
    monkeypatch.setattr(autostart, "LAUNCHER", launcher)
    monkeypatch.setattr(autostart, "AUTOSTART", tmp_path / "autostart" / "numpadbind.desktop")
    return launcher


def test_enable_writes_absolute_exec_and_verifies(tmp_path, monkeypatch):
    launcher = setup(tmp_path, monkeypatch)
    assert autostart.set_autostart(True) == (True, "")
    text = autostart.AUTOSTART.read_text()
    assert f'Exec="{launcher}" --background' in text and "X-GNOME-Autostart-enabled=true" in text
    assert autostart.is_enabled()


def test_disable_removes_entry(tmp_path, monkeypatch):
    setup(tmp_path, monkeypatch)
    autostart.set_autostart(True)
    assert autostart.set_autostart(False) == (True, "")
    assert not autostart.AUTOSTART.exists() and not autostart.is_enabled()


def test_entry_disabled_elsewhere_or_dangling_is_not_enabled(tmp_path, monkeypatch):
    launcher = setup(tmp_path, monkeypatch)
    autostart.set_autostart(True)
    p = autostart.AUTOSTART
    p.write_text(p.read_text().replace("enabled=true", "enabled=false"))          # e.g. switched off in GNOME Tweaks
    assert not autostart.is_enabled()
    autostart.set_autostart(True); launcher.unlink()                              # program was uninstalled
    assert not autostart.is_enabled()


def test_unwritable_location_reports_error(tmp_path, monkeypatch):
    setup(tmp_path, monkeypatch)
    blocker = tmp_path / "file"; blocker.write_text("x")
    monkeypatch.setattr(autostart, "AUTOSTART", blocker / "numpadbind.desktop")   # parent is a file
    ok, msg = autostart.set_autostart(True)
    assert not ok and msg