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
install -m644 "$ROOT/packaging/numpadbind.desktop" "$HOME/.local/share/applications/numpadbind.desktop"

echo "Done. Quit any running copy (tray icon -> Quit, or: pkill -f numpadbind), then run: numpadbind\n(No re-login needed. The input group is only a fallback for non-seat sessions.)"
