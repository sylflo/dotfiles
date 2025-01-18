import shutil
import subprocess
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from wallpaper.models import Wallpaper as WallpaperModel, SETTINGS
from wallpaper.services import Pagination as WallpaperService
from wallpaper.views import Wallpaper as WallpaperView

from wallpaper.models import Settings


class Wallpaper:
    def __init__(self):
        self._model = WallpaperModel(SETTINGS.main.wallpapers_folder)
        self._service = WallpaperService()
        self._service.connect("next-page", self.next_page)
        self._service.connect("previous-page", self.previous_page)
        self._service.connect("go-to-page", self.go_to_page)
        self._service.connect("select-monitor", self.select_monitor)
        self._service.connect("select-image", self.select_image)
        self._current_page = 1
        self._total_pages = self._get_total_pages(
            SETTINGS.layout.img_per_row, SETTINGS.layout.row_per_page
        )
        self._selected_monitors = []
        self._selected_monitors_name = []
        self._selected_image = None
        if SETTINGS.main.pagination:
            wallpaper_rows = self._get_pagination_wallpaper_rows(
                self._current_page - 1,
                SETTINGS.layout.img_per_row,
                SETTINGS.layout.row_per_page,
            )
        else:
            wallpaper_rows = self._get_scrolling_wallpaper_rows(
                SETTINGS.layout.img_per_row
            )
        self._view = WallpaperView(
            service=self._service,
            total_pages=self._total_pages,
            monitors=self._get_monitors(),
            wallpaper_rows=wallpaper_rows,
        )
        self._set_stylesheet_vars()

    def _get_monitors(self):
        return self._model.get_monitors()

    def _get_scrolling_wallpaper_rows(self, img_per_row: int):
        images = self._model.get_images()
        return [images[i : i + img_per_row] for i in range(0, len(images), img_per_row)]

    def _get_total_pages(self, img_per_row: int, row_per_page: int):
        images = self._model.get_images()

        items_per_page = img_per_row * row_per_page
        total_pages = (len(images) + (items_per_page - 1)) // items_per_page

        return total_pages

    def _get_pagination_wallpaper_rows(
        self, page_index: int, img_per_row: int, row_per_page: int
    ):
        images = self._model.get_images()

        items_per_page = img_per_row * row_per_page
        start_index = page_index * items_per_page
        end_index = start_index + items_per_page
        page_images = images[start_index:end_index]

        rows = [
            page_images[i : i + img_per_row]
            for i in range(0, len(page_images), img_per_row)
        ]
        return rows

    def next_page(self, service):
        if self._current_page < self._total_pages:
            self._current_page = self._current_page + 1
            self._update_view(action='next')

    def previous_page(self, service):
        if self._current_page > 1:
            self._current_page = self._current_page - 1
            self._update_view(action='previous')

    def go_to_page(self, service, page_index: int):
        if page_index > 0 and page_index <= self._total_pages:
            action = 'next' if page_index > self._current_page else 'previous'
            self._current_page = page_index
            self._update_view(action=action)

    def select_monitor(self, service, widget, monitor_name):
        if widget in self._selected_monitors:
            self._view.set_unselected_monitor(widget)
            self._selected_monitors.remove(widget)
            self._selected_monitors_name.remove(monitor_name)
        else:
            self._view.set_selected_monitor(widget)
            self._selected_monitors.append(widget)
            self._selected_monitors_name.append(monitor_name)
        self.update_monitor_image()

    def select_image(self, service, widget, image_name):
        self._view.set_selected_image(widget)
        self._selected_image = image_name
        self.update_monitor_image()

    def update_monitor_image(self):
        if self._selected_image:
            for widget, name in zip(
                self._selected_monitors, self._selected_monitors_name
            ):
                image_location = (
                    f"{SETTINGS.main.wallpapers_folder}/{self._selected_image}"
                )
                command = SETTINGS.swww.build_command(name, image_location)
                # TODO add logger for command
                subprocess.run(command)
                self._view.update_monitor_image(widget, self._selected_image)
                shutil.copy(
                    image_location, Path(SETTINGS.config_file).parent / name
                )

    def _update_view(self, action: str):
        self._view.update_wallpaper_rows(
            service=self._service,
            action=action,
            page_index=self._current_page,
            wallpaper_rows=self._get_pagination_wallpaper_rows(
                self._current_page - 1,
                SETTINGS.layout.img_per_row,
                SETTINGS.layout.row_per_page,
            ),
        )

    def _set_stylesheet_vars(self):
        filename = "style.css"
        environment = Environment(loader=FileSystemLoader("templates/"))
        template = environment.get_template(filename)
        content = template.render(
            background_color=SETTINGS.layout.background_color,
            background_img=SETTINGS.layout.background_img,
            background_selected_image=SETTINGS.layout.selected_image,
            background_selected_screen=SETTINGS.layout.selected_screen,
            pagination_background_color=SETTINGS.layout.pagination_background_color,
            pagination_color=SETTINGS.layout.pagination_color,
            pagination_border_color=SETTINGS.layout.pagination_border_color,
            pagination_hover_background_color=SETTINGS.layout.pagination_hover_background_color,
            pagination_hover_color=SETTINGS.layout.pagination_hover_color,
            pagination_selected_background_color=SETTINGS.layout.pagination_selected_background_color,
            pagination_selected_color=SETTINGS.layout.pagination_selected_color,
            pagination_selected_border=SETTINGS.layout.pagination_selected_border,
            pagination_disabled_background_color=SETTINGS.layout.pagination_disabled_background_color,
            pagination_disabled_color=SETTINGS.layout.pagination_disabled_color,
            pagination_disabled_border=SETTINGS.layout.pagination_disabled_border,
            img_spacing=SETTINGS.layout.img_spacing,
        )
        with open(filename, mode="w", encoding="utf-8") as file:
            file.write(content)

    @property
    def view(self):
        return self._view
