from fabric import Application
from fabric.widgets.wayland import WaylandWindow as Window
from widgets.combobox import ComboBox
from fabric.widgets.label import Label
from fabric.widgets.box import Box
from fabric.widgets.scale import Scale, ScaleMark
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.widgets.widget import Widget


from widgets.separator import Separator
from fabric.utils import invoke_repeater, get_relative_path

from options import OPTIONS


class Title(Box):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            h_align="fill",
            v_align="fill",
            name="title",
            **kwargs,
        )
        self.add(Label(label="SWWW Settings").build().add_style_class("title").unwrap())
        self.add(Separator(h_align="fill", orientation="horizontal").build().add_style_class("separator").unwrap())



class Options(Box):
    def __init__(self, title: str, content: str, widget: Widget, **kwargs):
        super().__init__(
            orientation="vertical",
            h_align="fill",
            v_align="fill",
            **kwargs,
        )
        self.add(Separator(h_align="fill", orientation="horizontal").build().add_style_class("separator").unwrap())
        self.add(Label(h_align="start", label=title).build().add_style_class("label-title").unwrap())
        self.add(Label(h_align="start", label=content).build().add_style_class("label-description").unwrap())
        self.add(widget.build().add_style_class("settings-wdiget").unwrap())


class WallpaperSettings(Window):
    def __init__(self, **kwargs):
        super().__init__(
            anchor="left bottom top right",
            **kwargs
        )
        box = Box(
            name="wallpaper-settings",
            open_inspector=True,
            orientation="vertical",
            children=[
                Title().build().add_style_class("settings-title").unwrap(),
                Box(
                    h_align="center",
                    orientation="vertical",
                    children=[Options(title=option.title, content=option.content, widget=option.widget) for option in OPTIONS ]
                ),
            ],
        )
        self.children = ScrolledWindow(
            child=box
        )


if __name__ == "__main__":
    settings = WallpaperSettings()
    app = Application("wallpaper-settings", settings)
    app.set_stylesheet_from_file(get_relative_path("../style.css"))
    app.run()
