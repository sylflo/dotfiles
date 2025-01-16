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

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from gi.repository import GdkPixbuf



class BaseRow(Box):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="horizontal",
            h_align="center",
            v_align="fill",
            **kwargs,
        )

class WallpaperRow(BaseRow):
    def __init__(self, service, wallpapers_folder: Path, img_size: int, images, **kwargs):
        super().__init__(**kwargs)
        for image in images:
            event_box = EventBox(
                on_button_press_event=lambda widget, _, image_name=image: service.select_image(widget, image_name),
                child=Image(image_file=f"{wallpapers_folder}/{image}", size=img_size).build().add_style_class("img").unwrap(),
            )
            self.add(event_box)


class MonitorsRow(BaseRow):
    def __init__(self, service, config_file, monitors: list[str], img_size: int, **kwargs):

        super().__init__(**kwargs)
        for monitor in monitors:
            if os.path.exists(f"{config_file}/{monitor}"):
                image_name = f"{config_file}/{monitor}"
            else:
                image_name = "./images/default.png"
            event_box = EventBox(
                on_button_press_event=lambda widget, _, monitor_name=monitor: service.select_monitor(widget, monitor_name),
                child=Box(
                    children=[
                        Overlay(
                            child=Image(
                                image_file=image_name,
                                size=img_size,
                                ).build().add_style_class("img").unwrap(),
                            overlays=Label(label=monitor)
                        )
                    ]
                )
            )
            self.add(event_box)


class MainContent(Box):
    def __init__(self, service, settings, monitors, wallpaper_rows, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.add(MonitorsRow(service, settings.config_file, monitors, settings.monitor_img_size))
        for row in wallpaper_rows:
            self.add(WallpaperRow(service, settings.wallpapers_folder, settings.wallpaper_img_size, images=row))

    def update(self, settings, wallpaper_rows):
        self.children = [self.children[0]] + [WallpaperRow(settings.wallpapers_folder, settings.wallpaper_img_size, images=row) for row in wallpaper_rows] + [self.children[-1]]


class Pagination(Box):
    def __init__(self, service, nb_pages: int, **kwargs):
        super().__init__(
            name="pagination",
            orientation="horizontal",
            h_align="center",
            children=[Button(label="Previous", on_clicked=lambda widget: service.previous_page())] +
                [Button(label=str(i), on_clicked=lambda widget, page=i: service.go_to_page(page)) for i in range(1, nb_pages + 1)] +
                [Button(label="Next", on_clicked=lambda widget: service.next_page())],
            **kwargs
        )


class Wallpaper(Window):
    def __init__(self, settings, service, total_pages: int, monitors: list[str], wallpaper_rows: list[list[str]], **kwargs):
        super().__init__(
            layer="top",
            anchor="left bottom top right",
            exclusivity="auto",
            keyboard_mode='on-demand',
            **kwargs
        )
        self.settings = settings

        self.main_content = MainContent(service, settings, monitors, wallpaper_rows)
        if settings.pagination:
            self.main_content.add(Pagination(service, total_pages))

        self.revealer = Revealer(transition_type=settings.transition_type, transition_duration=settings.transition_duration, child=self.main_content)
        self.connect("draw", self.on_draw)
        outer_box = Box(
            orientation="vertical",
            children=[self.revealer],
        )
        if settings.background_img:
            outer_box.add_style_class("background-img")
        else:
            outer_box.add_style_class("background-color")

        if settings.pagination:
            self.children = outer_box
        else:
            self.children = ScrolledWindow(
                child=outer_box
            )

    def set_selected_monitor(self, widget):
        for child in self.main_content.children[0].children:
            if isinstance(child, EventBox):
                child.remove_style_class("selected-screen")
        widget.add_style_class("selected-screen")


    def set_selected_image(self, widget):
        for child in self.main_content.children[1]:
            if isinstance(child, EventBox):
                child.remove_style_class("selected-image")
        widget.add_style_class("selected-image")

    def update_monitor_image(self, monitor, image_name):

        image_widget = monitor.children[0].children[0].children[0]
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            f"{self.settings.wallpapers_folder}/{image_name}",
            width=self.settings.monitor_img_size,
            height=self.settings.monitor_img_size,
        )
        image_widget.set_from_pixbuf(pixbuf)

    def update_content(self, settings, page_index, wallpaper_rows):
        # page_index # TODO show curretn selected page
        self.main_content.update(settings, wallpaper_rows)

    def on_draw(self, *args):
        self.revealer.child_revealed = True
