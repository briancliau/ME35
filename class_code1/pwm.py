from machine import Pin, PWM
import time

pwm = PWM(Pin(4))
pwm.freq(50)
# pwm.duty_u16(32768)
while True: 
    pwm.duty_u16(1638)
    time.sleep_ms(1000)
    pwm.duty_u16(3277) 
    time.sleep_ms(1000)
    pwm.duty_u16(4915)
    # time.sleep_ms(1000)
    # pwm.duty_u16(7919)
    # time.sleep_ms(1000)


# 0 degrees = 1583, 90 degrees = 4915, 180 degrees = 7919