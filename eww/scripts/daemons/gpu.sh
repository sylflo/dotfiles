#!/bin/bash
update() {
    eww update gpu="$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits)"

    # Alternatively: With amdgpu_top
    # eww update gpu="$(amdgpu_top -gm --single | awk '/average_gfx_activity/ {print substr($2, 1, length($2)-1)}')"
}

while true; do
    update
    sleep 5
done
