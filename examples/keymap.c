#include QMK_KEYBOARD_H

/* THIS FILE WAS GENERATED!
 *
 * This file was generated by qmk json2c. You may or may not want to
 * edit it directly.
 */

layer_state_t layer_state_set_user(layer_state_t state)
{
	// Your custom logic to determine the active layer(s)
	uint8_t layer = get_highest_layer(state);
	uprintf("Active layer: %d\n", layer);

	return state;
}

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
	[0] = LAYOUT_split_3x5_3(KC_Q, KC_W, KC_F, KC_P, KC_B, KC_J, KC_L, KC_U, KC_Y, KC_SCLN, LGUI_T(KC_A), LALT_T(KC_R), LCTL_T(KC_S), LSFT_T(KC_T), KC_G, KC_M, RSFT_T(KC_N), LCTL_T(KC_E), LALT_T(KC_I), LGUI_T(KC_O), KC_Z, KC_X, KC_C, KC_D, LT(5, KC_V), LT(1, KC_K), KC_H, KC_COMM, KC_DOT, KC_SLSH, LT(6, KC_ESC), LT(3, KC_SPC), LT(5, KC_TAB), LT(1, KC_ENT), LT(2, KC_BSPC), LT(4, KC_DEL)),
	[1] = LAYOUT_split_3x5_3(KC_VOLU, KC_WH_L, KC_MS_U, KC_WH_U, KC_WH_R, KC_NO, KC_NO, KC_NO, KC_NO, QK_RBT, KC_MS_L, KC_BTN2, KC_BTN1, KC_MS_R, KC_MUTE, KC_NO, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_VOLD, KC_MNXT, KC_MS_D, KC_WH_D, KC_MPLY, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_TRNS, KC_TRNS, KC_NO, KC_NO, KC_NO),
	[2] = LAYOUT_split_3x5_3(KC_NO, KC_HOME, KC_DEL, KC_PGUP, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_LEFT, KC_UP, KC_RGHT, KC_NO, KC_NO, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_NO, KC_END, KC_DOWN, KC_PGDN, KC_NO, KC_NO, KC_BTN1, KC_BTN2, KC_BTN3, KC_BTN4, KC_NO, KC_TRNS, KC_TRNS, KC_NO, KC_NO, KC_NO),
	[3] = LAYOUT_split_3x5_3(KC_NO, KC_NO, KC_NO, KC_NO, KC_WH_U, KC_AT, KC_UNDS, KC_PIPE, KC_GRV, KC_PERC, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, RGB_TOG, KC_HASH, KC_TAB, KC_EXLM, KC_DQUO, KC_DLR, KC_BTN4, KC_BTN3, KC_BTN2, KC_BTN1, KC_WH_D, KC_TILD, KC_QUOT, KC_BSLS, KC_SLSH, KC_AMPR, KC_NO, KC_NO, KC_NO, KC_TRNS, KC_TRNS, KC_NO),
	[4] = LAYOUT_split_3x5_3(KC_EQL, KC_CIRC, KC_LT, KC_GT, KC_SCLN, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_LCBR, KC_RCBR, KC_LPRN, KC_RPRN, KC_AT, KC_NO, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_MINS, KC_EXLM, KC_LBRC, KC_RBRC, KC_TRNS, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_TRNS, KC_TRNS, KC_TRNS, KC_NO, KC_NO),
	[5] = LAYOUT_split_3x5_3(QK_RBT, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_F7, KC_F8, KC_F9, KC_F10, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_NO, KC_NO, KC_F4, KC_F5, KC_F6, KC_F11, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_F1, KC_F2, KC_F3, KC_F12, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS),
	[6] = LAYOUT_split_3x5_3(RGB_SPI, RGB_VAI, RGB_SAI, RGB_HUI, RGB_MOD, KC_PPLS, KC_P7, KC_P8, KC_P9, KC_PAST, EE_CLR, KC_TRNS, KC_TRNS, KC_TRNS, RGB_TOG, KC_PMNS, KC_P4, KC_P5, KC_P6, KC_PSLS, RGB_SPD, RGB_VAD, RGB_SAD, RGB_HUD, RGB_RMOD, KC_PDOT, KC_P1, KC_P2, KC_P3, KC_PEQL, KC_NO, KC_NO, KC_NO, KC_0, KC_COMM, KC_P0)};

#if defined(ENCODER_ENABLE) && defined(ENCODER_MAP_ENABLE)
const uint16_t PROGMEM encoder_map[][NUM_ENCODERS][NUM_DIRECTIONS] = {

};
#endif // defined(ENCODER_ENABLE) && defined(ENCODER_MAP_ENABLE)