import os
import random
import gi
from ctypes import CDLL

CDLL("/nix/store/wx6b8hcxsw80pn6vjv8469kv3gbzyvzd-gtk4-layer-shell-1.0.4/lib/libgtk4-layer-shell.so")

gi.require_version("Gtk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")
from gi.repository import Gtk, Gdk, GLib, Gtk4LayerShell as LayerShell

TRANSITION_INTERVAL_MS = 100
TRANSITION_DURATION_MS = 3000
STEPS = TRANSITION_DURATION_MS // TRANSITION_INTERVAL_MS

def animate_transition(from_widget, to_widget, container):
    if not from_widget or not to_widget or not container:
        return

    to_widget.set_opacity(0.0)
    to_widget.set_visible(True)
    to_widget.set_margin_start(100)
    to_widget.set_margin_top(100)
    to_widget.set_margin_bottom(100)
    to_widget.set_vexpand(True)
    container.set_child(to_widget)

    from_translate = 0
    to_translate = 100
    from_widget.set_margin_start(from_translate)
    to_widget.set_margin_start(to_translate)

    step = {"count": 0}
    def animate():
        t = step["count"] / STEPS
        from_opacity = max(0.0, 1.0 - t)
        from_widget.set_opacity(from_opacity)
        slide = int(to_translate * (1.0 - t))
        to_widget.set_margin_start(slide)
        to_opacity = min(1.0, t)
        to_widget.set_opacity(to_opacity)
        step["count"] += 1
        if step["count"] <= STEPS:
            return True
        from_widget.set_visible(False)
        to_widget.set_margin_start(0)
        return False
    GLib.timeout_add(TRANSITION_INTERVAL_MS, animate)

def get_random_wallpaper(folder):
    valid_exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
    files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f)) and os.path.splitext(f)[1].lower() in valid_exts
    ]
    if not files:
        raise FileNotFoundError("No image files found in the wallpaper folder.")
    return random.choice(files)

def on_key_press(controller, keyval, keycode, state):
    if keyval == Gdk.KEY_Escape:
        controller.get_widget().get_root().close()
        return True
    return False

def on_activate(app):
    window = Gtk.Window(application=app)
    window.set_default_size(1920, 1080)
    window.set_focusable(True)
    window.set_can_focus(True)

    LayerShell.init_for_window(window)
    LayerShell.set_layer(window, LayerShell.Layer.OVERLAY)
    LayerShell.set_keyboard_mode(window, LayerShell.KeyboardMode.ON_DEMAND)

    for edge in [LayerShell.Edge.TOP, LayerShell.Edge.BOTTOM, LayerShell.Edge.LEFT, LayerShell.Edge.RIGHT]:
        LayerShell.set_anchor(window, edge, True)

    LayerShell.auto_exclusive_zone_enable(window)

    # CSS
    background_path = get_random_wallpaper("/home/sylflo/Pictures/Wallpapers-tests")
    css = Gtk.CssProvider()
    css_string = f"""
    .background {{
        background-image: url("file://{background_path}");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
    }}
    .row-box {{
        background-color: white;
        border: 1px solid black;
        border-radius: 8px;
        margin: 10px;
        padding: 20px;
        min-height: 100px;
    }}
    .label {{
        font-size: 22px;
        color: black;
        font-weight: bold;
    }}
    .right-label {{
        font-size: 16px;
        color: black;
    }}
    .icon-wrapper {{
        min-width: 100px;
        align-items: center;
        justify-content: center;
    }}
    .scale {{
        margin-left: auto;
        min-width: 200px;
    }}
    switch {{
        margin-left: auto;
    }}
    .material-icon {{
        font-family: "Material Symbols Rounded";
        font-size: 100px;
        font-weight: normal;
        letter-spacing: normal;
        line-height: 1;
    }}
    """
    css.load_from_data(css_string.encode("utf-8"))
    Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    # Load layout
    builder = Gtk.Builder()
    builder.add_from_file("layouts/layout.ui")

    overlay = builder.get_object("overlay")
    main_box = builder.get_object("main_box")

    if overlay is None or main_box is None:
        raise Exception("layout.ui missing overlay or main_box")

    def get(obj_id):
        o = builder.get_object(obj_id)
        if o is None:
            raise Exception(f"Missing object: {obj_id}")
        return o

    brightness_revealer = get("brightness_revealer")
    brightness_row = get("brightness_row")
    sound_row = get("sound_row")
    vpn_row = get("vpn_row")
    bluetooth_row = get("bluetooth_row")
    wifi_row = get("wifi_row")

    def connect_row_click(row, target=None):
        click = Gtk.GestureClick()
        if isinstance(target, Gtk.Revealer):
            click.connect("pressed", lambda *_: target.set_reveal_child(not target.get_reveal_child()))
        elif target:
            click.connect("pressed", lambda *_: animate_transition(main_box, target, overlay))
        row.add_controller(click)

    connect_row_click(brightness_row, brightness_revealer)

    # Pages
    def load_page(name):
        b = Gtk.Builder()
        b.add_from_file(f"layouts/{name}.ui")
        page = b.get_object(f"{name}_page")
        back = b.get_object(f"{name}_back")
        if page is None or back is None:
            raise Exception(f"Missing {name}.ui ids")
        overlay.add_overlay(page)
        connect_row_click(get(f"{name}_row"), page)
        back.connect("clicked", lambda *_: animate_transition(page, main_box, overlay))

    for name in ["sound", "vpn", "bluetooth", "wifi"]:
        load_page(name)

    controller = Gtk.EventControllerKey()
    controller.connect("key-pressed", on_key_press)
    window.add_controller(controller)

    window.set_child(overlay)
    window.present()
    window.set_focus(window)

app = Gtk.Application(application_id="com.example.LayerShellButtons")
app.connect("activate", on_activate)
app.run()
