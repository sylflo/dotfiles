from pathlib import Path

import gi
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.eventbox import EventBox
from fabric.widgets.image import Image
from fabric.widgets.label import Label
from fabric.widgets.overlay import Overlay
from fabric.widgets.revealer import Revealer
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.scrolledwindow import ScrolledWindow

from wallpaper.models import SETTINGS


gi.require_version("Gtk", "3.0")
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
    def __init__(
        self, service, wallpapers_folder: Path, img_size: int, images, **kwargs
    ):
        super().__init__(**kwargs)
        max_width = 200
        max_height = 200
        for image in images:
            # Load and resize the image while maintaining aspect ratio
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(f"{wallpapers_folder}/{image}")
            original_width = pixbuf.get_width()
            original_height = pixbuf.get_height()
            width_ratio = max_width / original_width
            height_ratio = max_height / original_height
            scale_ratio = min(width_ratio, height_ratio)
            new_width = int(original_width * scale_ratio)
            new_height = int(original_height * scale_ratio)
            scaled_pixbuf = pixbuf.scale_simple(new_width, new_height, GdkPixbuf.InterpType.BILINEAR)
            image = Image(image_file=f"{wallpapers_folder}/{image}")
            image.set_from_pixbuf(scaled_pixbuf)

            event_box = EventBox(
                on_button_press_event=lambda widget, _, image_name=image: service.select_image(
                    widget, image_name
                ),
                child=image.build().add_style_class("img").unwrap(),
            )
            self.add(event_box)


class MonitorsRow(BaseRow):
    def __init__(
        self, service, config_file, monitors: list[str], img_size: int, **kwargs
    ):

        super().__init__(**kwargs)
        for monitor in monitors:
            image = Path(config_file).parent / monitor
            if image.exists():
                image_name = str(image)
            else:
                image_name = "./images/default.png"
            event_box = EventBox(
                on_button_press_event=lambda widget, _, monitor_name=monitor: service.select_monitor(
                    widget, monitor_name
                ),
                child=Box(
                    children=[
                        Overlay(
                            child=Image(
                                image_file=image_name,
                                size=img_size,
                            )
                            .build()
                            .add_style_class("img")
                            .unwrap(),
                            overlays=Label(label=monitor),
                        )
                    ]
                ),
            )
            self.add(event_box)


class MainContent(Box):
    def __init__(self, service, monitors, wallpaper_rows, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        wallpaper_rows = [
            WallpaperRow(
                service,
                SETTINGS.main.wallpapers_folder,
                SETTINGS.layout.wallpaper_img_size,
                images=row,
            ) for row in wallpaper_rows]

        self.add(
            MonitorsRow(
                service, SETTINGS.config_file, monitors, SETTINGS.layout.monitor_img_size
            )
        )

        self.add(ScrolledWindow(
            min_content_size=(280, 320),
            max_content_size=(1000, 1000),
            child=Box(
                orientation="vertical",
                children=wallpaper_rows,
            )
        ))

    def get_wallpaper_rows(self) -> WallpaperRow:
        return self.children[1:-1]

    def get_monitors_row(self) -> MonitorsRow:
        return self.children[0]

    def get_pagination_row(self):
        return self.children[-1]

    def update_wallpaper_rows(self, service, action, wallpaper_rows):
        if action == 'next':
            transition_type = SETTINGS.animation.next_transition_type
            transition_duration = SETTINGS.animation.next_transition_duration       
        else:
            transition_type = SETTINGS.animation.prev_transition_type
            transition_duration = SETTINGS.animation.prev_transition_duration       
        self.revealer = Revealer(
            transition_type=transition_type,
            transition_duration=transition_duration,
            child=Box(
                orientation="vertical",
                children=[
                    WallpaperRow(
                        service, SETTINGS.main.wallpapers_folder, SETTINGS.layout.wallpaper_img_size, images=row
                    )
                    for row in wallpaper_rows
                ]
            ),
        )
        self.connect("draw", self.on_draw)
        box = CenterBox(
            center_children=self.revealer,
        )
        self.children = (
            [self.get_monitors_row()]
            + [box]
            + [self.get_pagination_row()]
        )

    def on_draw(self, *args):
        if self.revealer:
            self.revealer.child_revealed = True

class Pagination(Box):
    def __init__(self, service, nb_pages: int, **kwargs):
        self.max_pages = nb_pages

        super().__init__(
            name="pagination",
            orientation="horizontal",
            h_align="center",
            children=[
                Button(
                    label="Previous", on_clicked=lambda widget: service.previous_page()
                ).build().add_style_class("pagination-button").unwrap()
            ]
            + [
                Button(
                    label=str(i),
                    on_clicked=lambda widget, page=(i): service.go_to_page(page),
                ).build().add_style_class("pagination-button").unwrap()
                for i in range(1, nb_pages + 1)
            ]
            + [Button(label="Next", on_clicked=lambda widget: service.next_page()).build().add_style_class("pagination-button").unwrap()],
            **kwargs,
        )
        self.get_prev_button().add_style_class("pagination-disabled")
        self.get_page_button(1).add_style_class("pagination-selected-page")

    def get_prev_button(self):
        return self.children[0]

    def get_next_button(self):
        return self.children[-1]

    def get_all_page_button(self):
        return self.children[1:-1]

    def get_page_button(self, index: int):
        return self.children[index]

    def _update_nav_button(self, button, disabled):
        if disabled:
            button.add_style_class("pagination-disabled")
        else:
            button.remove_style_class("pagination-disabled")     

    def reset_pagination(self, page_index):
        # Prev and next
        self._update_nav_button(self.get_prev_button(), page_index == 1)
        self._update_nav_button(self.get_next_button(), page_index == self.max_pages)

        # Pagination number
        for index, button in enumerate(self.get_all_page_button()):
            if (index + 1) == page_index:
                button.add_style_class("pagination-selected-page")
            else:
                button.remove_style_class("pagination-selected-page")


class Wallpaper(Window):
    def __init__(
        self,
        service,
        total_pages: int,
        monitors: list[str],
        wallpaper_rows: list[list[str]],
        **kwargs,
    ):
        super().__init__(
            size=800,
            anchor="top left",
            # anchor="left bottom top right",
            exclusivity="auto",
            keyboard_mode="on-demand",
            **kwargs
        )
        self.set_resizable(False)  
    
        self.pagination = None
        self.main_content = MainContent(service, monitors, wallpaper_rows)

        self.revealer = Revealer(
            transition_type=SETTINGS.animation.init_transition_type,
            transition_duration=SETTINGS.animation.init_transition_duration,
            child=self.main_content,
        )
        self.connect("draw", self.on_draw)
        outer_box = CenterBox(
            center_children=self.revealer,
        )
        if SETTINGS.layout.background_img:
            outer_box.add_style_class("background-img")
        else:
            outer_box.add_style_class("background-color")

        if SETTINGS.main.pagination:
            self.pagination = Pagination(service, total_pages)
            self.main_content.add(self.pagination)
            self.children = outer_box
        else:
            self.children = outer_box


    def set_selected_monitor(self, widget):
        widget.add_style_class("selected-screen")

    def set_unselected_monitor(self, widget):
        widget.remove_style_class("selected-screen")

    def set_selected_image(self, widget):
        for row in self.main_content.get_wallpaper_rows():
            for child in row:
                if isinstance(child, EventBox):
                    child.remove_style_class("selected-image")
        widget.add_style_class("selected-image")

    def update_monitor_image(self, monitor, image_name):
        image_widget = monitor.children[0].children[0].children[0]
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            f"{SETTINGS.main.wallpapers_folder}/{image_name}",
            width=SETTINGS.layout.monitor_img_size,
            height=SETTINGS.layout.monitor_img_size,
        )
        image_widget.set_from_pixbuf(pixbuf)

    def update_wallpaper_rows(self, service, action, page_index, wallpaper_rows):
        self.main_content.update_wallpaper_rows(service, action, wallpaper_rows)
        self.pagination.reset_pagination(page_index)

    def on_draw(self, *args):
        self.revealer.child_revealed = True
