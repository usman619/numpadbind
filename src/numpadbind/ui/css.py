"""Application stylesheet."""

CSS = b"""
.npkey { border-radius: 14px; padding: 6px; min-width: 92px; min-height: 84px; }
.npkey.bound { background: alpha(@theme_selected_bg_color, .14); border: 1px solid alpha(@theme_selected_bg_color, .55); }
.npkey.flash { background: @theme_selected_bg_color; }
.npnum { opacity: .55; font-size: 11px; font-weight: bold; }
.nplabel { font-size: 12px; font-weight: 600; }
.npdim { opacity: .5; }
.npind { border-radius: 14px; border: 1px dashed alpha(currentColor, .3); padding: 6px; }
.npind.on { border-style: solid; border-color: @theme_selected_bg_color; }
.npoverlay { background-color: transparent; }
.npcard { background-color: rgba(24, 24, 28, 0.92); border-radius: 20px; border: 1px solid rgba(255,255,255,.12); }
.npcard label { color: #f2f2f2; }
.npotitle { font-size: 15px; font-weight: bold; }
.npcell { background-color: rgba(255,255,255,.07); border-radius: 12px; padding: 6px; min-width: 88px; min-height: 76px; }
.npcell.bound { background-color: rgba(70,130,255,.30); }
.npcell .npnum { opacity: .6; }
.npextra { font-size: 10px; opacity: .75; }
"""
