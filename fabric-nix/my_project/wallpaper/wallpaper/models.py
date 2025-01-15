import subprocess
import json
import os

from dataclasses import asdict, dataclass, field, fields
from typing import Optional, Literal
from configparser import ConfigParser
from pathlib import Path



DEFAULT_CONFIG_FILE = Path.home() / ".config" / "sww_ui_ricing" / "app"


TransitionType = ['none', 'crossfade', 'slide-right', 'slide-left', 'slide-up', 'slide-down']

@dataclass
class Settings:
    img_per_row: int = 3
    wallpaper_img_size: int = 250
    monitor_img_size: int = 250
    wallpapers_folder: Path = Path.home() / "Pictures"
    background_img: str = ""
    background_color: str = "#f2f2f2"
    transition_type: str = 'none'
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
                data[field_.name] = field_.type(config.get("View", field_.name))
                print(data[field_.name])
            settings = cls(**data)
        else:
            settings = cls(config_file=config_path)
            settings.save()

        if settings.background_img and not Path(settings.background_img).exists():
            raise FileNotFoundError(f"Background image '{settings.background_img}' does not exist.")
        if settings.transition_type not in TransitionType:
            raise ValueError(f"Transition type {settings.transition_type} not in TransitionType")
        return settings

    def save(self):
        config = ConfigParser()
        config["View"] = {k: str(v) for k, v in asdict(self).items() if k != "config_file"}

        config_path = Path(self.config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            config.write(f)

# @dataclass
# class Settings:
#     # min_width:
#     # min_height
#     # max_width
#     # max_heigth
#     # color_text:
#     scroll: Optional[bool] = False # if False pagination

class Wallpaper:
    def __init__(self, directory):
        self.directory = directory
        self.image_selected = None
        self.screens_selected = {}

    def get_images_as_row(self, img_per_row: int):
        images = os.listdir(self.directory)
        return [images[i:i + img_per_row] for i in range(0, len(images), img_per_row)]

    def get_monitors(self):
        result = subprocess.run(["hyprctl", "-j", "monitors"], capture_output=True, text=True)
        return [monitor['name'] for monitor in json.loads(result.stdout)]

    # def set_wallpaper(self, monitors, image_name):
    #     # This should be in controller
    #     if image_name:
    #         for monitor in monitors:
    #             os.system(f"swww img -o \"{monitor}\" ./images/{image_name}")
