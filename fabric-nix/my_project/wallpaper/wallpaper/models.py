import json
import os
import subprocess
from configparser import ConfigParser
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from screeninfo import get_monitors

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

    config_file: str = field(default=str(DEFAULT_CONFIG_FILE), repr=False)

    @classmethod
    def load(cls, config_path=DEFAULT_CONFIG_FILE):
        if os.path.exists(config_path):
            config = ConfigParser()
            config.read(config_path)

            main_data = {
                field_.name: field_.type(config.get("Main", field_.name))
                for field_ in fields(MainSettings)
            }
            layout_data = {
                field_.name: field_.type(config.get("Layout", field_.name))
                for field_ in fields(LayoutSettings)
            }
            animation_data = {
                field_.name: field_.type(config.get("Animation", field_.name))
                for field_ in fields(AnimationSettings)
            }

            settings = cls(
                main=MainSettings(**main_data),
                layout=LayoutSettings(**layout_data),
                animation=AnimationSettings(**animation_data),
                config_file=config_path,
            )
        else:
            settings = cls(config_file=config_path)
            settings.save()
        return settings
        #     data = {}
        #     for field_ in fields(cls):
        #         if field_.name == "config_file":
        #             continue
        #         if field_.type == bool:
        #             data[field_.name] = config.getboolean("View", field_.name)
        #         else:
        #             data[field_.name] = field_.type(config.get("View", field_.name))
        #     settings = cls(**data)
        if settings.layout.background_img and not Path(settings.layout.background_img).exists():
            raise FileNotFoundError(
                f"Background image '{settings.background_img}' does not exist."
            )
        # if settings.init_transition_type not in TransitionType:
        #     raise ValueError(
        #         f"Transition type {settings.init_transition_type} not in TransitionType"
        #     )
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
