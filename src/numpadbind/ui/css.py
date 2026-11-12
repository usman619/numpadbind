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
"""

