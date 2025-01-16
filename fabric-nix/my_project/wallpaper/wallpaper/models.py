import json
import os
import subprocess
from configparser import ConfigParser
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Literal, Optional

DEFAULT_CONFIG_FILE = Path.home() / ".config" / "sww_ui_ricing" / "app"


TransitionType = [
    "none",
    "crossfade",
    "slide-right",
    "slide-left",
    "slide-up",
    "slide-down",
]


@dataclass
class Settings:
    pagination: bool = False
    img_per_row: int = 3
    row_per_page: int = 4
    wallpaper_img_size: int = 250
    monitor_img_size: int = 250
    wallpapers_folder: Path = Path.home() / "Pictures"
    background_img: str = ""
    background_color: str = "#f2f2f2"
    transition_type: str = "none"
    transition_duration: int = 2000

    config_file: str = field(default=str(DEFAULT_CONFIG_FILE), repr=False)

    @classmethod
    def load(cls, config_path=DEFAULT_CONFIG_FILE):
        if os.path.exists(config_path):
            config = ConfigParser()
            config.read(config_path)

            data = {}
            for field_ in fields(cls):
                if field_.name == "config_file":
                    continue
                if field_.type == bool:
                    data[field_.name] = config.getboolean("View", field_.name)
                else:
                    data[field_.name] = field_.type(config.get("View", field_.name))
            settings = cls(**data)
        else:
            settings = cls(config_file=config_path)
            settings.save()

        if settings.background_img and not Path(settings.background_img).exists():
            raise FileNotFoundError(
                f"Background image '{settings.background_img}' does not exist."
            )
        if settings.transition_type not in TransitionType:
            raise ValueError(
                f"Transition type {settings.transition_type} not in TransitionType"
            )
        return settings

    def save(self):
        config = ConfigParser()
        config["View"] = {
            k: str(v) for k, v in asdict(self).items() if k != "config_file"
        }

        config_path = Path(self.config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            config.write(f)


class Wallpaper:
    def __init__(self, directory):
        self.directory = directory
        self.image_selected = None
        self.screens_selected = {}

    def get_images(self):
        return os.listdir(self.directory)

    def get_monitors(self):
        result = subprocess.run(
            ["hyprctl", "-j", "monitors"], capture_output=True, text=True
        )
        return [monitor["name"] for monitor in json.loads(result.stdout)]
