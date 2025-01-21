import shutil
import subprocess
import threading
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from wallpaper.models import Wallpaper as WallpaperModel, SETTINGS
from wallpaper.services import Pagination as WallpaperService
from wallpaper.views import Wallpaper as WallpaperView

from wallpaper.models import Settings
from wallpaper.cache import CacheManager

import gi
from gi.repository import GdkPixbuf, GLib
from gi.repository import Gtk

import os


class Wallpaper:
    def _cache(self):
        cache_manager = CacheManager()
        if cache_manager.should_clear_cache():
            os.makedirs(f"{SETTINGS.main.cache_folder}/images", exist_ok=True)        
            cache_manager.clear_cache()
            os.makedirs(f"{SETTINGS.main.cache_folder}/images", exist_ok=True)        
            files_processed = 0
            for cached_files in cache_manager.cache_images():
                files_processed = len(cached_files) + files_processed
                self.cache_data = cache_manager = CacheManager().get_data_from_cache_file()
                self.total_pages = self._get_total_pages(
                    SETTINGS.layout.img_per_row, SETTINGS.layout.row_per_page
                )
                # Update ui accordingly
                if SETTINGS.main.pagination:
                    wallpaper_rows = self._get_pagination_wallpaper_rows(
                        self.current_page - 1,
                        SETTINGS.layout.img_per_row,
                        SETTINGS.layout.row_per_page,
                    )
                else:
                    wallpaper_rows = self._get_scrolling_wallpaper_rows(
                        SETTINGS.layout.img_per_row
                    )
                GLib.idle_add(self._view.set_wallpaper_rows, self.service, wallpaper_rows, self.total_pages)





                print(f"Cached {files_processed} files...")
            print("All files have been cached")
        # self.cache_data = cache_manager = CacheManager().get_data_from_cache_file()
        # self.total_pages = self._get_total_pages(
        #     SETTINGS.layout.img_per_row, SETTINGS.layout.row_per_page
        # )
        # # Update ui accordingly
        # if SETTINGS.main.pagination:
        #     wallpaper_rows = self._get_pagination_wallpaper_rows(
        #         self.current_page - 1,
        #         SETTINGS.layout.img_per_row,
        #         SETTINGS.layout.row_per_page,
        #     )
        # else:
        #     wallpaper_rows = self._get_scrolling_wallpaper_rows(
        #         SETTINGS.layout.img_per_row
        #     )
        # GLib.idle_add(self._view.set_wallpaper_rows, self.service, wallpaper_rows, self.total_pages)


    def __init__(self):
        self.model = WallpaperModel(SETTINGS.main.cache_folder / "images")
        self.service = WallpaperService()
        self.service.connect("next-page", self.next_page)
        self.service.connect("previous-page", self.previous_page)
        self.service.connect("go-to-page", self.go_to_page)
        self.service.connect("select-monitor", self.select_monitor)
        self.service.connect("select-image", self.select_image)
        self.current_page = 1
        self.selected_monitors = []
        self.selected_monitors_name = []
        self.selected_image = None

        self._view = WallpaperView(
            service=self.service,
            monitors=self._get_monitors(),
        )
        self._set_stylesheet_vars()
        thread = threading.Thread(target=self._cache, daemon=True).start()

    def _get_monitors(self):
        return self.model.get_monitors()

    def _get_scrolling_wallpaper_rows(self, img_per_row: int):
        images = self.model.get_images()
        return [images[i : i + img_per_row] for i in range(0, len(images), img_per_row)]

    def _get_total_pages(self, img_per_row: int, row_per_page: int):
        images = self.model.get_images()

        items_per_page = img_per_row * row_per_page
        total_pages = (len(images) + (items_per_page - 1)) // items_per_page

        return total_pages

    def _get_pagination_wallpaper_rows(
        self, page_index: int, img_per_row: int, row_per_page: int
    ):
        images = self.model.get_images()

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
        if self.current_page < self.total_pages:
            self.current_page = self.current_page + 1
            self._update_view(action='next')

    def previous_page(self, service):
        if self.current_page > 1:
            self.current_page = self.current_page - 1
            self._update_view(action='previous')

    def go_to_page(self, service, page_index: int):
        if page_index > 0 and page_index <= self.total_pages:
            action = 'next' if page_index > self.current_page else 'previous'
            self.current_page = page_index
            self._update_view(action=action)

    def select_monitor(self, service, widget, monitor_name):
        if widget in self.selected_monitors:
            self._view.set_unselected_monitor(widget)
            self.selected_monitors.remove(widget)
            self.selected_monitors_name.remove(monitor_name)
        else:
            self._view.set_selected_monitor(widget)
            self.selected_monitors.append(widget)
            self.selected_monitors_name.append(monitor_name)
        self.update_monitor_image()

    def select_image(self, service, widget, image_name):
        self._view.set_selected_image(widget)
        self.selected_image = image_name
        self.update_monitor_image()

    def _get_original_image_from_cache(self, thumbail_location: str):
        return self.cache_data["files"][self.selected_image]['source_filename']

    def update_monitor_image(self):
        if self.selected_image:
            for widget, name in zip(
                self.selected_monitors, self.selected_monitors_name
            ):
                org_img_path = self._get_original_image_from_cache(self.selected_image)
                command = SETTINGS.swww.build_command(name, org_img_path)
                # TODO add logger for command
                subprocess.run(command)
                self._view.update_monitor_image(widget, org_img_path)
                shutil.copy(
                    org_img_path, Path(SETTINGS.config_file).parent / name
                )

    def _update_view(self, action: str):
        self._view.update_wallpaper_rows(
            service=self.service,
            action=action,
            page_index=self.current_page,
            wallpaper_rows=self._get_pagination_wallpaper_rows(
                self.current_page - 1,
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
