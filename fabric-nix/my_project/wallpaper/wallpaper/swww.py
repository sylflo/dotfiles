from dataclasses import asdict, dataclass, fields
from enum import Enum
from typing import Optional

import re

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
    resize: SwwwResize = SwwwResize.CROP
    fill_color: HexColor = "#000000"
    filter: SwwwFilter = SwwwFilter.LANCZOS3
    transition_type: SwwwTransitionType = SwwwTransitionType.SIMPLE
    transition_step: int = 90
    transition_duration: int = 3
    transition_fps: int = 30
    transition_angle: int = 45
    transition_pos: SwwwTransitionPosition = SwwwTransitionPosition.CENTER
    # # TODO
    # invert_y: bool = False
    # # TODO correct this
    # transition_bezier: tuple[float, float, float] = [0.54, 0, 0.34, 0.99]
    # transition_wave: tuple[int, int] = [20, 20]


    def _transform_option(self, option: str, value: str) -> list[str]:
        return [f"--{option.replace('_', '-')}", str(value)]

    def build_command(self, monitor_name: str, image_path: str) -> str:
        command = ["swww", "img", "-o", monitor_name]
        for name, value in asdict(self).items():            
            if isinstance(value, Enum):
                value = value.value
            elif isinstance(value, str) and "#" in value:
                value = value[1:]
            command.extend(self._transform_option(name, value))
        command.append(image_path)
        return command
