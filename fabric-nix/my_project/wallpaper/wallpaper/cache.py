import json
import os
from pathlib import Path
import hashlib
import gi
import shutil

gi.require_version("Gtk", "3.0")
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf

from wallpaper.models import SETTINGS



class CacheManager:
    def _get_data_from_cache_file(self, file_path):
        file = Path(file_path)
        if file.exists():
            with open(file, 'r') as f:
                data = json.load(f)
        else:
            data = {
                "files": {},
                "wallpapers_folder": str(SETTINGS.main.wallpapers_folder),
                "img_max_width": SETTINGS.layout.img_max_width,
                "img_max_height": SETTINGS.layout.img_max_height,
            }
        return data

    # def _cache_image(self, path_file, hashed_filename, cache_data) -> Path:
    #     filename = path_file.name
    #     cached_filename = Path(SETTINGS.main.cache_folder / "images" /  hashed_filename)
    #     pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(path_file))
    #     original_width = pixbuf.get_width()
    #     original_height = pixbuf.get_height()
    #     width_ratio = SETTINGS.layout.img_max_width / original_width
    #     height_ratio = SETTINGS.layout.img_max_height / original_height
    #     scale_ratio = min(width_ratio, height_ratio)
    #     new_width = int(original_width * scale_ratio)
    #     new_height = int(original_height * scale_ratio)
    #     scaled_pixbuf = pixbuf.scale_simple(new_width, new_height, GdkPixbuf.InterpType.BILINEAR)
    #     pixbuf.savev(cached_filename.as_posix().encode('utf-8'), "jpeg", [], [])
    #     cache_data['files'][path_file.name] = {
    #         "thumbnail": hashed_filename,
    #         "source_image": str(path_file),
    #     }
    #     return cached_filename

    # def _get_files_by_batch(self, directory, batch_size):
    #     #for root, _, files in os.walk(DIRECTORY):
    #     def files_generator():
    #         for root, _, files in os.walk(directory):
    #             for file in files:
    #                 yield file
    #                 #yield os.path.join(root, file)
    #     #files = (f for f in Path(directory).iterdir() if f.is_file())
    #     batch = []
    #     for file in files_generator():
    #         batch.append(file)
    #         if len(batch) == batch_size:
    #             yield batch
    #             batch = []
    #     # Yield any remaining files
    #     if batch:
    #         yield batch

    def _get_cache_file(self):
        return SETTINGS.main.cache_folder  / "cache.json"

    # def cache_images(self):
    #     cache_data = self._get_data_from_cache_file(self._get_cache_file())
    #     Path(SETTINGS.main.cache_folder  / "images").mkdir(parents=True, exist_ok=True)
    #     for path_files in self._get_files_by_batch(SETTINGS.main.wallpapers_folder, SETTINGS.main.cache_batch):
    #         cached_files = []
    #         for path_file in path_files:
    #             # hashed_filename = hashlib.md5(path_file.name.encode('utf-8')).hexdigest()
    #             hashed_filename = hashlib.md5(path_file.encode('utf-8')).hexdigest()
    #             if path_file not in cache_data['files']:
    #                 cached_filename = self._cache_image(path_file, hashed_filename, cache_data)
    #             cached_files.append(hashed_filename)
    #         yield cached_files
    #     with open(self._get_cache_file(), "w") as f:
    #         json.dump(cache_data, f, indent=4)


    def cache_images(self):
    # File generator for all files in the directory
        DIRECTORY = "/home/sylflo/Projects/dotfiles/fabric-nix/my_project/images"

        def files_generator():
            for root, _, files in os.walk(DIRECTORY):
                for file in files:
                    yield file

        cache_data = self._get_data_from_cache_file(self._get_cache_file())
        # Load and display images in batches
        batch_size = 10 # Number of images to load per batch
        image_batch = []
        for filename in files_generator():
            image_batch.append(filename)
            if len(image_batch) >= batch_size:
                # Process the batch
                yield image_batch
                image_batch = []
        # TODO check we do all images
        # # Process the remaining files
        # if image_batch:
        #     CONTROLLER.process_image_batch(image_batch)

    def _should_clear_cache(self):
        cache_data = self._get_data_from_cache_file(self._get_cache_file())
        return cache_data['wallpapers_folder'] != str(SETTINGS.main.wallpapers_folder)

    def clear_cache(self):
        if os.path.exists(SETTINGS.main.cache_folder) and self._should_clear_cache():
            for item in os.listdir(SETTINGS.main.cache_folder):
                item_path = os.path.join(SETTINGS.main.cache_folder, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)  # Remove files
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)  # Remove directories
            print(f"All contents of {SETTINGS.main.cache_folder} have been deleted.")
        else:
            print(f"{SETTINGS.main.cache_folder} does not exist.")
