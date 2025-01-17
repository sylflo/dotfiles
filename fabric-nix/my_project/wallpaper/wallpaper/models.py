import json
import os
import subprocess
from configparser import ConfigParser
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from screeninfo import get_monitors

from wallpaper.swww import SWWW as SwwwSettings

from typing import Union


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
class MainSettings:
    wallpapers_folder: Path = Path.home() / "Pictures"
    pagination: bool = False


@dataclass
class LayoutSettings:
    img_per_row: int = 3
    row_per_page: int = 4
    wallpaper_img_size: int = 250
    monitor_img_size: int = 250
    background_img: str = ""
    background_color: str = "#f2f2f2"
    selected_image: str = "#ffffff"
    selected_screen: str = "#ffffff"
    pagination_background_color: str = "#ffffff"
    pagination_color: str = "#495057"
    pagination_border_color: str = "#dee2e6"
    pagination_hover_background_color: str = "#f8f9fa"
    pagination_hover_color: str = "#212529"
    pagination_selected_background_color = "#007bff"
    pagination_selected_color: str = "#ffffff"
    pagination_selected_border: str = "#007bff"
    pagination_disabled_background_color: str = "#e9ecef"
    pagination_disabled_color: str = "#6c757d"
    pagination_disabled_border: str = "#e9ecef"


@dataclass
class AnimationSettings:
    init_transition_type: str = "none"
    init_transition_duration: int = 2000
    prev_transition_type: str = "none"
    prev_transition_duration: int = 2000
    next_transition_type: str = "none"
    next_transition_duration: int = 2000


@dataclass
class Settings:
    main: MainSettings = field(default_factory=MainSettings)
    layout: LayoutSettings = field(default_factory=LayoutSettings)
    animation: AnimationSettings = field(default_factory=AnimationSettings)
    swww: SwwwSettings = field(default_factory=SwwwSettings)

    config_file: str = field(default=str(DEFAULT_CONFIG_FILE), repr=False)

    @classmethod
    def load(cls, config_path=DEFAULT_CONFIG_FILE):
        from enum import Enum

        if os.path.exists(config_path):
            config = ConfigParser()
            config.read(config_path)

            def get_or_default(section, field_, default):
                if section in config and field_.name in config[section]:
                    value = config.get(section, field_.name)
                    if field_.type == bool:
                        return config.getboolean(section, field_.name)
                    else:
                        return field_.type(value)
                else:
                    return default

            main_data = {
                field_.name: get_or_default("Main", field_, field_.default)
                for field_ in fields(MainSettings)
            }
            layout_data = {
                field_.name: get_or_default("Layout", field_, field_.default)
                for field_ in fields(LayoutSettings)
            }
            animation_data = {
                field_.name: get_or_default("Animation", field_, field_.default)
                for field_ in fields(AnimationSettings)
            }
            swww_data = {
                field_.name: get_or_default("Swww", field_, field_.default)
                for field_ in fields(SwwwSettings)
            }

            settings = cls(
                main=MainSettings(**main_data),
                layout=LayoutSettings(**layout_data),
                animation=AnimationSettings(**animation_data),
                swww=SwwwSettings(**swww_data),
                config_file=config_path,
            )
        else:
            settings = cls(config_file=config_path)
            settings.save()
        return settings
        if settings.layout.background_img and not Path(settings.layout.background_img).exists():
            raise FileNotFoundError(
                f"Background image '{settings.background_img}' does not exist."
            )
        return settings

    def save(self):
        config = ConfigParser()

        config["Main"] = {
            k: str(v) for k, v in asdict(self.main).items()
        }
        config["Layout"] = {
            k: str(v) for k, v in asdict(self.layout).items()
        }
        config["Animation"] = {
            k: str(v) for k, v in asdict(self.animation).items()
        }
        config["Swww"] = {
            k: str(v) for k, v in asdict(self.swww).items()
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
        return [monitor.name for monitor in get_monitors()]


# Global variable for settings
SETTINGS = Settings.load()
