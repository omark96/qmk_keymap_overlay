import glob
import os
import json
import hjson
import tkinter as tk
from tkinter import font as tkFont
from tkinter import ttk
from threading import Thread
from threading import Event
import hid
import time


def load_keymap():
    keycodes = load_keycodes()
    with open(
        "../keyboards/"
        + keyboard_config["keyboard"]
        + "/keymaps/"
        + keyboard_config["keymap"]
        + "/keymap.json"
    ) as f:
        data = json.load(f)
    keymap_layers_unfiltered = data["layers"]
    keymap_layers_filtered = []
    for layer in keymap_layers_unfiltered:
        layer_filtered = []
        for key in layer:
            if key in keycodes.keys():
                layer_filtered.append(keycodes[key])
            else:
                layer_filtered.append(key)
        keymap_layers_filtered.append(layer_filtered)
    return keymap_layers_filtered


def load_keycodes():
    keycode_directory = "../data/constants/keycodes/"
    keycode_hjson_files = os.listdir(keycode_directory)

    for x in range(len(keycode_hjson_files)):
        keycode_hjson_files[x] = os.path.join(keycode_directory, keycode_hjson_files[x])

    keycodes_unfiltered = []
    for keycode_hjson_file in keycode_hjson_files:
        if keycode_hjson_file.endswith(".hjson"):
            with open(keycode_hjson_file, "r") as file:
                data = hjson.load(file)
                if "keycodes" in data.keys():
                    keycodes_unfiltered.append(data["keycodes"])

    keycodes_filtered = {}
    for keycodes in keycodes_unfiltered:
        for keycode, values in keycodes.items():
            try:
                if "label" in values.keys():
                    keycodes_filtered[values["key"]] = values["label"]
                    if "aliases" in values.keys():
                        for alias in values["aliases"]:
                            keycodes_filtered[alias] = values["label"]
            except:
                pass
    with open(
        keycode_directory + "extras/keycodes_us_0.0.1.hjson", "r", encoding="utf8"
    ) as file:
        data = hjson.load(file)
        for keycode in data["aliases"]:
            keycodes_filtered[data["aliases"][keycode]["key"]] = data["aliases"][
                keycode
            ]["label"]
            if "aliases" in data["aliases"][keycode].keys():
                for alias in data["aliases"][keycode]["aliases"]:
                    keycodes_filtered[alias] = data["aliases"][keycode]["label"]
    return keycodes_filtered


def fade_in(step=0, steps=30):
    alpha = keyboard_config["transparency"]
    if showing and step < steps:
        progress = step / steps
        ease = (1 - progress) * (1 - progress)
        new_alpha = alpha * (1 - ease)
        root.wm_attributes("-alpha", new_alpha)
        root.after(10, lambda: fade_in(step + 1, steps))
    else:
        root.wm_attributes("-alpha", keyboard_config["transparency"])


def show_window():
    # root.overrideredirect(1)
    global showing
    root.attributes("-topmost", True)
    root.update()
    root.attributes("-topmost", False)

    if not showing:
        showing = True
        fade_in(0, keyboard_config["fade_in_steps"])


def fade_out(step=0, steps=30):
    if not showing and step < steps:
        alpha = root.wm_attributes("-alpha")
        progress = step / steps
        ease = (1 - progress) * (1 - progress)
        new_alpha = alpha * ease
        root.wm_attributes("-alpha", new_alpha)
        root.after(30, lambda: fade_out(step + 1, steps))
    else:
        root.wm_attributes("-alpha", 0)

    # if alpha > 0:
    #     alpha -= 0.1
    #     root.wm_attributes("-alpha", alpha)
    #     root.after(20, fade_out)


def hide_window():
    global showing
    # root.withdraw()
    # root.wm_attributes("-alpha", 0)
    if showing:
        showing = False
        fade_out(0, keyboard_config["fade_out_steps"])
    root.overrideredirect(0)


def quit_program():
    root.destroy()


def swap_layer(layer):
    auto_hide_window = keyboard_config["auto_hide"]
    if layer == "0" and auto_hide_window:
        hide_window()
    else:
        root.after(1, layer_frames[layer].tkraise())
        show_window()


def swap_to_main_menu(event=None):
    global layer_frames
    show_window()
    for frame in layer_frames:
        layer_frames[frame].destroy()
    stop_HID_event.set()
    main_menu.tkraise()


def create_layer_frames(root, keymap_layers, keyboard_layout):
    """
    Creates a dictionary of frames for each layer in the keymap.

    :param root: The parent Tkinter window.
    :param rows: Number of rows in the grid.
    :param columns: Number of columns in the grid.
    :param square_size: Size of each square in pixels.
    :param texts: List of texts for each square.
    """
    layer_frames = {}

    max_x = max(item["x"] for item in keyboard_layout)
    max_y = max(item["y"] for item in keyboard_layout)
    square_size = keyboard_config["square_size"]
    label_font = tkFont.Font(family="Helvetica", size=keyboard_config["font_size"])

    for layer_index, keymap_layer in enumerate(keymap_layers):
        layer_frame = tk.Frame(
            root,
            bg=theme["bg"],
            padx=20,
            pady=20,
            width=square_size * (max_x + 1) + 25,
            height=square_size * (max_y + 1) + 25,
        )
        layer_frame.grid(row=0, column=0, sticky="nsew")
        for index, key in enumerate(keymap_layer):
            x_cord = keyboard_layout[index]["x"] * square_size
            y_cord = keyboard_layout[index]["y"] * square_size
            label = tk.Label(
                layer_frame,
                text=key,
                bg=theme["key_bg"],
                fg=theme["fg"],
                font=label_font,
                wraplength=square_size * 0.9,
            )
            label.place(
                x=x_cord,
                y=y_cord,
                width=square_size - 10,
                height=square_size - 10,
            )
        layer_frames[str(layer_index)] = layer_frame
    return layer_frames


def load_keyboard_layout():
    try:
        with open(
            "../keyboards/"
            + keyboard_config["keyboard"]
            + "/"
            + keyboard_config["revision"]
            + "/info.json"
        ) as f:
            data = json.load(f)
        keyboard_layout = data["layouts"][keyboard_config["layout"]]["layout"]
        return keyboard_layout
    except:
        print("No such layout")
        exit()


def stop_HID_listener(event):
    event.set()


def start_HID_listener(stop_HID_event, paused_event):
    # Replace these with your keyboard's VID and PID
    VID = keyboard_config["VID"]
    PID = keyboard_config["PID"]

    try:
        # Open the device
        h = hid.device()
        h.open(VID, PID)

        # Set the non-blocking mode
        h.set_nonblocking(1)

        print("Listening for debug info...")
        while not stop_HID_event.is_set():
            data = h.read(2)  # Adjust the size as necessary
            if data:
                print(data)
                layer = chr(data[0])
                print("Received message:", layer)
                if layer.isnumeric():
                    swap_layer(layer)
            time.sleep(0.01)

    except IOError as e:
        print(e)
        swap_to_main_menu()

    finally:
        h.close()


def get_USB_info(path_to_info_json, vid_or_pid):
    try:
        with open(path_to_info_json) as f:
            data = json.load(f)
        ID = data["usb"][vid_or_pid]
        return int(ID, 16)
    except:
        print("No such device")
        exit()


def get_VID(keyboard, revision):
    path_to_info_json = os.path.join("../keyboards", keyboard, revision, "info.json")
    return get_USB_info(path_to_info_json, "vid")


def get_PID(keyboard, revision):
    path_to_info_json = os.path.join("../keyboards", keyboard, revision, "info.json")
    return get_USB_info(path_to_info_json, "pid")


def start_layout_overlay(config):
    global layer_frames
    global keyboard_config
    global stop_HID_event
    keyboard_config = {
        "keyboard": os.path.join(config["maker"].get(), config["keyboard"].get()),
        "revision": config["revision"].get(),
        "layout": config["layout"].get(),
        "keymap": config["keymap"].get(),
        "keycode_directory": "data/constants/keycodes/",
        "square_size": config["square_size"].get(),
        "font_size": config["font_size"].get(),
        "auto_hide": config["auto_hide"].get(),
        "fade_in_steps": config["fade_in_steps"].get(),
        "fade_out_steps": config["fade_out_steps"].get(),
        "transparency": config["transparency"].get(),
    }
    keyboard_config["VID"] = get_VID(
        keyboard_config["keyboard"], keyboard_config["revision"]
    )
    keyboard_config["PID"] = get_PID(
        keyboard_config["keyboard"], keyboard_config["revision"]
    )
    paused_event.clear()
    stop_HID_event.clear()
    try:
        HID_listener = Thread(
            target=start_HID_listener, args=(stop_HID_event, paused_event)
        )
        HID_listener.start()
        keymap = load_keymap()
        keyboard_layout = load_keyboard_layout()
        layer_frames = create_layer_frames(root, keymap, keyboard_layout)
        swap_layer("0")
    except IOError as e:
        stop_HID_event.set()
        print(e)
        return


def print_config(config):
    for key in config:
        try:
            print(config[key].get())
        except:
            print("Can't print:", key)
            print(config[key])


def get_makers():
    makers = []
    for path in glob.glob("../keyboards/*/"):
        normalized_path = os.path.normpath(path)
        maker_name = os.path.basename(normalized_path)
        makers.append(maker_name)
    return makers


def get_keyboards(maker):
    keyboards = []
    path_to_maker = os.path.join("../keyboards/" + maker + "/")
    if not os.path.exists(path_to_maker + "/rules.mk"):
        for path in glob.glob(path_to_maker + "*/"):
            normalized_path = os.path.normpath(path)
            keyboard_name = os.path.basename(normalized_path)
            keyboards.append(keyboard_name)
    if "keymaps" in keyboards:
        keyboards.remove("keymaps")
    return keyboards


def get_revisions(maker, keyboard):
    revisions = []
    path_to_keyboard = os.path.join("../keyboards", maker, keyboard, "*/")
    for path in glob.glob(path_to_keyboard):
        normalized_path = os.path.normpath(path)
        revision_name = os.path.basename(normalized_path)
        revisions.append(revision_name)
    if "keymaps" in revisions:
        revisions.remove("keymaps")
    return revisions


def get_layouts(maker, keyboard, revision):
    layouts = []
    path_to_info_json = os.path.join(
        "../keyboards", maker, keyboard, revision, "info.json"
    )
    with open(path_to_info_json, "r") as f:
        data = json.load(f)
    for key in data["layouts"]:
        layouts.append(key)
    return layouts


def get_keymaps(maker, keyboard):
    keymaps = []
    path_to_keymaps = os.path.join("../keyboards", maker, keyboard, "keymaps/*/")
    for path in glob.glob(path_to_keymaps):
        keymap_path = os.path.join(path, "keymap.json")
        if os.path.isfile(keymap_path):
            normalized_path = os.path.normpath(path)
            keymap_name = os.path.basename(normalized_path)
            keymaps.append(keymap_name)
    return keymaps


def update_keyboard_combobox(keyboard_combobox, maker):
    keyboards = get_keyboards(maker)
    keyboard_combobox["values"] = keyboards
    if keyboards:
        keyboard_combobox["state"] = "normal"
        keyboard_combobox.current(0)
    else:
        keyboard_combobox.set("")
        keyboard_combobox["state"] = "disabled"


def update_revision_combobox(revision_combobox, maker, keyboard):
    revisions = get_revisions(maker, keyboard)
    revision_combobox["values"] = revisions
    if revisions:
        revision_combobox["state"] = "normal"
        revision_combobox.current(0)
    else:
        revision_combobox.set("")
        revision_combobox["state"] = "disabled"


def update_layout_combobox(layout_combobox, maker, keyboard, revision):
    layouts = get_layouts(maker, keyboard, revision)
    layout_combobox["values"] = layouts
    if layouts:
        layout_combobox["state"] = "normal"
        layout_combobox.current(0)
    else:
        layout_combobox.set("")
        layout_combobox["state"] = "disabled"


def update_keymap_combobox(keymap_combobox, maker, keyboard):
    keymaps = get_keymaps(maker, keyboard)
    keymap_combobox["values"] = keymaps
    if keymaps:
        keymap_combobox["state"] = "normal"
        keymap_combobox.current(0)
    else:
        keymap_combobox.set("")
        keymap_combobox["state"] = "disabled"


def load_user_settings():
    with open("user_settings.json") as f:
        user_settings = json.load(f)
    return user_settings


def export_user_settings(config):
    user_settings = {}
    for key in config:
        try:
            user_settings[key] = config[key].get()
        except:
            print("Error exporting key.")
    with open("user_settings.json", "w") as f:
        json.dump(user_settings, f, indent=4)


def update_window_transparency(value):
    if value < 0.1:
        value = 0.1
    root.wm_attributes("-alpha", value)


def create_main_menu(root):
    main_menu = tk.Frame(root, bg=theme["bg"], padx=30, pady=30)

    user_settings = load_user_settings()

    config = {
        "maker": tk.StringVar(main_menu, value=user_settings.get("maker")),
        "keyboard": tk.StringVar(main_menu, value=user_settings.get("keyboard")),
        "revision": tk.StringVar(main_menu, value=user_settings.get("revision")),
        "layout": tk.StringVar(main_menu, value=user_settings.get("layout")),
        "keymap": tk.StringVar(main_menu, value=user_settings.get("keymap")),
        "square_size": tk.IntVar(main_menu, value=user_settings.get("square_size")),
        "font_size": tk.IntVar(main_menu, value=user_settings.get("font_size")),
        "auto_hide": tk.BooleanVar(main_menu, value=user_settings.get("auto_hide")),
        "fade_in_steps": tk.IntVar(main_menu, value=user_settings.get("fade_in_steps")),
        "fade_out_steps": tk.IntVar(
            main_menu, value=user_settings.get("fade_out_steps")
        ),
        "transparency": tk.DoubleVar(
            main_menu, value=user_settings.get("transparency")
        ),
    }
    update_window_transparency(config["transparency"].get())
    maker_label = tk.Label(main_menu, text="Maker", bg=theme["bg"], fg=theme["fg"])
    keyboard_label = tk.Label(
        main_menu, text="Keyboard", bg=theme["bg"], fg=theme["fg"]
    )
    revision_label = tk.Label(
        main_menu, text="Revision", bg=theme["bg"], fg=theme["fg"]
    )
    layout_label = tk.Label(main_menu, text="Layout", bg=theme["bg"], fg=theme["fg"])
    keymap_label = tk.Label(main_menu, text="Keymap", bg=theme["bg"], fg=theme["fg"])

    separator = ttk.Separator(main_menu, orient="vertical")

    square_size_label = tk.Label(
        main_menu, text="Square size", bg=theme["bg"], fg=theme["fg"]
    )
    font_size_label = tk.Label(
        main_menu, text="Font size", bg=theme["bg"], fg=theme["fg"]
    )
    toggle_label = tk.Label(main_menu, text="Auto-hide", bg=theme["bg"], fg=theme["fg"])
    fade_in_label = tk.Label(
        main_menu, text="Fade in steps", bg=theme["bg"], fg=theme["fg"]
    )
    fade_out_label = tk.Label(
        main_menu, text="Fade out steps", bg=theme["bg"], fg=theme["fg"]
    )
    transparency_label = tk.Label(
        main_menu, text="Transparency", bg=theme["bg"], fg=theme["fg"]
    )

    maker_combobox = ttk.Combobox(main_menu, textvariable=config["maker"])
    keyboard_combobox = ttk.Combobox(main_menu, textvariable=config["keyboard"])
    revision_combobox = ttk.Combobox(main_menu, textvariable=config["revision"])
    layout_combobox = ttk.Combobox(main_menu, textvariable=config["layout"])
    keymap_combobox = ttk.Combobox(main_menu, textvariable=config["keymap"])

    square_size_spinbox = ttk.Spinbox(
        main_menu, from_=1.0, to=200.0, textvariable=config["square_size"]
    )
    font_size_spinbox = ttk.Spinbox(
        main_menu, from_=1.0, to=100.0, textvariable=config["font_size"]
    )
    toggle_checkbox = ttk.Checkbutton(main_menu, variable=config["auto_hide"])
    fade_in_spinbox = ttk.Spinbox(
        main_menu, from_=0, to=100.0, textvariable=config["fade_in_steps"]
    )
    fade_out_spinbox = ttk.Spinbox(
        main_menu, from_=0, to=100.0, textvariable=config["fade_out_steps"]
    )
    transparency_spinbox = ttk.Spinbox(
        main_menu,
        from_=0.1,
        to=1.0,
        increment=0.01,
        textvariable=config["transparency"],
    )
    export_button = tk.Button(
        main_menu, text="Export", command=lambda: export_user_settings(config)
    )
    start_button = tk.Button(
        main_menu, text="Start", command=lambda: start_layout_overlay(config)
    )
    # print_button = tk.Button(
    #     main_menu, text="Print", command=lambda: print_config(config)
    # )

    maker_combobox["values"] = get_makers()
    if config["maker"].get() == "":
        maker_combobox.set(get_makers()[0])
    update_keyboard_combobox(keyboard_combobox, config["maker"].get())
    update_revision_combobox(
        revision_combobox, config["maker"].get(), config["keyboard"].get()
    )
    update_layout_combobox(
        layout_combobox,
        config["maker"].get(),
        config["keyboard"].get(),
        config["revision"].get(),
    )
    update_keymap_combobox(
        keymap_combobox, config["maker"].get(), config["keyboard"].get()
    )

    config["maker"].trace_add(
        "write",
        lambda var, index, mode: update_keyboard_combobox(
            keyboard_combobox, config["maker"].get()
        ),
    )

    config["keyboard"].trace_add(
        "write",
        lambda var, index, mode: update_revision_combobox(
            revision_combobox, config["maker"].get(), config["keyboard"].get()
        ),
    )
    config["revision"].trace_add(
        "write",
        lambda var, index, mode: update_layout_combobox(
            layout_combobox,
            config["maker"].get(),
            config["keyboard"].get(),
            config["revision"].get(),
        ),
    )
    config["keyboard"].trace_add(
        "write",
        lambda var, index, mode: update_keymap_combobox(
            keymap_combobox, config["maker"].get(), config["keyboard"].get()
        ),
    )
    config["transparency"].trace_add(
        "write",
        lambda var, index, mode: update_window_transparency(
            config["transparency"].get()
        ),
    )

    main_menu.grid(row=0, column=0, sticky="nsew")

    maker_label.grid(column=0, row=0)
    keyboard_label.grid(column=0, row=1)
    revision_label.grid(column=0, row=2)
    layout_label.grid(column=0, row=3)
    keymap_label.grid(column=0, row=4)

    maker_combobox.grid(column=1, row=0)
    keyboard_combobox.grid(column=1, row=1)
    revision_combobox.grid(column=1, row=2)
    layout_combobox.grid(column=1, row=3)
    keymap_combobox.grid(column=1, row=4)

    separator.grid(column=2, row=0, rowspan=5, sticky="ns", padx=30)

    square_size_label.grid(column=3, row=0)
    font_size_label.grid(column=3, row=1)
    fade_in_label.grid(column=3, row=2)
    fade_out_label.grid(column=3, row=3)
    transparency_label.grid(column=3, row=4)
    toggle_label.grid(column=3, row=5)

    square_size_spinbox.grid(column=4, row=0)
    font_size_spinbox.grid(column=4, row=1)
    fade_in_spinbox.grid(column=4, row=2)
    fade_out_spinbox.grid(column=4, row=3)
    transparency_spinbox.grid(column=4, row=4)
    toggle_checkbox.grid(column=4, row=5)

    export_button.grid(column=3, row=7, pady=(20, 0))
    start_button.grid(column=4, row=7, pady=(20, 0))

    return main_menu


def start_move(event):
    global x
    global y
    x = event.x
    y = event.y


def stop_move(event):
    global x
    global y
    x = None
    y = None


def do_move(event):
    global x
    global y
    deltax = event.x - x
    deltay = event.y - y
    x = root.winfo_x() + deltax
    y = root.winfo_y() + deltay
    root.geometry(f"+{x}+{y}")


def SaveLastClickPos(event):
    global lastClickX, lastClickY
    lastClickX = event.x
    lastClickY = event.y


def Dragging(event):
    x, y = event.x - lastClickX + root.winfo_x(), event.y - lastClickY + root.winfo_y()
    root.geometry("+%s+%s" % (x, y))


if __name__ == "__main__":
    keyboard_config = {}
    theme = {
        "bg": "#0D1117",
        "fg": "white",
        "key_bg": "#1E242E",
    }
    # UI
    root = tk.Tk()
    root.title("Keymap Overlay")
    root.iconbitmap("icon.ico")
    root.configure(bg="#333333")
    root.resizable(False, False)
    showing = True
    # root.overrideredirect(1)

    # Start HID listener
    stop_HID_event = Event()
    paused_event = Event()

    root.bind("<Escape>", swap_to_main_menu)
    root.bind("<Button-3>", swap_to_main_menu)
    # Draggable window
    lastClickX = 0
    lastClickY = 0
    root.bind("<Button-1>", SaveLastClickPos)
    root.bind("<B1-Motion>", Dragging)
    # Label font

    layer_frames = {}

    main_menu = create_main_menu(root)

    swap_to_main_menu()
    root.mainloop()
    stop_HID_listener(stop_HID_event)
