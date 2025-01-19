import json
import os
from pathlib import Path
import hashlib
import gi
import shutil

gi.require_version("Gtk", "3.0")
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf

class CacheManager:
    def __init__(self, directory, cache_directory, img_max_width, img_max_height, wallpaper_folder):
        self.DIRECTORY = directory
        self.CACHE_DIRECTORY = cache_directory
        self.IMG_MAX_WIDTH = img_max_width
        self.IMG_MAX_HEIGHT = img_max_height
        self.WALLPAPER_FOLDER = wallpaper_folder

    def _get_data_from_cache_file(self, file_path):
        file = Path(file_path)
        if file.exists():
            with open(file, 'r') as f:
                data = json.load(f)
        else:
            data = {
                "files": {},
                "wallpaper_folder": self.WALLPAPER_FOLDER,
                "img_max_width": self.IMG_MAX_WIDTH,
                "img_max_height": self.IMG_MAX_HEIGHT,
            }
        return data

    def _cache_image(self, path_file, cache_data):
        filename = path_file.name
        hashed_filename = hashlib.md5(path_file.name.encode('utf-8')).hexdigest()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(path_file))
        original_width = pixbuf.get_width()
        original_height = pixbuf.get_height()
        width_ratio = self.IMG_MAX_WIDTH / original_width
        height_ratio = self.IMG_MAX_HEIGHT / original_height
        scale_ratio = min(width_ratio, height_ratio)
        new_width = int(original_width * scale_ratio)
        new_height = int(original_height * scale_ratio)
        scaled_pixbuf = pixbuf.scale_simple(new_width, new_height, GdkPixbuf.InterpType.BILINEAR)
        pixbuf.savev(self.CACHE_DIRECTORY + "/images/" + hashed_filename, "jpeg", [], [])
        cache_data['files'][path_file.name] = {
            "thumbnail": hashed_filename,
            "source_image": str(path_file),
        }

    def _get_files_by_batch(self, directory, batch_size):
        files = (f for f in Path(directory).iterdir() if f.is_file())
        batch = []
        for file in files:
            batch.append(file)
            if len(batch) == batch_size:
                yield batch
                batch = []
        # Yield any remaining files
        if batch:
            yield batch

    def _get_cache_file(self):
        sel;f
        return self.CACHE_DIRECTORY + "/" + "cache.json"

    def cache_images(self):
        cache_data = self._get_data_from_cache_file(self._get_cache_file())
        Path(self.CACHE_DIRECTORY + "/images").mkdir(parents=True, exist_ok=True)
        for path_files in self._get_files_by_batch(self.DIRECTORY, batch_size=100):
            for path_file in path_files:
                if path_file.name not in cache_data['files']:
                    self._cache_image(path_file, cache_data)
        with open(self._get_cache_file(), "w") as f:
            json.dump(cache_data, f, indent=4)

    def _should_clear_cache(self):
        return cache_data['wallpaper_folder'] != self.WALLPAPER_FOLDER

    def clear_cache(self):
        if os.path.exists(self.CACHE_DIRECTORY) and self._should_clear_cache():
            for item in os.listdir(self.CACHE_DIRECTORY):
                item_path = os.path.join(self.CACHE_DIRECTORY, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)  # Remove files
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)  # Remove directories
            print(f"All contents of {self.CACHE_DIRECTORY} have been deleted.")
        else:
            print(f"{self.CACHE_DIRECTORY} does not exist.")


# cache_manager = CacheManager(
#     directory="/home/sylflo/Projects/dotfiles/fabric-nix/my_project/images",
#     cache_directory="/home/sylflo/.cache/sww_ui_ricing",
#     img_max_width=300,
#     img_max_height=300,
#     wallpaper_folder="/home/sylflo/Projects/dotfiles/fabric-nix/my_project/images"
# )

# cache_manager.cache_images()
# # cache_manager.clear_cache()
