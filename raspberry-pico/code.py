import time
import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

kbd = Keyboard(usb_hid.devices)

# define first button (ESC, GRAVE_ACCENT, BACKSLASH)
button1 = digitalio.DigitalInOut(board.GP10)
button1.direction = digitalio.Direction.INPUT
button1.pull = digitalio.Pull.DOWN

# define second button (TAB)
button2 = digitalio.DigitalInOut(board.GP11)
button2.direction = digitalio.Direction.INPUT
button2.pull = digitalio.Pull.DOWN

while True:
    # Check if the first button is pressed
    if button1.value:
        kbd.press(Keycode.ESCAPE)
        time.sleep(0.1)
        kbd.release(Keycode.ESCAPE)
        time.sleep(0.1)
        kbd.press(Keycode.GRAVE_ACCENT)
        time.sleep(0.1)
        kbd.release(Keycode.GRAVE_ACCENT)
        time.sleep(0.1)
        kbd.press(Keycode.RIGHT_BRACKET)
        time.sleep(0.1)
        kbd.release(Keycode.RIGHT_BRACKET)
        time.sleep(0.1)
        
        print("Button 1 pressed")
    
    # Check if the second button is pressed
    if button2.value:
        kbd.press(Keycode.BACKSLASH)
        time.sleep(0.1)
        kbd.release(Keycode.BACKSLASH)
        time.sleep(0.1)
        print("Button 2 pressed")

    time.sleep(0.1)
