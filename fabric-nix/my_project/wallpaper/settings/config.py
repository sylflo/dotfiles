from dataclasses import dataclass
from enum import Enum

# @dataclass
# class App:
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


class SwwwResize(Enum):
    NO = "no"
    CROP  = "crop"
    FIT = "fit"


class SwwwFilter(Enum):
    NEAREST = "Nearest"
    BILINEAR = "Bilinear"
    CATMULLROM = "CatmullRom"
    MITCHELL = "Mitechell"
    LANCZOS3 = "Lanzcos3"


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


@dataclass
class SWWW:
    resize: SwwwResize # [default: crop]
    # TODO
    #fill_color: # [default: 000000]
    filter: SwwwFilter #[default: Lanczos3]
    transition_type: SwwwTransitionType # [default: simple]
    transition_step: int # [default: 90]
    transition_duration: int #[default: 3]
    tranistion_fps: int # [default: 30]
    tranistion_angle: int #[default: 45]
    tranistion_pos: int #  [default: center]
    invert_y: bool # Default disable
    transition_bezier: int #  [default: .54,0,.34,.99]
    transition_wave: int # [default: 20,20]

# TODO chec file 
    # if it exit
      # read data from iot
    # if it does not
      # create it and generate it from the dataclass value


# TODO the ui should call the dataclass and the dataclass recreates the files
