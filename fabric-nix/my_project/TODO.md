LATER
  WALLPAPER
    1) Fullscreonn => boolean, scrolling => min_content_size, max_content_size also confgigurable
    2) spacing should be configurable
    2) responsive layout
    3) Try scrolling with 100 items or more and use caching
    3.1) Font family, color screen name
    4) Refresh button wallpaper folder
    5) Shortcut key => configurable
    6) Possiobility to split wallpaper between n screens
    7) Dameon to chang wallpaper every x seconss
    8) Wait for sww to work before changing screenshot image


TODO:
  add ruff
  add mypy
  add black
  add isort

    NAME: SwwwUiTuning

MUSIC PLAYER:
  background => album image
  favorite add




# def generate_grid(
#     total_pages: int,
#     wallpaper_rows: list[list[str]],
# ):
class Plop(Box):
    def __init__(
        self
    ):

        super().__init__(orientation="vertical", spacing=10)

        # Desired maximum dimensions for images
        # TODO config
        max_width = 300
        max_height = 300

        # Number of columns in the grid
        # TODO config
        columns = 3

        # Populate the grid with rows of images
        current_row = None
        for i, image_path in enumerate(image_paths):
            # If starting a new row
            if i % columns == 0:
                current_row = Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                self.pack_start(current_row, False, False, 0)

            # Load and resize the image while maintaining aspect ratio
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(image_path)
            original_width = pixbuf.get_width()
            original_height = pixbuf.get_height()

            width_ratio = max_width / original_width
            height_ratio = max_height / original_height
            scale_ratio = min(width_ratio, height_ratio)

            new_width = int(original_width * scale_ratio)
            new_height = int(original_height * scale_ratio)

            scaled_pixbuf = pixbuf.scale_simple(new_width, new_height, GdkPixbuf.InterpType.BILINEAR)
            #image = Image.new_from_pixbuf(scaled_pixbuf)
            # image = Label(label='FUICK')
            image = Image(image_file=image_path)
            image.set_from_pixbuf(scaled_pixbuf)

            # Add the image to the current row
            current_row.pack_start(image, False, False, 0)