from wallpaper.models import SETTINGS
from wallpaper.models import Wallpaper as WallpaperModel


class Pagination:
    def __init__(self):
        self.current_page = 1
        self.total_pages = 0
        self.model = WallpaperModel(SETTINGS.main.cache_folder / "images")
        self.total_pages = self.get_total_pages(
            SETTINGS.layout.img_per_row, SETTINGS.layout.row_per_page
        )

    def get_total_pages(self, img_per_row: int, row_per_page: int):
        images = self.model.get_images()
        items_per_page = img_per_row * row_per_page
        self.total_pages = (len(images) + (items_per_page - 1)) // items_per_page
        return self.total_pages


    def get_wallpaper_rows(
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

    def has_next(self) -> bool:
        return self.current_page < self.total_pages

    def has_previous(self) -> bool:
        return self.current_page > 1

    def next_page(self) -> int:
        if self.has_next():
            self.current_page = self.current_page + 1
        return self.current_page

    def previous_page(self) -> int:
        if self.has_previous():
            self.current_page = self.current_page - 1
        return self.current_page

    def go_to_page(self, page_index: int) -> int:
        if 1 <= page_index <= self.total_pages:
            self.current_page = page_index
        return self.current_page
    