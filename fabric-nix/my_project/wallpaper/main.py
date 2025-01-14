from fabric import Application
from wallpaper.views import Wallpaper as WallpaperView
from wallpaper.controller import Wallpaper as WallpaperController
from wallpaper.models import Wallpaper as WallpaperModel

from fabric.utils import invoke_repeater, get_relative_path


if __name__ == "__main__":
    controller = WallpaperController()
    view = controller.view
    app = Application("wallpaper", view)
    app.set_stylesheet_from_file(get_relative_path("./style.css"))
    app.run()
