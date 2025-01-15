from wallpaper.views import Wallpaper as WallpaperView
from wallpaper.models import Wallpaper as WallpaperModel, Settings
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

class Wallpaper:
    def __init__(self, settings):
        self._settings = settings
        self._model = WallpaperModel(self._settings.wallpapers_folder)
        self._view = WallpaperView(
            settings=self._settings,
            monitors=self._get_monitors(),
            wallpaper_rows=self._get_wallpaper_rows(),
        )
        self._set_stylesheet_vars()

    def _get_monitors(self):
        return self._model.get_monitors()

    def _get_wallpaper_rows(self):
        return self._model.get_images_as_row(self._settings.img_per_row)

    def _set_stylesheet_vars(self):
        environment = Environment(loader=FileSystemLoader("templates/"))
        template = environment.get_template("variables.css")
        content = template.render(
            background_color=self._settings.background_color,
        )
        with open("./variables.css", mode="w", encoding="utf-8") as file:
            file.write(content)

    @property
    def view(self):
        return self._view
