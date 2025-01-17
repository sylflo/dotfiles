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


# from fabric import Application
# from fabric.widgets.datetime import DateTime
# from fabric.widgets.centerbox import CenterBox
# from fabric.widgets.label import Label
# from fabric.widgets.wayland import WaylandWindow
# from fabric.widgets.window import Window


# # class StatusBar(Window):
# class StatusBar(WaylandWindow):
#     def __init__(self, **kwargs):
#         super().__init__(
#             title='fuck',
#             size=500,
#             keyboard_mode="on-demand",
#             # pass_through=False,
#         )
#         self.title = 'fuck'
#         self.set_resizable(False)  
#         self.date_time = DateTime()
#         self.children = Label(label="PLOP")

# if __name__ == "__main__":
#     bar = StatusBar()
#     app = Application("bar-example", bar)
#     app.run()