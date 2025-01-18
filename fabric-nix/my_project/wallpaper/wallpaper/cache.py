import json
import os
from pathlib import Path
import hashlib
import gi


gi.require_version("Gtk", "3.0")
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf

import os
import shutil

# TODO Load from settings
DIRECTORY = "/home/sylflo/Projects/dotfiles/fabric-nix/my_project/images"
CACHE_DIRECTORY = "/home/sylflo/.cache/sww_ui_ricing"
IMG_MAX_WIDTH = 300
IMG_MAX_HEIGHT = 300
WALLPAPER_FOLDER = "/home/sylflo/Projects/dotfiles/fabric-nix/my_project/images"

def get_data_from_cache_file(file_path):
    file = Path(file_path)
    if file.exists():
        with open(file, 'r') as f:
            data = json.load(f)
    else:
        data = {
            "files": {},
            "wallpaper_folder": WALLPAPER_FOLDER,
            "img_max_width": IMG_MAX_WIDTH,
            "img_max_height": IMG_MAX_HEIGHT,
        }
    return data


def cache_image(path_file, cache_data):
    filename = path_file.name
    hashed_filename = hashlib.md5(path_file.name.encode('utf-8')).hexdigest()
    pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(path_file))
    original_width = pixbuf.get_width()
    original_height = pixbuf.get_height()
    width_ratio = IMG_MAX_WIDTH / original_width
    height_ratio = IMG_MAX_HEIGHT / original_height
    scale_ratio = min(width_ratio, height_ratio)
    new_width = int(original_width * scale_ratio)
    new_height = int(original_height * scale_ratio)
    scaled_pixbuf = pixbuf.scale_simple(new_width, new_height, GdkPixbuf.InterpType.BILINEAR)
    pixbuf.savev(CACHE_DIRECTORY + "/images/" + hashed_filename, "jpeg", [], [])
    cache_data['files'][path_file.name] = {
        "thumbnail": hashed_filename,
        "source_image": str(path_file),
    }

def get_files_by_batch(directory, batch_size):
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

def cache_images():
    cache_data = get_data_from_cache_file(CACHE_DIRECTORY + "/" + "cache.json")
    Path(CACHE_DIRECTORY + "/images").mkdir(parents=True, exist_ok=True)
    for path_files in get_files_by_batch(DIRECTORY, batch_size=100):
        for path_file in path_files:
            if path_file.name not in cache_data['files']:
                cache_image(path_file, cache_data)
            else:
                print("ELSE")

    with open(CACHE_DIRECTORY + "/" + "cache.json", "w") as f:
        json.dump(cache_data, f, indent=4)


cache_images()

def clear_cache():
    # TODO call if wallpaperfolder change, width/heifght change
    # Delete all files and directories inside myapp_cache_dir
    if os.path.exists(CACHE_DIRECTORY):
        for item in os.listdir(CACHE_DIRECTORY):
            item_path = os.path.join(CACHE_DIRECTORY, item)
            if os.path.isfile(item_path):
                os.remove(item_path)  # Remove files
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Remove directories
        print(f"All contents of {CACHE_DIRECTORY} have been deleted.")
    else:
        print(f"{CACHE_DIRECTORY} does not exist.")

#clear_cache()
