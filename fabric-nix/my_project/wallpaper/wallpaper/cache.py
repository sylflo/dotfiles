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

    def _get_cache_file(self):
        return SETTINGS.main.cache_folder  / "cache.json"


    def cache_images(self):
    # File generator for all files in the directory
        def files_generator():
            for root, _, files in os.walk(SETTINGS.main.wallpapers_folder):
                for file in files:
                    yield file

        hash_md5 = hashlib.md5()
        cache_data = self._get_data_from_cache_file(self._get_cache_file())
        # Load and display images in batches
        image_batch = []
        for filename in files_generator():
            md5_filename = hashlib.md5(filename.encode("utf")).hexdigest()
            if md5_filename not in cache_data:
                cache_data["files"][md5_filename] = {
                    "source_filename": filename,
                }
            image_batch.append(filename)
            if len(image_batch) >= SETTINGS.main.cache_batch:
                # Process the batch
                yield image_batch
                image_batch = []
        # Process the remaining files
        if image_batch:
            yield image_batch


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

