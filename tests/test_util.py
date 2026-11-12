import pytest
from evdev import ecodes as e
from numpadbind.util import parse_combo


def test_parse_combo():
    assert parse_combo("Ctrl+Alt+T") == [e.KEY_LEFTCTRL, e.KEY_LEFTALT, e.KEY_T]
    assert parse_combo("super + enter") == [e.KEY_LEFTMETA, e.KEY_ENTER]
    assert parse_combo("volumeup") == [e.KEY_VOLUMEUP]


def test_parse_combo_rejects_unknown():
    with pytest.raises(ValueError):
        parse_combo("ctrl+nonsense")
