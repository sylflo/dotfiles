#!/usr/bin/env bash
source ~/.config/sway/scripts/sway-colors

# window_prefix="<span foreground=\"$x5\">» </span>"
# drun_prefix="<span foreground=\"$x6\">> </span>"
# run_prefix="<span foreground=\"$x2\">$ </span>"
combi_prompt=">>>"

rofi -show combi \
     -modes combi \
     -combi-modes "window,drun,run" \
     -display-window "window" \
     -display-drun "drun" \
     -display-run "run" \
     -display-combi "combi" \
