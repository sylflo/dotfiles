import hashlib
import json
import os
import shutil
from pathlib import Path

import gi
from gi.repository import GdkPixbuf

from wallpaper.models import SETTINGS

gi.require_version("Gtk", "3.0")
gi.require_version("GdkPixbuf", "2.0")


class CacheManager:
    def get_data_from_cache_file(self):
        file = Path(self._get_cache_file())
        if file.exists():
            with open(file, "r") as f:
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
        return SETTINGS.main.cache_folder / "cache.json"

    def cache_images(self):
        # File generator for all files in the directory
        def files_generator():
            for root, dirs, files in os.walk(SETTINGS.main.wallpapers_folder):
                for file in files:
                    # relative_path = os.path.relpath(os.path.join(root, file), SETTINGS.main.wallpapers_folder)
                    full_path = os.path.join(root, file)
                    yield full_path

        cache_data = self.get_data_from_cache_file()
        # Load and display images in batches
        image_batch = []
        for full_path in files_generator():
            md5_filename = hashlib.md5(full_path.encode("utf")).hexdigest()
            if md5_filename not in cache_data:
                # Avoid duplciate if two file are the same
                cache_data["files"][md5_filename] = {
                    "source_filename": full_path,
                }
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(full_path)
                original_width = pixbuf.get_width()
                original_height = pixbuf.get_height()
                width_ratio = SETTINGS.layout.img_max_width / original_width
                height_ratio = SETTINGS.layout.img_max_height / original_height
                scale_ratio = min(width_ratio, height_ratio)
                new_width = int(original_width * scale_ratio)
                new_height = int(original_height * scale_ratio)
                scaled_pixbuf = pixbuf.scale_simple(
                    new_width, new_height, GdkPixbuf.InterpType.BILINEAR
                )
                scaled_pixbuf.savev(
                    str(SETTINGS.main.cache_folder / "images" / md5_filename),
                    "jpeg",
                    [],
                    [],
                )
                image_batch.append(full_path)
            except gi.repository.GLib.GError:
                # TODO add logger
                pass

            if len(image_batch) >= SETTINGS.main.cache_batch:
                # Write JSON data to the file
                with open(self._get_cache_file(), "w") as json_file:
                    json.dump(cache_data, json_file, indent=4)
                yield image_batch
                image_batch = []
        # Process the remaining files
        if image_batch:
            yield image_batch

    def should_clear_cache(self):
        if Path(self._get_cache_file()).exists() is False:
            return True
        else:
            cache_data = self.get_data_from_cache_file()
            return cache_data["wallpapers_folder"] != str(
                SETTINGS.main.wallpapers_folder
            )

    def clear_cache(self):
        for item in os.listdir(SETTINGS.main.cache_folder):
            item_path = os.path.join(SETTINGS.main.cache_folder, item)
            if os.path.isfile(item_path):
                os.remove(item_path)  # Remove files
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Remove directories
        print(f"All contents of {SETTINGS.main.cache_folder} have been deleted.")
