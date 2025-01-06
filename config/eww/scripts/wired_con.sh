#!/bin/sh

# Run the command and capture the output
output=$(nmcli -t -f NAME,DEVICE con show --active | grep -i -m 1 "wired" | cut -d: -f1-3)

# Check if the output is not empty
if [[ -n "$output" ]]; then
    echo "$output"
else
    echo "N/A"
fi
