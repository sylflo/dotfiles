from fabric import Application
from fabric.widgets.datetime import DateTime
from fabric.widgets.box import Box
from fabric.widgets.eventbox import EventBox
from fabric.widgets.button import Button
from fabric.widgets.shapes.corner import Corner
from fabric.widgets.shapes.star import Star
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


from rounded_image import CustomImage
from gi.repository import Gtk, GLib
from settings import WallpaperSettings

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
    for monitor in monitors:
        os.system(f"swww img -o \"{monitor}\" --transition-type fade --transition-duration 10 --transition-fps 120 ./images/{image_name}")



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
                child=CustomImage(image_file=f"{DIRECTORY}/{image}", size=250).build().add_style_class("img").unwrap(),
            )
            event_box.connect("button-press-event", lambda widget, event, img=image: on_image_click(widget, event, img))
            # event_box.connect("button-press-event", on_image_click)
            self.add(event_box)


def open_settings(widget, *kwargs):
    settings = WallpaperSettings()
    settings.show_all()



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
        button = Button(label="Open settings", on_clicked=lambda b, *args: open_settings(b, args))
        box = Box(
            orientation="vertical",
            children=[Box(children=[button]), MonitorsRow()] + [WallpaperRow(images=row) for row in self.get_images()]
        )

        self.revealer = Revealer(transition_type='crossfade', transition_duration=2000)
        self.revealer.add(box)
        self.connect("draw", self.on_draw)

        outer_box = Box(
            name="outer-box",
            #open_inspector=True,
            orientation="vertical",
            children=[self.revealer],
        )

        self.children = ScrolledWindow(
            child=outer_box
        )


    def on_draw(self, *args):
        self.revealer.child_revealed = True



if __name__ == "__main__":
    wallpaper = Wallpaper()
    app = Application("wallpaper", wallpaper)
    app.set_stylesheet_from_file(get_relative_path("./style.css"))
    app.run()


# TODO show animation whjen qwuitting
# def on_close(self, *args):
#     self.revealer.set_reveal_child(False)
#     GLib.timeout_add(1000, Gtk.main_quit)  # Delay quitting to let the animation complete
#     return True  # Prevent default close behavior