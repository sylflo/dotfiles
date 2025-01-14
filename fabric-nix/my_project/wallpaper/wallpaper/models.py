import subprocess
import json
import os

# @dataclass
# class Settings:
#     # min_width:
#     # min_height
#     # max_width
#     # max_heigth
#     # background_color: Optional[str]
#     img_size: Optional[int] = 250
#     bacgkround_img: Optional[str] = None
#     # color_text:
#     img_per_row: Optional[int] = 3
#     scroll: Optional[bool] = False # if False pagination
#     animation: Optional[bool] = True

class Wallpaper:
    # TODO should be set in config and wuith a default in conig
    def __init__(self, directory="./images"):
        self.directory = directory
        self.image_selected = None
        self.screens_selected = {}

    def get_images_as_row(self, img_per_row: int):
        images = os.listdir(self.directory)
        return [images[i:i + img_per_row] for i in range(0, len(images), img_per_row)]

    def get_monitors(self):
        # TODO should work any WM
        result = subprocess.run(["hyprctl", "-j", "monitors"], capture_output=True, text=True)
        return [monitor['name'] for monitor in json.loads(result.stdout)]

    # def set_wallpaper(self, monitors, image_name):
    #     # # TODO image_name should be manadatyory
    #     # This should be in controller
    #     if image_name:
    #         for monitor in monitors:
    #             os.system(f"swww img -o \"{monitor}\" ./images/{image_name}")
