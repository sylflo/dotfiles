from pathlib import Path

import gi
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.eventbox import EventBox
from fabric.widgets.image import Image
from fabric.widgets.label import Label
from fabric.widgets.overlay import Overlay
from fabric.widgets.revealer import Revealer
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.widgets.wayland import WaylandWindow as Window

from wallpaper.models import SETTINGS

gi.require_version("Gtk", "3.0")
from gi.repository import GdkPixbuf


# Constants for styles
STYLE_SELECTED_IMAGE = "selected-image"
STYLE_DISABLED = "pagination-disabled"
STYLE_SELECTED_PAGE = "pagination-selected-page"
STYLE_BACKGROUND_COLOR = "background-color"
STYLE_BACKGROUND_IMG = "background-img"
STYLE_SELECTED_SCREEN = "selected-screen"
STYLE_IMG = "img"
STYLE_PAGINATION_BUTTON = "pagination-button"
STYLE_WALLPAPER_ROW = "wallpaper-row"

DEFAULT_IMAGE_PATH = "./images/default.png"


class BaseRow(Box):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="horizontal",
            h_align="center",
            v_align="fill",
            **kwargs,
        )


class WallpaperRow(BaseRow):
    def __init__(self, service, wallpapers_folder: Path, images, **kwargs):
        super().__init__(**kwargs)
        for image_name in images:
            scaled_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                f"{wallpapers_folder}/{image_name}",
                SETTINGS.layout.img_max_width,
                SETTINGS.layout.img_max_height,
                True,
            )
            image = Image(pixbuf=scaled_pixbuf)
            event_box = EventBox(
                on_button_press_event=lambda widget, _, image_name=image_name: service.select_image(
                    widget, image_name
                ),
                child=image.build().add_style_class(STYLE_IMG).unwrap(),
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
                image_name = DEFAULT_IMAGE_PATH
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
                            .add_style_class(STYLE_IMG)
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
            min_content_size=(
                SETTINGS.layout.scroll_min_width,
                SETTINGS.layout.scroll_min_height,
            ),
            max_content_size=(
                SETTINGS.layout.scroll_max_width,
                SETTINGS.layout.scroll_max_height,
            ),
            **kwargs,
        )

        self.wallpaper_rows = [
            WallpaperRow(
                service,
                SETTINGS.main.cache_folder / "images",
                images=row,
            )
            for row in wallpaper_rows
        ]

        self.add(
            Box(
                orientation="vertical",
                children=self.wallpaper_rows,
            )
        )

    def get_wallpaper_rows(self) -> WallpaperRow:
        return self.wallpaper_rows

    def update_wallpaper_rows(self, service, action, wallpaper_rows):
        if action == "next":
            transition_type = SETTINGS.animation.next_transition_type
            transition_duration = SETTINGS.animation.next_transition_duration
        else:
            transition_type = SETTINGS.animation.prev_transition_type
            transition_duration = SETTINGS.animation.prev_transition_duration
        # TODO put revealer in init
        # TODO Modify children rows nore properly
        self.revealer = Revealer(
            transition_type=transition_type,
            transition_duration=transition_duration,
            child=Box(
                orientation="vertical",
                children=[
                    WallpaperRow(
                        service, SETTINGS.main.cache_folder / "images", images=row
                    )
                    .build()
                    .add_style_class(STYLE_WALLPAPER_ROW)
                    .unwrap()
                    for row in wallpaper_rows
                ],
            ),
        )
        self.connect("draw", self.on_draw)
        box = CenterBox(
            center_children=self.revealer,
        )
        self.children = [box]

    def on_draw(self, *args):
        if self.revealer:
            self.revealer.child_revealed = True


class PaginationSection(Box):

    def _create_button(self, label: str, on_click):
        return  Button(label=label, on_clicked=on_click).build().add_style_class(STYLE_PAGINATION_BUTTON).unwrap()

    def __init__(self, service, nb_pages: int, **kwargs):
        self.max_pages = nb_pages

        prev_button = self._create_button("Previous", lambda widget: service.previous_page())
        next_button = self._create_button("Next", lambda widget: service.next_page())
        page_buttons = [
            self._create_button(str(i), lambda widget, page=i: service.go_to_page(page))
            for i in range(1, nb_pages + 1)
        ]
        children = [prev_button] + page_buttons + [next_button]
        super().__init__(
            name="pagination",
            orientation="horizontal",
            h_align="center",
            children=children,
            **kwargs,
        )
        self.get_prev_button().add_style_class(STYLE_DISABLED)
        self.get_page_button(1).add_style_class(STYLE_SELECTED_PAGE)

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
            button.add_style_class(STYLE_DISABLED)
        else:
            button.remove_style_class(STYLE_DISABLED)

    def reset_pagination(self, page_index):
        # Prev and next
        self._update_nav_button(self.get_prev_button(), page_index == 1)
        self._update_nav_button(self.get_next_button(), page_index == self.max_pages)

        # Pagination number
        for index, button in enumerate(self.get_all_page_button()):
            if (index + 1) == page_index:
                button.add_style_class(STYLE_SELECTED_PAGE)
            else:
                button.remove_style_class(STYLE_SELECTED_PAGE)

class Wallpaper(Window):
    def __init__(
        self,
        service,
        monitors: list[str],
        **kwargs,
    ):
        anchor = "left bottom top right" if SETTINGS.main.fullscreen else "top left"
        super().__init__(
            size=SETTINGS.layout.window_size,
            anchor=anchor,
            exclusivity="auto",
            keyboard_mode="on-demand",
            **kwargs,
        )
        self.set_resizable(False)
        self.button_clear_cache = Button(label="Clear cache", on_clicked=lambda _: service.clear_cache())

        self.pagination = None
        self.monitor_section = MonitorSection(
            service, SETTINGS.config_file, monitors, SETTINGS.layout.monitor_img_size
        )
        self.layout = CenterBox(
            orientation="vertical",
            start_children=self.monitor_section,
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
            outer_box.add_style_class(STYLE_BACKGROUND_IMG)
        else:
            outer_box.add_style_class(STYLE_BACKGROUND_COLOR)

        self.children = outer_box

    def set_selected_monitor(self, widget):
        widget.add_style_class(STYLE_SELECTED_SCREEN)

    def set_unselected_monitor(self, widget):
        widget.remove_style_class(STYLE_SELECTED_SCREEN)

    def set_selected_image(self, widget):
        for row in self.wallpaper_section.get_wallpaper_rows():
            for child in row:
                if isinstance(child, EventBox):
                    child.remove_style_class(STYLE_SELECTED_IMAGE)
        widget.add_style_class(STYLE_SELECTED_IMAGE)

    def update_monitor_image(self, monitor, image_name):
        image_widget = monitor.children[0].children[0].children[0]
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            image_name,
            width=SETTINGS.layout.monitor_img_size,
            height=SETTINGS.layout.monitor_img_size,
        )
        image_widget.set_from_pixbuf(pixbuf)

    def update_wallpaper_rows(self, service, action, page_index, wallpaper_rows):
        self.wallpaper_section.update_wallpaper_rows(service, action, wallpaper_rows)
        self.pagination.reset_pagination(page_index)

    def set_wallpaper_rows(self, service, wallpaper_rows, total_pages):
        self.wallpaper_section = WallpaperSection(service, wallpaper_rows)

        if SETTINGS.main.pagination:
            self.layout.center_children = self.wallpaper_section
            self.pagination = PaginationSection(service, total_pages)
            self.layout.end_children = self.button_clear_cache
            self.layout.add_end(self.pagination)
        else:
            self.wallpaper_section = WallpaperSection(service, wallpaper_rows)
            self.layout.add_center(self.wallpaper_section)

    def on_draw(self, *args):
        self.revealer.child_revealed = True
