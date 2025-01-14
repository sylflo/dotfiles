from wallpaper.views import Wallpaper as WallpaperView

# TODO use settings
IMG_PER_ROW = 3

class Wallpaper:
    def __init__(self, model):
        self.model = model

    def create_view(self):
        return WallpaperView(
            monitors=self.model.get_monitors(),
            wallpaper_rows=self.model.get_images_as_row(IMG_PER_ROW),
            # open_settings_callback=self.open_settings,
        )

    def _get_image_rows(self):
        images = self.model.get_images()
        return [images[i:i + 3] for i in range(0, len(images), 3)]
