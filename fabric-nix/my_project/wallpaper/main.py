from fabric import Application
from wallpaper.views import Wallpaper as WallpaperView
from wallpaper.controller import Wallpaper as WallpaperController
from wallpaper.models import Wallpaper as WallpaperModel
from wallpaper.models import Settings



from fabric.utils import invoke_repeater, get_relative_path


if __name__ == "__main__":
    settings = Settings.load()
    controller = WallpaperController(settings)
    app = Application("wallpaper", controller.view)

    app.set_stylesheet_from_file(get_relative_path("./style.css"))

    app.run()
