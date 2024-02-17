# QMK Keymap Overlay
A simple tool for displaying an overlay of your QMK keymap on Windows. This is meant for whenever you're trying to learn a new layout and want an easy way to check your layout.

Main menu:

![Main menu](https://github.com/omark96/qmk_keymap_overlay/assets/43138339/13dd1a12-f159-4688-8e3a-57708e65ffea)

Overlay:

![Skärmbild 2024-02-17 045939](https://github.com/omark96/qmk_keymap_overlay/assets/43138339/e474927c-d0e3-4248-ba64-7238b6eebead)

## Features
* Always on top while writing.
* Supports auto-hiding when base layer is active.
* Loads all the necessary data from your QMK folder. Such as keymaps, VID and PID for your keyboard and keycodes.

## How to use
### Required files and python modules
Clone the qmk_firmware.

Place the qmk_keymap_overlay folder directly inside the qmk_firmware folder.

`qmk_firmware/qmk_keymap_overlay/main.py`

It is important that it's placed directly in the qmk_firmware directory for the program to find the files and folders it needs to function.

Install the following packages that the program depends on:

```powershell
pip install hidapi
pip install hjson
```

### Configure your keyboard
The program relies on debug information being sent from your keyboard to operate, as such you will have to flash a keymap with a custom function added to it.

Firstly you will need to convert your `keymap.json` to a `keymap.c` file and add the following to your keymap:

```c
layer_state_t layer_state_set_user(layer_state_t state)
{
	// Your custom logic to determine the active layer(s)
	uint8_t layer = get_highest_layer(state);
	uprintf("%d\n", layer);

	return state;
}
```
For an example keymap check out the [example](examples/keymap.c) in the repo. This code will send a message to the overlay program every time you change layer.

Next you need to make sure that console is enabled for your keyboard, by for example editting your `rules.mk` and adding:
```
CONSOLE_ENABLE = yes
```

### Run the program:

```powershell
python main.py
```
The program requires that you have a `keymap.json` file for your keyboard. If you only have a `keymap.c` file you will have to convert it to .json.

### Alternative to requiring the full QMK repo

The program does not require the full QMK repo to function, as long as your folder structure looks like this it is fine:
```
QMK_folder/
├─ keyboards/
│  ├─ your_keyboard/
├─ data/
│  ├─ constants/
│  │  ├─ keycodes/
├─ keymap_overlay/
│  ├─ main.py
│  ├─ user_settings.json
│  ├─ icon.ico

```


## TODO:
* Change hardcoded path to qmk_firmware to allow users to place the script in another folder.
* Refactor how keymaps and keycodes are loaded

## Known Issues
* Not all keycodes are supported and the function for loading the keycodes will need a refactor. If no label is found for the keycode it will simply display the raw keycode.
* Yes, the code is not organized, for your own sanity do not have high expectations when checking the code, let it be known that you have been warned.
