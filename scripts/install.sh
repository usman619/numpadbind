#!/usr/bin/env bash
# NumpadBind installer for Ubuntu / Debian (per-user app, system-wide input permissions)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$HOME/.local/share/numpadbind/venv"

echo "==> System packages"
sudo apt-get install -y python3-gi python3-venv python3-evdev gir1.2-gtk-3.0 \
  gir1.2-ayatanaappindicator3-0.1 libnotify-bin wmctrl playerctl

echo "==> Input permissions (uinput + 'input' group)"
sudo rm -f /etc/udev/rules.d/99-numpadbind.rules      # old name from earlier versions
sudo install -m644 "$ROOT/packaging/70-numpadbind.rules" /etc/udev/rules.d/70-numpadbind.rules
sudo install -m644 "$ROOT/packaging/uinput.conf" /etc/modules-load.d/numpadbind.conf
sudo modprobe uinput
sudo udevadm control --reload && sudo udevadm trigger
sudo usermod -aG input "$USER"

echo "==> Installing app into $VENV"
# Must be the distro Python (not conda/pyenv) so apt's python3-gi and python3-evdev are visible
rm -rf "$VENV"
/usr/bin/python3 -m venv --system-site-packages "$VENV"
"$VENV/bin/python" -c "import gi, evdev" || { echo "gi/evdev not importable - is python3-gi installed?"; exit 1; }
"$VENV/bin/pip" install --quiet --upgrade "$ROOT"
mkdir -p "$HOME/.local/bin" "$HOME/.local/share/applications"
install -m755 "$ROOT/packaging/numpadbind-launcher.sh" "$HOME/.local/bin/numpadbind"   # wrapper: cleans snap env, then runs the venv app
rm -f "$HOME/.local/share/applications/numpadbind.desktop"     # old name; the id must match the app id for dock icons
install -m644 "$ROOT/packaging/io.github.numpadbind.desktop" "$HOME/.local/share/applications/io.github.numpadbind.desktop"

echo "==> Icon (from assets/)"
pick() { local f="$ROOT/assets/numpadbind.$1"; if [ -f "$f" ]; then echo "$f"; else find "$ROOT/assets" -maxdepth 1 -name "*.$1" 2>/dev/null | sort | head -1 || true; fi; }
THEME="$HOME/.local/share/icons/hicolor"
ICON_SVG="$(pick svg)"; ICON_PNG="$(pick png)"
[ -n "$ICON_SVG" ] && install -Dm644 "$ICON_SVG" "$THEME/scalable/apps/numpadbind.svg"
if [ -n "$ICON_PNG" ]; then
  SIZE="$(python3 - "$ICON_PNG" <<'PY'
import struct, sys
w = struct.unpack(">I", open(sys.argv[1], "rb").read(24)[16:20])[0]
print(max([s for s in (16, 22, 24, 32, 48, 64, 96, 128, 256, 512) if s <= w] or [16]))
PY
)"
  install -Dm644 "$ICON_PNG" "$THEME/${SIZE}x${SIZE}/apps/numpadbind.png"
fi
[ -z "$ICON_SVG$ICON_PNG" ] && echo "   no icon found in assets/ - using the generated tray icons"
gtk-update-icon-cache -f -t "$THEME" 2>/dev/null || true

echo "Done. Quit any running copy (tray icon -> Quit, or: pkill -f numpadbind), then run: numpadbind\n(No re-login needed. The input group is only a fallback for non-seat sessions.)"
