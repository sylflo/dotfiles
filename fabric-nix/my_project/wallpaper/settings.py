from fabric import Application
from fabric.widgets.wayland import WaylandWindow as Window
from combobox import ComboBox
from fabric.widgets.label import Label
from fabric.widgets.box import Box
from fabric.widgets.scale import Scale, ScaleMark


class WallpaperSettings(Window):
    def __init__(self, **kwargs):
        super().__init__(
            layer="top",
            #anchor="left bottom top right",
            exclusivity="auto",
            **kwargs
        )
        # TODO add random stuff for all value when possible
        # TODO add submit button and store value in a text
        scale_1 = Scale(
            value=90, min_value=0, max_value=255,
        )
        scale_2 = Scale(
            value=10, min_value=0, max_value=300,
        )
        box = Box(
            name="outer-box",
            open_inspector=True,
            orientation="vertical",
            children=[
                # Resize
                Label(label="Resize"),
                ComboBox(items=["no", "crop", "fit"]),
                # TODO Fill color
                Label(label="Fill color"),
                # Filter
                Label(label="Filter"),
                ComboBox(items=["Nearest", "Bilinear", "CatmullRom", "Mitchell", "Lanczos3"]),
                # Transition type
                Label(label="Transition type"),
                ComboBox(items=["none", "simple", "fade", "left", "right", "top", "bottom", "wipe", "wave", "grow", "center", "any", "outer", "random"]),
                # Transtion step
                Label(label="Transition step"),
                scale_1,
                # Transtion duration
                Label(label="Transition duration (in seconds)"),
                scale_2,
                Label(label=f"value is {scale_2.get_value()}")
            ],
        )
        self.add(box)


if __name__ == "__main__":
    settings = WallpaperSettings()
    app = Application("wallpaper-settings", settings)
    #app.set_stylesheet_from_file(get_relative_path("./style.css"))
    app.run()
