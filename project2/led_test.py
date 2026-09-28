from machine import Pin, PWM
import time
from time import ticks_ms, ticks_diff

red = PWM(Pin(18))
green = PWM(Pin(19))
blue = PWM(Pin(21))
red.freq(50)
green.freq(50)
blue.freq(50)

pwm1 = PWM(Pin(4))
pwm2 = PWM(Pin(5))
pwm1.freq(50)
pwm2.freq(50)

button1 = Pin(22, Pin.IN, Pin.PULL_UP) 
button2 = Pin(23, Pin.IN, Pin.PULL_UP)
DEBOUNCE_MS = 200
last_press_1 = 0
last_press_2 = 0

def set_rgb(r, g, b):
    red.duty_u16(int(((255-r) / 255) * 65535))
    green.duty_u16(int(((255-g) / 255) * 65535))
    blue.duty_u16(int(((255-b) / 255) * 65535))
    

def weather_handler(pin):
    global last_press_1
    global state
    now = ticks_ms()
    if ticks_diff(now, last_press_1) > DEBOUNCE_MS:
        if (pin.value() == 0):
            last_press_1 = now
            set_rgb(255, 0, 0)
            time.sleep_ms(1000)
            
def timer_handler(pin):
    global last_press_2
    global state
    now = ticks_ms()
    if ticks_diff(now, last_press_2) > DEBOUNCE_MS:
        if (pin.value() == 0):
            last_press_2 = now
            set_rgb(0, 0, 255)
            time.sleep_ms(1000)

button1.irq(trigger=Pin.IRQ_FALLING, handler=weather_handler)
button2.irq(trigger=Pin.IRQ_FALLING, handler=timer_handler)

while True:
    set_rgb(128, 60, 0)
    pwm1.duty_u16(1638)
    pwm2.duty_u16(8192)    
