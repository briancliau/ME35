from machine import Pin
import neopixel
import time
from time import ticks_ms, ticks_diff

btn = Pin(34, Pin.IN, Pin.PULL_UP) 
DEBOUNCE_MS = 200
last_press = 0
lights = neopixel.NeoPixel(Pin(15), 4)
x = 0
y = 0
z = 0

def button_handler(pin):
    global last_press
    now = ticks_ms()
    if ticks_diff(now, last_press) > DEBOUNCE_MS:
        if (pin.value() == 0):
            last_press = now
            print("Button pressed!")
            
            if 0 < x < 255:
                x += 30
            else:
                x = 0

            if 0 < y < 255:
                y -= 30
            else:
                y = 255

            if 0 < z < 255:
                z = 0
            else:
                z = 255
            
            lights[0] = (x, y, z)
            lights[1] = (y, z, x)
            lights.write()
            time.sleep_ms(200)
            

btn.irq(trigger=Pin.IRQ_FALLING, handler=button_handler)

while True: 
    lights[0] = (0, 0, 0)
    lights[1] = (0, 0, 0)
    lights.write()
        


