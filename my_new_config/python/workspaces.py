import os
import jinja2
import subprocess
import json
from dataclasses import dataclass


EWW_TEMPLATE = """
    (box :orientation "vertical"
        {% for pair in workspaces|batch(2) %}
        (box :orientation "horizontal" :class "workspace-group"
            {% for workspace in pair %}
            (eventbox :onclick "python /home/sylflo/.config/eww/python/cli.py --manager hyprland switch-workspace --workspace {{ workspace['id'] }}"
                (overlay
                    (image :class "image" :path "./images/test.png" :image-height 400)
                    (input :class "input" :valign "end" :halign "center" :value "{{ workspace['name'] }}" :onaccept "eww close workspaces")
                )
            )
            {% endfor %}
        )
        {% endfor %}
    )
"""

@dataclass
class Workspace:
    id: int
    name: str

class WindowManager:
    def __init__(self):
        environment = jinja2.Environment()
        self.template = environment.from_string(EWW_TEMPLATE)

    def get_workspaces(self) -> [Workspace]:
        """Return a list of workspaces"""
        raise NotImplementedError

    def switch_workspace(self, workspace_id: int):
        """Switch to the specified workspace."""
        raise NotImplementedError

    def rename_workspace(self, worspace_id: int, new_name: str):
        """Change name of the workspace ID specified"""
        raise NotImplementedError

    def set_eww_workspace(self) -> [Workspace]:
        workspaces = self.get_workspaces()
        ret = self.template.render(workspaces=workspaces)
        os.system(f"eww update workspaces_template='{ret}'") 

class HyprlandManager(WindowManager):
    def get_workspaces(self):
        result = subprocess.run(["hyprctl", "workspaces", "-j"], capture_output=True, text=True)
        return json.loads(result.stdout)

    def rename_workspace(self, workspace_id: int, new_name: str):
        os.system(f"hyprctl dispatch renameworkspace {workspace_id}, {new_name}")

    def switch_workspace(self, workspace_id: int):
        os.system(f"hyprctl dispatch workspace {str(workspace_id)}")
        os.system("eww close workspaces")
