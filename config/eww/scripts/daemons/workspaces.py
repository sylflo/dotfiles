#!/usr/bin/env python3
import os
import socket
import subprocess
import json


def get_workspaces():
    workspaces_raw = subprocess.check_output(["hyprctl", "workspaces", "-j"])
    workspaces = json.loads(workspaces_raw)
    for ws in workspaces:
        os.system(f"eww update ws{ws['id']}=''")

def get_active_workspace():
    monitors_raw = subprocess.check_output(["hyprctl", "monitors", "-j"])
    monitors = json.loads(monitors_raw)
    for monitor in monitors:
        if monitor['focused']:
            focused_id = monitors[0]['activeWorkspace']['id']
            os.system(f"eww update ws{focused_id}=''focused") 
            return 


# Path to Hyprland's IPC socket
socket_path = os.path.join(
    os.getenv("XDG_RUNTIME_DIR", ""),
    "hypr",
    os.getenv("HYPRLAND_INSTANCE_SIGNATURE", ""),
    ".socket2.sock"
)


def listen_for_events():
    # Connect to Hyprland IPC socket and listen for events
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(socket_path)
        print(f"Connected to {socket_path}, listening for events...")
        while True:
            try:
                event = client_socket.recv(4096).decode("utf-8").strip()
                if event:
                    print(f"Event received: {event}")
                    cmd = event.split(">>")[0]
            
                    if cmd == "workspace":
                        parts = event.split("\n")[1].split(">>")
                        cmd, params = parts[0], parts[1].split(",")
                        get_workspaces()
                        os.system(f"eww update ws{params[0]}='focused'")

                    # Add logic to handle specific events here
            except KeyboardInterrupt:
                print("Stopping event listener.")
                break
            except Exception as e:
                print(f"Error: {e}")
                break


def init():
    get_workspaces()
    get_active_workspace()


init()
listen_for_events()
