import servo , time
from machine import Pin
servo1 = servo.Servo(Pin(5)) # change this
servo2 = servo.Servo(Pin(4)) # and this

servo1.write_angle(30)
servo2.write_angle(60)
