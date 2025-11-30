import time
import board#type:ignore
import digitalio#type:ignore
import neopixel#type:ignore
import rotaryio#type:ignore
from adafruit_hid.keyboard import Keyboard#type:ignore
from adafruit_hid.keycode import Keycode#type:ignore
from adafruit_hid.consumer_control import ConsumerControl#type:ignore
from adafruit_hid.consumer_control_code import ConsumerControlCode#type:ignore
import rainbowio#type:ignore  # For nice rainbow colors

# -----------------------------
# CONFIG
# -----------------------------
NUM_LEDS = 7
PIXEL_PIN = board.GP3

# Button pins
BUTTON_PINS = [board.GP4, board.GP2, board.GP1, board.GP0, board.GP7, board.GP6, board.GP29]

# Rotary encoder pins
ENCODER_PIN_A = board.GP28
ENCODER_PIN_B = board.GP27
ENCODER_BUTTON = board.GP26  # S1

# -----------------------------
# SETUP DEVICES
# -----------------------------

# Neopixels
pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_LEDS, brightness=0.3, auto_write=True)

# Push buttons
buttons = []
for pin in BUTTON_PINS:
    b = digitalio.DigitalInOut(pin)
    b.direction = digitalio.Direction.INPUT
    b.pull = digitalio.Pull.UP
    buttons.append(b)

# Rotary encoder
encoder = rotaryio.IncrementalEncoder(ENCODER_PIN_A, ENCODER_PIN_B)
last_position = encoder.position

# Encoder button
encoder_btn = digitalio.DigitalInOut(ENCODER_BUTTON)
encoder_btn.direction = digitalio.Direction.INPUT
encoder_btn.pull = digitalio.Pull.UP

# HID devices
kbd = Keyboard()
cc = ConsumerControl()

# -----------------------------
# PUSH BUTTON MAPPINGS
# -----------------------------
button_keys = [
    (Keycode.CONTROL, Keycode.T),          # Button 1
    (Keycode.CONTROL, Keycode.W),          # Button 2
    (Keycode.CONTROL, Keycode.SHIFT, Keycode.T), # Button 3
    (Keycode.WINDOWS, Keycode.ONE),        # Button 4
    (Keycode.WINDOWS, Keycode.TWO),        # Button 5
    (Keycode.WINDOWS, Keycode.THREE),      # Button 6
    (Keycode.WINDOWS, Keycode.FOUR)        # Button 7
]

# -----------------------------
# NEOPIXEL RAINBOW
# -----------------------------
def rainbow_cycle(wait=0.02):
    for i in range(NUM_LEDS):
        pixel_index = (i * 256 // NUM_LEDS) + rainbow_cycle.index
        pixels[i] = rainbowio.colorwheel(pixel_index & 255)
    rainbow_cycle.index = (rainbow_cycle.index + 1) % 256
rainbow_cycle.index = 0

# -----------------------------
# MAIN LOOP
# -----------------------------
while True:
    # ----- ROTARY ENCODER -----
    position = encoder.position
    if position != last_position:
        if position > last_position:
            cc.send(ConsumerControlCode.VOLUME_INCREMENT)
        else:
            cc.send(ConsumerControlCode.VOLUME_DECREMENT)
        last_position = position

    # ----- ENCODER BUTTON -----
    if not encoder_btn.value:  # pressed (active low)
        cc.send(ConsumerControlCode.PLAY_PAUSE)
        time.sleep(0.2)  # debounce

    # ----- PUSH BUTTONS -----
    for i, b in enumerate(buttons):
        if not b.value:  # pressed (active low)
            keys = button_keys[i]
            kbd.press(*keys)
            kbd.release_all()
            time.sleep(0.2)  # simple debounce

    # ----- RAINBOW ANIMATION -----
    rainbow_cycle()
    pixels.show()
    time.sleep(0.02)
