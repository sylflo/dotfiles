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
        self, service, wallpapers_folder: Path, images, **kwargs
    ):
        #raise Exception(wallpapers_folder, images)
        super().__init__(**kwargs)
        for image_name in images:
            image = Image(image_file=f"{wallpapers_folder}/{image_name}", size=SETTINGS.layout.img_max_width)
            event_box = EventBox(
                on_button_press_event=lambda widget, _, image_name=image_name: service.select_image(
                    widget, image_name
                ),
                child=image.build().add_style_class("img").unwrap(),
            )
            self.add(event_box)


class MonitorSection(BaseRow):
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


class WallpaperSection(ScrolledWindow):

    def __init__(self, service, wallpaper_rows, **kwargs):
        super().__init__(
            min_content_size=(SETTINGS.layout.scroll_min_width, SETTINGS.layout.scroll_min_height),
            max_content_size=(SETTINGS.layout.scroll_max_width, SETTINGS.layout.scroll_max_height),
            **kwargs
        )

        self.wallpaper_rows = [
            WallpaperRow(
                service,
                SETTINGS.main.cache_folder / "images",
                images=row,
            ) for row in wallpaper_rows]

        self.add(
            Box(
                orientation="vertical",
                children=self.wallpaper_rows,
            )
        )

    def get_wallpaper_rows(self) -> WallpaperRow:
        return self.wallpaper_rows

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
                        service, SETTINGS.main.cache_folder / "images", images=row
                    ).build().add_style_class("wallpaper-row").unwrap()
                    for row in wallpaper_rows
                ]
            ),
        )
        #raise Exception("FUCK")
        self.connect("draw", self.on_draw)
        box = CenterBox(
            center_children=self.revealer,
        )
        self.children = [box]

    def on_draw(self, *args):
        if self.revealer:
            self.revealer.child_revealed = True

class PaginationSection(Box):
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
        anchor = "left bottom top right" if SETTINGS.main.fullscreen else "top left"
        super().__init__(
            size=SETTINGS.layout.window_size,
            anchor=anchor,
            exclusivity="auto",
            keyboard_mode="on-demand",
            **kwargs
        )
        self.set_resizable(False)

        self.pagination = None
        self.wallpaper_section = WallpaperSection(service, wallpaper_rows)
        self.monitor_section = MonitorSection(
            service, SETTINGS.config_file, monitors, SETTINGS.layout.monitor_img_size
        )
        self.layout = CenterBox(
            orientation='vertical',
            start_children=self.monitor_section,
            center_children=self.wallpaper_section,
        )

        self.revealer = Revealer(
            transition_type=SETTINGS.animation.init_transition_type,
            transition_duration=SETTINGS.animation.init_transition_duration,
            child=self.layout,
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
            self.pagination = PaginationSection(service, total_pages)
            self.layout.end_children = self.pagination
            self.children = outer_box
        else:
            self.children = outer_box


    def set_selected_monitor(self, widget):
        widget.add_style_class("selected-screen")

    def set_unselected_monitor(self, widget):
        widget.remove_style_class("selected-screen")

    def set_selected_image(self, widget):
        for row in self.wallpaper_section.get_wallpaper_rows():
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
        self.wallpaper_section.update_wallpaper_rows(service, action, wallpaper_rows)
        self.pagination.reset_pagination(page_index)

    def add_wallpaper_rows(self, pixbuf, filepath):
        self.wallpaper_section.children[0].get_child().add(Image(pixbuf=pixbuf))

    def on_draw(self, *args):
        self.revealer.child_revealed = True
