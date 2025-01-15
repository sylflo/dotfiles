import subprocess
import json
import os

from dataclasses import asdict, dataclass, field, fields
from typing import Optional
from configparser import ConfigParser
from pathlib import Path

DEFAULT_CONFIG_FILE = Path.home() / ".config" / "sww_ui_ricing" / "app"

@dataclass
class Settings:
    img_per_row: int = 3
    wallpaper_img_size: int = 250
    monitor_img_size: int = 250
    wallpapers_folder: Path = Path.home() / "Pictures"

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
            return cls(**data)
        else:
            default_settings = cls(config_file=config_path)
            default_settings.save()

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
#     # background_color: Optional[str]
#     bacgkround_img: Optional[str] = None
#     # color_text:
#     scroll: Optional[bool] = False # if False pagination
#     animation: Optional[bool] = True

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
