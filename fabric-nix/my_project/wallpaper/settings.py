from fabric import Application
from fabric.widgets.wayland import WaylandWindow as Window
from combobox import ComboBox
from fabric.widgets.label import Label
from fabric.widgets.box import Box
from fabric.widgets.scale import Scale, ScaleMark
from fabric.widgets.scrolledwindow import ScrolledWindow

import textwrap
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from separator import Separator
from fabric.utils import invoke_repeater, get_relative_path



# TODO add tooltip and get it from the help, just copy paste => Description
# TODO disable/enable optins in function of value of animation
class WallpaperSettings(Window):
    def __init__(self, **kwargs):
        super().__init__(
            #layer="top",
            anchor="left top right",
            #anchor="left bottom top right",
            #exclusivity="auto",
            **kwargs
        )
        # TODO add random stuff for all value when possible
        # TODO add submit button and store value in a text
        scale_1 = Scale(
            value=90, min_value=0, max_value=255,
        )
        scale_2 = Scale(
            value=10, min_value=0, max_value=300,
        )
        box = Box(
            name="outer-box",
            open_inspector=True,
            orientation="vertical",
            children=[
                Separator(orientation="horizontal"),
                Label(label="SWWW Settings").build().add_style_class("title").unwrap(),
                Separator(orientation="horizontal"),

                  #     --fill-color <FILL_COLOR>
  #         Which color to fill the padding with when output image does not fill screen
          
  #         [default: 000000]

                #.build().add_style_class("img").unwrap()
                # Resize
                Box(
                    h_align="center",
                    orientation="vertical",
                    children=[
                        Separator(orientation="horizontal"),
                        Label(h_align="start", label="Resize").build().add_style_class("label-title").unwrap(),
                        # Label(h_align="start", label="""
                        # plpo
                        # """).build().add_style_class("label-descriptio").unwrap(),
                        Label(h_align="start", label=textwrap.dedent("""
                            - no:   Do not resize the image
                            - crop: Resize the image to fill the whole screen, cropping out parts that don't fit
                            - fit:  Resize the image to fit inside the screen, preserving the original aspect ratio
                        """)).build().add_style_class("label-description").unwrap(),
                        ComboBox(items=["no", "crop", "fit"]),

                        # TODO Fill color
                        Separator(orientation="horizontal"),
                        Label(label="Fill color"),

                        # Filter
                        Separator(orientation="horizontal"),
                        Label(label="Filter"),
                        ComboBox(items=["Nearest", "Bilinear", "CatmullRom", "Mitchell", "Lanczos3"]),

                        # Transition type
                        Separator(orientation="horizontal"),

                        Label(label="Transition type"),
                        ComboBox(items=["none", "simple", "fade", "left", "right", "top", "bottom", "wipe", "wave", "grow", "center", "any", "outer", "random"]),

                        # Transtion step
                        Separator(orientation="horizontal"),
                        Label(label="Transition step"),
                        scale_1,

                        # Transtion duration
                        Separator(orientation="horizontal"),
                        Label(label="Transition duration (in seconds)"),
                        scale_2,
                        Label(label=f"value is {scale_2.get_value()}"),

                        # Transition fps
                        Separator(orientation="horizontal"),
                        Label(label="Transition fps"),
                        Scale(value=90, min_value=0, max_value=1000),

                        # Transition angle
                        Separator(orientation="horizontal"),
                        Label(label="Transition angle"),
                        Scale(value=0, min_value=0, max_value=360),

                        # Transition pos
                        Separator(orientation="horizontal"),
                        Label(label="Transition pos in %"),
                        Scale(value=0, min_value=0, max_value=100),

                        # Invert Y
                        Separator(orientation="horizontal"),
                        Label(label="Invert the Y")
                ]),


                # TODO booelan
  #     --transition-bezier <TRANSITION_BEZIER>
  #         bezier curve to use for the transition https://cubic-bezier.com is a good website to get these values from
          
  #         eg: 0.0,0.0,1.0,1.0 for linear animation
          
  #         [env: SWWW_TRANSITION_BEZIER=]
  #         [default: .54,0,.34,.99]

  #     --transition-wave <TRANSITION_WAVE>
  #         currently only used for 'wave' transition to control the width and height of each wave
          
  #         [env: SWWW_TRANSITION_WAVE=]
  #         [default: 20,20]
            ],
        )
        self.add(box)


if __name__ == "__main__":
    settings = WallpaperSettings()
    app = Application("wallpaper-settings", settings)
    app.set_stylesheet_from_file(get_relative_path("./style.css"))
    app.run()
