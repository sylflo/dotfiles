from fabric import Application
from wallpaper.views import Wallpaper as WallpaperView
from wallpaper.controller import Wallpaper as WallpaperController
from wallpaper.models import Wallpaper as WallpaperModel
from wallpaper.models import Settings



from fabric.utils import invoke_repeater, get_relative_path

def close_app(app):
    app.quit()

if __name__ == "__main__":
    settings = Settings.load()
    controller = WallpaperController(settings)

    app = Application("wallpaper", controller.view)
    app.set_stylesheet_from_file(get_relative_path("./style.css"))
    controller.view.add_keybinding("Escape", lambda widget, key, app=app, *_: close_app(app))
    app.run()
