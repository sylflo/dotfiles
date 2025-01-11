from fabric import Application
from fabric.widgets.datetime import DateTime
from fabric.widgets.box import Box
from fabric.widgets.eventbox import EventBox
from fabric.widgets.button import Button
from fabric.widgets.label import Label
from fabric.widgets.overlay import Overlay
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.revealer import Revealer
from fabric.widgets.image import Image
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.utils import invoke_repeater, get_relative_path
import os
import subprocess
import json
import time


# TODO change image screen when changing wallapper
# TODO move image screen to ./images/screens
# TODO image DP-3 ands HDMI-A-1 put in another directoy
# TODO  change this should be configurable
DIRECTORY = "./images"


# TODO remove global
IMAGE_SELECTED = {'name': None, 'widget': None}# {image_name: wisdgert}
SCREENS_SELECTED = {}

def set_wallpaper(monitors: list[str], image_name: str):
    if image_name is None:
        ...
    # TODO pass image as parameter
    for monitor in monitors:
        # os.system(f"swww img -o \"{monitor}\" --transition-type random ./images/{image_name}")
        os.system(f"swww img -o \"{monitor}\" --transition-type fade --transition-duration 10 --transition-fps 120 ./images/{image_name}")
        #swww img --transition-type fade --transition-duration 3000 --transition-fps 120 wallpaper.jpg
    #subprocess.run(["ls", "-l"])
    #swww img -o "DP-2" --transition-type random /tmp/output-0.png
    #swww img -o "DP-1" --transition-type random /tmp/output-1.png


def on_screen_click(widget, event, monitor, *args):
    global SCREENS_SELECTED

    selected_monitor = SCREENS_SELECTED.pop(monitor, None)
    if selected_monitor:
        selected_monitor.remove_style_class("selected-screen")
    else:
        widget.add_style_class("selected-screen")
        SCREENS_SELECTED[monitor] = widget

    set_wallpaper(SCREENS_SELECTED.keys(), IMAGE_SELECTED['name'])


def on_image_click(widget, event, image, *args):
    global IMAGE_SELECTED

    if  IMAGE_SELECTED['name']:
        IMAGE_SELECTED['widget'].remove_style_class("selected-image")
        IMAGE_SELECTED = {
            'name': None,
            'widget': None
        }

    widget.add_style_class("selected-image")
    IMAGE_SELECTED = {
        'name': image,
        'widget': widget
    }
    set_wallpaper(SCREENS_SELECTED.keys(), IMAGE_SELECTED['name'])


class MonitorsRow(Box):
    def get_monitors(self) -> list[str]:
        # TODO should work with sway
        result = subprocess.run(["hyprctl", "-j", "monitors"], capture_output=True, text=True)
        return [monitor['name'] for monitor in json.loads(result.stdout)]

    def __init__(self, **kwargs):
        super().__init__(
            orientation="horizontal",
            h_align="center",
            v_align="fill",
            **kwargs,
        )
        for monitor in self.get_monitors():
            event_box = EventBox(
                events="button-press",
                child=Box(
                    children=[
                        Overlay(
                            child=Image(
                                # TODO should not be hardcoded get it from monitor name
                                image_file="./images/DP-3",
                                size=250,
                                ).build().add_style_class("img").unwrap(),
                            overlays=Label(label=monitor)
                        )
                    ]
                )
            )
            self.add(event_box)
            event_box.connect("button-press-event", lambda widget, event, monitor=monitor: on_screen_click(widget, event, monitor))


class WallpaperRow(Box):
    def __init__(self, images, **kwargs):
        super().__init__(
            orientation="horizontal",
            h_align="center",
            v_align="fill",
            **kwargs,
        )
        for image in images:
            event_box = EventBox(
                events="button-press",
                child=Image(image_file=f"{DIRECTORY}/{image}", size=250).build().add_style_class("img").unwrap(),
            )
            event_box.connect("button-press-event", lambda widget, event, img=image: on_image_click(widget, event, img))
            # event_box.connect("button-press-event", on_image_click)
            self.add(event_box)


class Wallpaper(Window):
    # TODO maybe use something like ~/.config/wallpapers
    def get_images(self, folder=DIRECTORY, image_per_row=3):
        images = os.listdir(folder)
        rows = [images[i:i + image_per_row] for i in range(0, len(images), image_per_row)]
        return rows

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
            children=[MonitorsRow()] + [Revealer(child=WallpaperRow(images=row), child_revealed=True) for row in self.get_images()],
        )

        self.children = ScrolledWindow(
            child=outer_box
        )



if __name__ == "__main__":
    wallpaper = Wallpaper()
    app = Application("wallpaper", wallpaper)
    app.set_stylesheet_from_file(get_relative_path("./style.css"))
    #time.sleep(10)
    app.run()
