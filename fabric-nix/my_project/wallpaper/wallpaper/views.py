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


# def set_wallpaper(monitors: list[str], image_name: str):
#     if image_name is None:
#         ...
#     # TODO pass image as parameter
#     for monitor in monitors:
#         # os.system(f"swww img -o \"{monitor}\" --transition-type random ./images/{image_name}")
#         os.system(f"swww img -o \"{monitor}\" --transition-type fade --transition-duration 10 --transition-fps 120 ./images/{image_name}")
#         #swww img --transition-type fade --transition-duration 3000 --transition-fps 120 wallpaper.jpg
#     #subprocess.run(["ls", "-l"])
#     #swww img -o "DP-2" --transition-type random /tmp/output-0.png
#     #swww img -o "DP-1" --transition-type random /tmp/output-1.png
# def on_screen_click(widget, event, monitor, *args):
#     global SCREENS_SELECTED
#     selected_monitor = SCREENS_SELECTED.pop(monitor, None)
#     if selected_monitor:
#         selected_monitor.remove_style_class("selected-screen")
#     else:
#         widget.add_style_class("selected-screen")
#         SCREENS_SELECTED[monitor] = widget
#     set_wallpaper(SCREENS_SELECTED.keys(), IMAGE_SELECTED['name'])
# def on_image_click(widget, event, image, *args):
#     global IMAGE_SELECTED
#     if  IMAGE_SELECTED['name']:
#         IMAGE_SELECTED['widget'].remove_style_class("selected-image")
#         IMAGE_SELECTED = {
#             'name': None,
#             'widget': None
#         }
#     widget.add_style_class("selected-image")
#     IMAGE_SELECTED = {
#         'name': image,
#         'widget': widget
#     }
#     set_wallpaper(SCREENS_SELECTED.keys(), IMAGE_SELECTED['name'])



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
    def __init__(self, settings, monitors, wallpaper_rows, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.add(MonitorsRow(monitors, settings.monitor_img_size))
        for row in wallpaper_rows:
            self.add(WallpaperRow(settings.wallpapers_folder, settings.wallpaper_img_size, images=row))

    def update(self, settings, wallpaper_rows):
        self.children = [self.children[0]] + [WallpaperRow(settings.wallpapers_folder, settings.wallpaper_img_size, images=row) for row in wallpaper_rows] + [self.children[-1]]


class Pagination(Box):
    def __init__(self, pagination_service, nb_pages: int, **kwargs):
        super().__init__(
            name="pagination",
            orientation="horizontal",
            h_align="center",
            children=[Button(label="Previous", on_clicked=lambda widget: pagination_service.previous_page())] +
                [Button(label=str(i)) for i in range(1, nb_pages + 1)] +
                [Button(label="Next", on_clicked=lambda widget: pagination_service.next_page())],
            **kwargs
        )

class Wallpaper(Window):
    def __init__(self, settings, pagination_service, total_pages: int, monitors: list[str], wallpaper_rows: list[list[str]], **kwargs):
        super().__init__(
            layer="top",
            anchor="left bottom top right",
            exclusivity="auto",
            **kwargs
        )
        self.main_content = MainContent(settings, monitors, wallpaper_rows)
        if settings.pagination:
            self.main_content.add(Pagination(pagination_service, total_pages))

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


    def update_content(self, settings, wallpaper_rows):
        self.main_content.update(settings, wallpaper_rows)

      
    # TODO use service
    def on_draw(self, *args):
        self.revealer.child_revealed = True
