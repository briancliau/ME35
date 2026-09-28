from machine import Pin, PWM
import time

motor1 = PWM(Pin(4), freq = 50)
motor2 = PWM(Pin(5), freq = 50)

DUTY_MID = 4915
DUTY_45  = 3277
DUTY_135 = 6553

def put_in_middle():
    motor1.duty_u16(DUTY_MID)
    motor2.duty_u16(DUTY_MID)

def put_in_1():
    motor2.duty_u16(DUTY_135)    
    motor1.duty_u16(DUTY_45)
    
def put_in_2():
    motor1.duty_u16(DUTY_135)
    motor2.duty_u16(DUTY_45)
    





