from wallpaper.views import Wallpaper as WallpaperView
from wallpaper.models import Wallpaper as WallpaperModel, Settings

from pathlib import Path

class Wallpaper:
    def __init__(self):
        self._settings = Settings.load()
        self._model = WallpaperModel(self._get_wallpapers_folder())
        self._view = WallpaperView(
            wallpapers_folder=self._get_wallpapers_folder(),
            img_size=self._get_wallpapers_size(),
            monitor_size=self._get_monitor_size(),
            monitors=self._get_monitors(),
            wallpaper_rows=self._get_wallpaper_rows(),
        )

    def _get_wallpapers_folder(self) -> Path:
        return self._settings.wallpapers_folder

    def _get_wallpapers_size(self) -> int:
        return self._settings.wallpaper_img_size

    def _get_monitor_size(self) -> int:
        return self._settings.monitor_img_size

    def _get_monitors(self):
        return self._model.get_monitors()

    def _get_wallpaper_rows(self):
        return self._model.get_images_as_row(self._settings.img_per_row)

    @property
    def view(self):
        return self._view
