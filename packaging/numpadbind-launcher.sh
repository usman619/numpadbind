#!/usr/bin/env bash
# Launcher for NumpadBind. Terminals started from snap apps (e.g. the VS Code snap)
# leak snap library paths that crash system Python/GTK, so strip them first.
if [ -n "${SNAP:-}${SNAP_NAME:-}" ] || [[ "${LD_LIBRARY_PATH:-}${GIO_MODULE_DIR:-}${GTK_PATH:-}" == */snap/* ]]; then
  unset $(env | cut -d= -f1 | grep -E '^(SNAP|GIO_MODULE_DIR$|GTK_PATH$|GTK_EXE_PREFIX$|GTK_IM_MODULE_FILE$|GDK_PIXBUF|GSETTINGS_SCHEMA_DIR$|LOCPATH$|FONTCONFIG|LD_LIBRARY_PATH$|LD_PRELOAD$|XDG_DATA_HOME$|XDG_DATA_DIRS$|XDG_CONFIG_HOME$|XDG_CONFIG_DIRS$)')
fi
exec "${NUMPADBIND_VENV:-$HOME/.local/share/numpadbind/venv}/bin/numpadbind" "$@"