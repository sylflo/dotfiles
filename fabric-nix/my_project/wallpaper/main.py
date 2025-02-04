from fabric import Application
from fabric.utils import get_relative_path

from wallpaper.controller import Wallpaper as WallpaperController


def close_app(app):
    app.quit()


if __name__ == "__main__":
    controller = WallpaperController()

    app = Application("wallpaper", controller.view)
    app.set_stylesheet_from_file(get_relative_path("./style.css"))
    controller.view.add_keybinding(
        "Escape", lambda widget, key, app=app, *_: close_app(app)
    )
    app.run()
