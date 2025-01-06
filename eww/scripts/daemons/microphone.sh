#!/bin/sh
old_status=-1
update() {
    info="$(pactl list sources | awk '/Name: alsa_input.pci/{nr[NR+6]}; NR in nr')"
    status="$([[ "$info" == *"Mute: yes"* ]] && echo off || echo on)"
    # Only update if status changed
    if [ "$old_status" != "$status" ]; then
        eww update microphone="$status"
        old_status=$status
    fi
}

update
if [ "$1" == "oneshot" ]; then
    exit
fi

LANG=C pactl subscribe 2> /dev/null | grep --line-buffered "Event 'change' on source #" | while read -r line ; do
    update
done
