from wallpaper.views import Wallpaper as WallpaperView
from wallpaper.models import Wallpaper as WallpaperModel, Settings

from pathlib import Path

class Wallpaper:
    def __init__(self):
        self._settings = Settings.load()
        self._model = WallpaperModel(self._settings.wallpapers_folder)
        self._view = WallpaperView(
            settings=self._settings,
            monitors=self._get_monitors(),
            wallpaper_rows=self._get_wallpaper_rows(),
        )

    def _get_monitors(self):
        return self._model.get_monitors()

    def _get_wallpaper_rows(self):
        return self._model.get_images_as_row(self._settings.img_per_row)

    @property
    def view(self):
        return self._view
