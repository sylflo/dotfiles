# # Get the active monitor's geometry
# GEOMETRY=$(hyprctl monitors -j | jq -r '.[] | select(.focused == true) | "\(.x),\(.y) \(.width)x\(.height)"')

# # Take a screenshot of the active workspace
# grim -g "$GEOMETRY" ~/Pictures/workspace_screenshot.png =? in /tmp

;mayube jsut show n worksapce 
; Update name
; animeation when openning eww window workspace vie



# LATER
# Put this in bin path
python /home/sylflo/.config/eww/python/cli.py --manager hyprland switch-workspace --workspace {{ workspace['id'] }}
Custom Erorr for each exception

# add linter,mypy, black
