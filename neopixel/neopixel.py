from machine import Pin
import neopixel
import time

lights = neopixel.NeoPixel(Pin(15), 4)

x = 0
y = 0
z = 0

for i in range(350):
    if 0 < x < 50:
        x += 1
    else:
        x = 0

    if 0 < y < 50:
        y -= 1
    else:
        y = 50

    z = 0

    if i % 2 == 0:
        if i % 6 == 2:
            lights[0] = (x, y, z)
            lights[1] = (y, z, x)
        if i % 6 == 4:
            lights[0] = (y, x, z)
            lights[1] = (x, z, y)
        else:
            lights[0] = (y, z, x)
            lights[1] = (z, y, x)
    else:
        lights[0] = (0, 0, 0)
        lights[1] = (0, 0, 0)

    lights.write() 
    time.sleep_ms(1000)
