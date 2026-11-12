#!/usr/bin/env bash
set -euo pipefail
rm -rf "$HOME/.local/share/numpadbind" "$HOME/.local/bin/numpadbind" \
  "$HOME/.local/share/applications/numpadbind.desktop" "$HOME/.config/autostart/numpadbind.desktop"
sudo rm -f /etc/udev/rules.d/70-numpadbind.rules /etc/udev/rules.d/99-numpadbind.rules /etc/modules-load.d/numpadbind.conf
echo "Removed. Your bindings are kept in ~/.config/numpadbind (delete it to wipe them)."
echo "To drop input-group access:  sudo gpasswd -d \$USER input"
