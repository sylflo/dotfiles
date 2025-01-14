from widgets.combobox import ComboBox

from dataclasses import dataclass
from fabric.widgets.widget import Widget
from fabric.widgets.entry import Entry


@dataclass
class Options:
    title: str
    content: str
    widget: Widget


def toto(text: str):
    raise Exception("PLOP")

OPTIONS = [
    Options(
        title="Resize",
        content="Specifies resizing behavior—options include no resize, crop to fit the screen, or scale to fit while maintaining aspect ratio",
        widget=ComboBox(items=["no", "crop", "fit"]),
    ),
    # TODO fill color add colorpicker
    # Options(
    #     title=
    #     content=
    #     widget=
    # ),
    Options(
        title="Filter",
        content="Determines the scaling filter for resizing, with options optimized for pixel art or general use",
        # TODO use enum
        widget=ComboBox(items=["Nearest", "Bilinear", "CatmullRom", "Mitchell", "Lanczos3"]),
    ),
    Options(
        title="Transition type",
        content="Chooses the type of image transition effect, such as fade, wipe, wave, or random effects",
        # TODO use enum
        widget=ComboBox(items=["none", "simple", "fade", "left", "right", "top", "bottom", "wipe", "wave", "grow", "center", "any", "outer", "random"]),
    ),
    Options(
        title="Transition step",
        content="Controls how quickly the RGB values change during transitions; higher values make it faster and more abrupt",
        widget=Entry(
            placeholder="Search Applications...",
            h_expand=True,
            notify_text=lambda entry, *_: toto(entry.get_text()),
        )
        #widget=Entry(),
    ),
    Options(
        title="Transition duration",
        content="Specifies the duration (in seconds) for completing transitions, excluding the 'simple' type.",
        widget=Entry(),
    ),
    Options(
        title="Transition fps",
        content="Sets the frame rate for transition animations, ideally matching the monitor's refresh rate",
        widget=Entry(),
    ),
    Options(
        title="Transition angle",
        content="Defines the angle for 'wipe' and 'wave' transitions, with 0° for horizontal and 90° for vertical",
        widget=Entry(),
    ),
    Options(
        title="Transition position",
        content=" Sets the center position for circular transitions, using percentages, pixels, or aliases like 'center'",
        widget=Entry(),
    ),
    # TODO invert add checkbox
    # Option(
    #     title="Transition position",
    #     content=" Sets the center position for circular transitions, using percentages, pixels, or aliases like 'center'",
    #     widget=Entry(),
    # ),
    Options(
        title="Transition bezier",
        content="Applies a custom bezier curve for the transition animation, offering fine control over timing",
        widget=Entry(),
    ),
    Options(
        title="Transition wave",
        content="Configures the width and height of the wave in 'wave' transitions",
        widget=Entry(),
    )
]
