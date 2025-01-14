from dataclasses import asdict, dataclass, fields
from enum import Enum
from typing import Optional

import re

# @dataclass
# class App:
# disable aimation
#     # min_width: ?
#     # min_height: ?
#     # max_width: ?
#     # max_heigth: ?
#     # fullscreen ?
#     # text color
#     # inputr/entry color
#     img_per_row: 2
#     backround_color:
#     background_image
#     swww: SWWW

# TODO put this into config file
# CONFIG_FILE = "~/.config/swww_ui_ricing"
CONFIG_FILE = "./config.test"


class HexColor:
    HEX_COLOR_PATTERN = re.compile(r'^#?[0-9A-Fa-f]{6}$')

    def __init__(self, color: str):
        if not self.HEX_COLOR_PATTERN.match(color):
            raise ValueError(f"Invalid hex color: {color}")
        self.color = color if color.startswith('#') else f"#{color}"

    def __str__(self):
        return self.color


class SwwwResize(Enum):
    NO = "no"
    CROP  = "crop"
    FIT = "fit"


class SwwwFilter(Enum):
    NEAREST = "Nearest"
    BILINEAR = "Bilinear"
    CATMULLROM = "CatmullRom"
    MITCHELL = "Mitechell"
    LANCZOS3 = "Lanczos3"


class SwwwTransitionType(Enum):
    NONE = "none"
    SIMPLE = "simple"
    FADE = "fade"
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    WIPE = "wipe"
    WAVE = "wave"
    GROW = "grow"
    CENTER = "center"
    ANY = "any"
    OUTER = "outer"
    RANDOM = "random"

class SwwwTransitionPosition(Enum):
    CENTER = "center"
    TOP = "top"
    LEFT = "left"
    RIGHT = "right"
    BOTTOM = "bottom"
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"


@dataclass
class SWWW:
    resize: Optional[SwwwResize] = SwwwResize.CROP
    fill_color: Optional[HexColor] = "#000000"
    filter: Optional[SwwwFilter] = SwwwFilter.LANCZOS3
    transition_type: Optional[SwwwTransitionType] = SwwwTransitionType.SIMPLE
    transition_step: Optional[int] = 90
    transition_duration: Optional[int] = 3
    transition_fps: Optional[int] = 30
    transition_angle: Optional[int] = 45
    transition_pos: Optional[SwwwTransitionPosition] = SwwwTransitionPosition.CENTER
    invert_y: Optional[bool] = False
    # transition_bezier: tuple[float, float, float] = [0.54, 0, 0.34, 0.99]
    # transition_wave: tuple[int, int] = [20, 20]


    def _transform_option(self, option: str, value: str):
        return f"--{option.replace('_', '-')} {value}"

    def generate_config(self):
        with open(CONFIG_FILE, "w") as file:
            for name, value in asdict(self).items():
                # Handle Enums: Convert to their string representation
                if isinstance(value, Enum):
                    value = value.value
                # Handle booleans as lowercase strings
                elif isinstance(value, bool):
                    value = str(value).lower()
                # Write to the file
                file.write(f"sww_{name}={value}\n")


    def build_command(self) -> str:
        command = []
        for name, value in asdict(self).items():            
            if isinstance(value, Enum):
                value = value.value
            elif isinstance(value, str) and "#" in value:
                value = value[1:]
            command.append(self._transform_option(name, value))
        # TODO add img
        return f"swww img {' '.join(command)}"


ret = SWWW().generate_config()
print(ret)


# TODO chec file 
    # if it exit
      # read data from iot
    # if it does not
      # create it and generate it from the dataclass value


# TODO the ui should call the dataclass and the dataclass recreates the files
