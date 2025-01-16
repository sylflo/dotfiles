from wallpaper.views import Wallpaper as WallpaperView
from wallpaper.models import Wallpaper as WallpaperModel, Settings
from wallpaper.services import Pagination as PaginationService
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader
from pathlib import Path


class Wallpaper:
    def __init__(self, settings):
        self._settings = settings
        self._model = WallpaperModel(self._settings.wallpapers_folder)
        self._pagination_service = PaginationService()
        self._pagination_service.connect("next-page", self.next_page)
        self._pagination_service.connect("previous-page", self.previous_page)
        self._pagination_service.connect("go-to-page", self.go_to_page)
        self._current_page = 1
        self._total_pages = self._get_total_pages(self._settings.img_per_row, self._settings.row_per_page)
        if self._settings.pagination:
            wallpaper_rows = self._get_pagination_wallpaper_rows(self._current_page, self._settings.img_per_row, self._settings.row_per_page)
        else:
            wallpaper_rows = self._get_scrolling_wallpaper_rows(self._settings.img_per_row)
        self._view = WallpaperView(
            settings=self._settings,
            pagination_service=self._pagination_service,
            total_pages=self._total_pages,
            monitors=self._get_monitors(),
            wallpaper_rows=wallpaper_rows,
        )
        self._set_stylesheet_vars()

    def _get_monitors(self):
        return self._model.get_monitors()

    def _get_scrolling_wallpaper_rows(self, img_per_row: int):
        images = self._model.get_images()
        return [images[i:i + img_per_row] for i in range(0, len(images), img_per_row)]

    def _get_total_pages(self, img_per_row: int, row_per_page: int):
        images = self._model.get_images()

        items_per_page = img_per_row * row_per_page
        total_pages = (len(images) + (items_per_page - 1)) // items_per_page

        return total_pages

    def _get_pagination_wallpaper_rows(self, page_index: int, img_per_row: int, row_per_page: int):
        images = self._model.get_images()

        items_per_page = img_per_row * row_per_page
        start_index = page_index * items_per_page
        end_index = start_index + items_per_page
        page_images = images[start_index:end_index]

        rows = [page_images[i:i + img_per_row] for i in range(0, len(page_images), img_per_row)]
        return rows

    def next_page(self, service):
        if self._current_page < self._total_pages - 1:
            self._current_page = self._current_page + 1
            self._update_view()

    def previous_page(self, service):
        if self._current_page > 0:
            self._current_page = self._current_page - 1
            self._update_view()

    def go_to_page(self, service, page_index: int):
        if page_index > 0 and page_index <  self._total_pages:
            self._current_page = page_index
            self._update_view()

    def _update_view(self):
        self._view.update_content(
            settings=self._settings,
            page_index=self._current_page,
            wallpaper_rows=self._get_pagination_wallpaper_rows(self._current_page, self._settings.img_per_row, self._settings.row_per_page),
        )

    def _set_stylesheet_vars(self):
        template_folder = "templates/"
        filename = "style.css"
        environment = Environment(loader=FileSystemLoader("templates/"))
        template = environment.get_template(filename)
        content = template.render(
            background_color=self._settings.background_color,
            background_img=self._settings.background_img,
        )
        with open(filename, mode="w", encoding="utf-8") as file:
            file.write(content)

    @property
    def view(self):
        return self._view
