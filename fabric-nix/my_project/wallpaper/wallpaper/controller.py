import os
import shutil
import subprocess
import threading
from pathlib import Path

from gi.repository import GLib
from jinja2 import Environment, FileSystemLoader

from wallpaper.cache import CacheManager
from wallpaper.models import SETTINGS, Wallpaper as WallpaperModel
from wallpaper.services import Pagination as WallpaperService
from wallpaper.views import Wallpaper as WallpaperView
from wallpaper.pagination_service import PaginationService


class Wallpaper:
    def _cache(self):
        cache_manager = CacheManager()
        if cache_manager.should_clear_cache():
            self._initialize_cache_directory()
            cache_manager.clear_cache()
            self._initialize_cache_directory()
            files_processed = 0
            for cached_files in cache_manager.cache_images():
                files_processed = len(cached_files) + files_processed
                self._update_cache_ui()
                print(f"Cached {files_processed} files...")
            print("All files have been cached")
        self._update_cache_ui()

    def _update_cache_ui(self):
        self.cache_data = cache_manager = CacheManager().get_data_from_cache_file()
        self.total_pages = self.pagination_service.get_total_pages(
            SETTINGS.layout.img_per_row, SETTINGS.layout.row_per_page
        )
        # Update ui accordingly
        if SETTINGS.main.pagination:
            wallpaper_rows = self.pagination_service.get_wallpaper_rows(
                self.pagination_service.current_page - 1,
                SETTINGS.layout.img_per_row,
                SETTINGS.layout.row_per_page,
            )
        else:
            wallpaper_rows = self._get_scrolling_wallpaper_rows(
                SETTINGS.layout.img_per_row
            )
        GLib.idle_add(
            self._view.set_wallpaper_rows,
            self.service,
            wallpaper_rows,
            self.total_pages,
        )

    def _initialize_cache_directory(self):
        """Ensures the cache directory exists."""
        cache_dir = SETTINGS.main.cache_folder / "images"
        os.makedirs(cache_dir, exist_ok=True)
        #logger.debug(f"Cache directory initialized: {cache_dir}")


    def clear_cache(self, service):
        cache_manager = CacheManager()
        cache_manager.clear_cache()
        threading.Thread(target=self._cache, daemon=True).start()

    def _init_services(self):
        self.service.connect("next-page", self.next_page)
        self.service.connect("previous-page", self.previous_page)
        self.service.connect("go-to-page", self.go_to_page)
        self.service.connect("select-monitor", self.select_monitor)
        self.service.connect("select-image", self.select_image)
        self.service.connect("clear-cache", self.clear_cache)

    def __init__(self):
        self.model = WallpaperModel(SETTINGS.main.cache_folder / "images")
        self.pagination_service = PaginationService()
        self.service = WallpaperService()
        self._init_services()
        self.selected_monitors = []
        self.selected_monitors_name = []
        self.selected_image = None
        self._view = WallpaperView(
            service=self.service,
            monitors=self._get_monitors(),
        )
        self._set_stylesheet_vars()
        threading.Thread(target=self._cache, daemon=True).start()

    def _get_monitors(self):
        return self.model.get_monitors()

    def _get_scrolling_wallpaper_rows(self, img_per_row: int):
        images = self.model.get_images()
        return [images[i : i + img_per_row] for i in range(0, len(images), img_per_row)]

    def next_page(self, service):
        if self.pagination_service.has_next():
            self.pagination_service.next_page()
            self._update_pagination_view(action="next")

    def previous_page(self, service):
        if self.pagination_service.has_previous():
            self.pagination_service.previous_page()
            self._update_pagination_view(action="next")

    def go_to_page(self, service, page_index: int):
        self.pagination_service.go_to_page(page_index)
        action = "next" if page_index > self.pagination_service.current_page else "previous"
        self._update_pagination_view(action=action)

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
        return self.cache_data["files"][self.selected_image]["source_filename"]

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
                shutil.copy(org_img_path, Path(SETTINGS.config_file).parent / name)

    def _update_pagination_view(self, action: str):
        self._view.update_wallpaper_rows(
            service=self.service,
            action=action,
            page_index=self.pagination_service.current_page,
            wallpaper_rows=self.pagination_service.get_wallpaper_rows(
                self.pagination_service.current_page - 1,
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
