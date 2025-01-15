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

from pathlib import Path


class BaseRow(Box):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="horizontal",
            h_align="center",
            v_align="fill",
            **kwargs,
        )

class WallpaperRow(BaseRow):
    def __init__(self, wallpapers_folder: Path, img_size: int, images, **kwargs):
        super().__init__(**kwargs)
        for image in images:
            event_box = EventBox(
                events="button-press",
                child=Image(image_file=f"{wallpapers_folder}/{image}", size=img_size).build().add_style_class("img").unwrap(),
            )
            #event_box.connect("button-press-event", lambda widget, event, img=image: on_image_click(widget, event, img))
            # event_box.connect("button-press-event", on_image_click)
            self.add(event_box)


class MonitorsRow(BaseRow):
    def __init__(self, monitors: list[str], img_size: int, **kwargs):
        super().__init__(**kwargs)
        for monitor in monitors:
            event_box = EventBox(
                events="button-press",
                child=Box(
                    children=[
                        Overlay(
                            child=Image(
                                # TODO should not be hardcoded get it from monitor name
                                image_file="./images/DP-3",
                                size=img_size,
                                ).build().add_style_class("img").unwrap(),
                            overlays=Label(label=monitor)
                        )
                    ]
                )
            )
            self.add(event_box)
            #event_box.connect("button-press-event", lambda widget, event, monitor=monitor: on_screen_click(widget, event, monitor))


class MainContent(Box):
    def __init__(self, wallpaper_folder: Path, img_size: int, monitor_size: int, monitors, wallpaper_rows, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        settings_button = Button(label="Open settings")
        self.add(Box(children=[settings_button]))

        self.add(MonitorsRow(monitors, monitor_size))
        for row in wallpaper_rows:
            self.add(WallpaperRow(wallpaper_folder, img_size, images=row))


class Wallpaper(Window):
    def __init__(self, wallpapers_folder: Path, img_size: int, monitor_size: int, monitors: list[str], wallpaper_rows: list[list[str]], **kwargs):
        super().__init__(
            layer="top",
            anchor="left bottom top right",
            exclusivity="auto",
            **kwargs
        )
        main_content = MainContent(wallpapers_folder, img_size, monitor_size, monitors, wallpaper_rows)

        self.revealer = Revealer(transition_type='crossfade', transition_duration=2000, child=main_content)
        self.connect("draw", self.on_draw)

        outer_box = Box(
            name="outer-box",
            orientation="vertical",
            children=[self.revealer],
        )

        self.children = ScrolledWindow(
            child=outer_box
        )


    def on_draw(self, *args):
        self.revealer.child_revealed = True
