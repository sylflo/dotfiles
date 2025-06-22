import os
import random
import gi
from ctypes import CDLL

# Load layer shell
CDLL("/nix/store/wx6b8hcxsw80pn6vjv8469kv3gbzyvzd-gtk4-layer-shell-1.0.4/lib/libgtk4-layer-shell.so")

gi.require_version("Gtk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")
from gi.repository import Gtk, Gdk, GLib, Gtk4LayerShell as LayerShell


TRANSITION_INTERVAL_MS = 100  # interval for each step
TRANSITION_DURATION_MS = 3000  # total duration
STEPS = TRANSITION_DURATION_MS // TRANSITION_INTERVAL_MS

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

def make_row(icon_widget, label_text, extra_widget=None):
    outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    outer_box.set_halign(Gtk.Align.CENTER)
    outer_box.set_hexpand(True)
    outer_box.set_vexpand(False)
    outer_box.set_size_request(960, -1)
    outer_box.set_css_classes(["row-box"])

    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
    row.set_hexpand(True)
    row.set_vexpand(True)

    icon_wrapper = Gtk.Box()
    icon_wrapper.set_valign(Gtk.Align.FILL)
    icon_wrapper.set_hexpand(False)
    icon_wrapper.set_vexpand(True)
    icon_wrapper.set_css_classes(["icon-wrapper"])

    icon_widget.set_valign(Gtk.Align.CENTER)
    icon_widget.set_hexpand(False)
    icon_widget.set_vexpand(False)
    icon_wrapper.append(icon_widget)
    row.append(icon_wrapper)

    label = Gtk.Label(label=label_text)
    label.set_halign(Gtk.Align.START)
    label.set_valign(Gtk.Align.CENTER)
    label.set_hexpand(True)
    label.set_css_classes(["label"])
    row.append(label)

    if extra_widget and isinstance(extra_widget, Gtk.Widget):
        extra_widget.set_halign(Gtk.Align.END)
        extra_widget.set_valign(Gtk.Align.CENTER)
        row.append(extra_widget)

    outer_box.append(row)
    return outer_box


def animate_transition(from_widget, to_widget, container):
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

        # Fade out from_widget
        from_opacity = max(0.0, 1.0 - t)
        from_widget.set_opacity(from_opacity)

        # Slide and fade in to_widget (left to right)
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
    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    overlay = Gtk.Overlay()

    # Main Page
    main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    main_box.set_css_classes(["background"])
    main_box.set_margin_top(100)
    main_box.set_margin_bottom(100)
    main_box.set_hexpand(True)
    main_box.set_vexpand(True)

    center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    center_box.set_halign(Gtk.Align.CENTER)
    center_box.set_valign(Gtk.Align.FILL)
    center_box.set_vexpand(True)

    brightness = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
    brightness.set_value(75)
    brightness.set_hexpand(True)
    brightness.set_css_classes(["scale"])

    revealer = Gtk.Revealer()
    revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
    revealer.set_transition_duration(250)
    revealer.set_reveal_child(False)
    revealer.set_child(brightness)

    brightness_icon = Gtk.Label(label="brightness_low")
    brightness_icon.set_css_classes(["material-icon"])
    brightness_row = make_row(brightness_icon, "Screen Brightness")
    brightness_row.append(revealer)

    click_controller = Gtk.GestureClick()
    click_controller.connect("pressed", lambda *_: revealer.set_reveal_child(not revealer.get_reveal_child()))
    brightness_row.add_controller(click_controller)

    arrow = Gtk.Label(label="›")
    arrow.set_css_classes(["right-label"])

    vpn_status = Gtk.Label(label="Enabled")
    vpn_status.set_css_classes(["right-label"])

    bt_toggle = Gtk.Switch()
    bt_toggle.set_active(True)

    wifi_icon = Gtk.Label(label="wifi")
    wifi_icon.set_css_classes(["material-icon"])

    sound_icon = Gtk.Label(label="volume_up")
    sound_icon.set_css_classes(["material-icon"])

    vpn_icon = Gtk.Label(label="vpn_key")
    vpn_icon.set_css_classes(["material-icon"])

    bluetooth_icon = Gtk.Label(label="bluetooth")
    bluetooth_icon.set_css_classes(["material-icon"])

    sound_row = make_row(sound_icon, "Sound", arrow)
    vpn_row = make_row(vpn_icon, "VPN", vpn_status)
    bluetooth_row = make_row(bluetooth_icon, "Bluetooth", bt_toggle)
    wifi_row = make_row(wifi_icon, "Wifi", bt_toggle)

    for row in [brightness_row, sound_row, vpn_row, bluetooth_row, wifi_row]:
        row.set_vexpand(False)
        center_box.append(row)

    main_box.append(center_box)

    # Sound Page
    sound_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=40)
    sound_page.set_halign(Gtk.Align.CENTER)
    sound_page.set_valign(Gtk.Align.CENTER)
    sound_page.set_opacity(0.0)
    sound_page.set_visible(False)
    sound_label = Gtk.Label(label="🎧 Sound Settings Page")
    sound_label.set_css_classes(["label"])
    back_button = Gtk.Button(label="‹ Back")
    sound_page.append(sound_label)
    sound_page.append(back_button)

    overlay.set_child(main_box)
    overlay.add_overlay(sound_page)

    sound_click = Gtk.GestureClick()
    sound_click.connect("pressed", lambda *_: animate_transition(main_box, sound_page, overlay))
    sound_row.add_controller(sound_click)

    back_button.connect("clicked", lambda *_: animate_transition(sound_page, main_box, overlay))

    controller = Gtk.EventControllerKey()
    controller.connect("key-pressed", on_key_press)
    window.add_controller(controller)

    window.set_child(overlay)
    window.present()
    window.set_focus(window)

app = Gtk.Application(application_id="com.example.LayerShellButtons")
app.connect("activate", on_activate)
app.run()
