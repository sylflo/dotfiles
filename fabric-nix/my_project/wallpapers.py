from fabric import Application
from fabric.widgets.datetime import DateTime
from fabric.widgets.box import Box
from fabric.widgets.eventbox import EventBox
from fabric.widgets.button import Button
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.image import Image
from fabric.widgets.label import Label
from fabric.widgets.wayland import WaylandWindow as Window  # Replace the previous Window import with this
from fabric.utils import invoke_repeater, get_relative_path
import os
import subprocess

# TODO separate component using class check example https://github.com/Fabric-Development/fabric/blob/c81e4f148add9d2d15820a4a1a704931315f24de/examples/bar/config.py#L51
# TODO change cursor
# TODO type evetything
#TODO maybe use sytle classes instead of 
# Image(image_file="./images/36592_serial_experiments_lain.png", size=250).build().add_style_class("img").unwrap(
# TODO add border radius om img except screens => img need to be set as bacgkround :/

# TODO add screen name as overly on screens image
# TODO add animations
# TODO put in blue screeen(selected) then click on image and call  set_wallpaper function

def set_wallpaper(monitor_name: str):
    # TODO pass image as parameter
    # TODO maybe use a proepr function
    # TODO change image ./image/monitor.extension
    os.system(f"swww img -o \"{monitor_name}\" --transition-type random ./images/cute-town-dark.png")
    #subprocess.run(["ls", "-l"])
    #swww img -o "DP-2" --transition-type random /tmp/output-0.png
    #swww img -o "DP-1" --transition-type random /tmp/output-1.png


def on_button_click(button, *args):
    #raise Exception("HEY YOU")
    os.system(f"swww img -o \"DP-3\" --transition-type random ./images/7l1gtm3m5gv51.jpg")



def generate_box():
    return Box(
        orientation="horizontal",
        h_align="center",
        v_align="fill",
        children=[
            Image(image_file="./images/36592_serial_experiments_lain.png", size=250).build().add_style_class("img").unwrap(),
            Image(image_file="./images/black-white-girl.png", size=250).build().add_style_class("img").unwrap(),
            Image(image_file="./images/fantasy-woods.jpg", size=250).build().add_style_class("img").unwrap(),
            Image(image_file="./images/black-white-girl.png", size=250).build().add_style_class("img").unwrap(),
        ]
    )

def monitors_box():
    eventbox = EventBox(events="button-press",child=Image(image_file="./images/hdmi_a_1.jpg", size=250).build().add_style_class("img").unwrap())
    ret = Box(
        orientation="horizontal",
        h_align="center",
        v_align="fill",
        children=[
            eventbox,
            Image(image_file="./images/hdmi_a_1.jpg", size=250).build().add_style_class("img").unwrap(),
        ]
    )
    eventbox.connect("button-press-event", on_button_click)
    return ret

def get_monitors():
    return ["DP-3", "HDMI-A-1"]
    # TOPDO shoulds work wirth sway also
    # hyprctl -j monitors

class Wallpaper(Window):

  def __init__(self, **kwargs):
    super().__init__(
      layer="top",
      anchor="left bottom top right",
      exclusivity="auto",
      **kwargs
    )


    outer_box = Box(
        name="outer-box",
        open_inspector=True,
        orientation="vertical",
        children=[
            monitors_box(),
            generate_box(),
            generate_box(),
            generate_box(),
            generate_box(),
            generate_box(),
            generate_box(),
        ]
    )

    self.children = ScrolledWindow(
        child=outer_box
    )


if __name__ == "__main__":
    wallpaper = Wallpaper()
    app = Application("wallpaper", wallpaper)
    app.set_stylesheet_from_file(get_relative_path("./style.css"))
    app.run()
