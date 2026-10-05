from machine import Pin, PWM
import time

servo_motor1 = PWM(Pin(4), freq = 50)
servo_motor2 = PWM(Pin(5), freq = 50)

def servo_motor_1_move(angle):
    servo_motor_movement = int((angle / 180) * 6554) + 1638
    servo_motor1.duty_u16(servo_motor_movement)

def servo_motor_2_move(angle):
    servo_motor_movement = int((angle / 180) * 6554) + 1638
    servo_motor2.duty_u16(servo_motor_movement)    
