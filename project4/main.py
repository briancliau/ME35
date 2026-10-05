import servo_motor
import dc_motor
import time
from time import ticks_ms, ticks_diff
from machine import Pin, PWM
from machine import Pin, SoftI2C

button1 = Pin(34, Pin.IN, Pin.PULL_UP) 
button2 = Pin(35, Pin.IN, Pin.PULL_UP)
motor1_stage       = 0
motor2_stage       = 0
motor1_first       = 0
motor1_second      = 0
motor1_calibration = 0
motor2_first       = 0
motor2_second      = 0
motor2_calibration = 0

new_pos_motor1          = 0
last_pos_motor1         = 0
current_angle_motor1    = 0
angle_step_motor1       = 0
delta_ticks_motor1      = 0
last_angle_motor1       = 0
calibration_flag_motor1 = False

new_pos_motor2          = 0
last_pos_motor2         = 0
current_angle_motor2    = 0
angle_step_motor2       = 0
delta_ticks_motor2      = 0
last_angle_motor2       = 0
calibration_flag_motor2 = False

DEBOUNCE_MS = 200
last_press_1 = 0
last_press_2 = 0

def left_wheel_initialization(pin):
    global last_press_1
    global motor1_stage
    global motor1_first
    global motor1_second
    global motor1_calibration
    global calibration_flag_motor1
    now = ticks_ms()
    if ticks_diff(now, last_press_1) > DEBOUNCE_MS:
        if (pin.value() == 0):
            if ((motor1_stage % 2) == 0):
                motor1_first = dc_motor.Motor1.pos()
                motor1_stage += 1
                calibration_flag_motor1 = False
            elif ((motor1_stage % 2) == 1):
                motor1_second = dc_motor.Motor1.pos()
                motor1_stage += 1
                calibration_flag_motor1 = True
            motor1_calibration = motor1_second - motor1_first
            print(f"Motor 1 calibrationed 180 degrees {motor1_calibration}")

def right_wheel_initialization(pin):
    global last_press_2
    global motor2_stage
    global motor2_first
    global motor2_second
    global motor2_calibration
    global calibration_flag_motor2
    now = ticks_ms()
    if ticks_diff(now, last_press_2) > DEBOUNCE_MS:
        if (pin.value() == 0):
            if ((motor2_stage % 2) == 0):
                motor2_first = dc_motor.Motor2.pos()
                motor2_stage += 1
                calibration_flag_motor2 = False
            elif ((motor2_stage % 2) == 1):
                motor2_second = dc_motor.Motor2.pos()
                motor2_stage += 1
                calibration_flag_motor2 = True
            motor2_calibration = motor2_second - motor2_first
            print(f"Motor 2 calibrationed 180 degrees {motor2_calibration}")
            
button1.irq(trigger=Pin.IRQ_FALLING, handler=left_wheel_initialization)
button2.irq(trigger=Pin.IRQ_FALLING, handler=right_wheel_initialization)

while True:
    new_pos_motor1  = dc_motor.Motor1.pos()
    new_pos_motor2  = dc_motor.Motor2.pos()
    
    #print("new cycle")
    #print(f"New position: {dc_motor.Motor1.pos()}")
    #print(f"Old position: {last_pos_motor1}")
    #print(f"Motor 1 calibration flag: {calibration_flag_motor1}")
    #print(f"New position: {dc_motor.Motor2.pos()}")
    #print(f"Old position: {last_pos_motor2}")
    #print(f"Motor 2 calibration flag: {calibration_flag_motor2}")
    
    if last_pos_motor1 != new_pos_motor1 and calibration_flag_motor1:
        delta_ticks_motor1 = new_pos_motor1 - last_pos_motor1
        angle_step_motor1 = delta_ticks_motor1 / (motor1_calibration / 180)
        current_angle_motor1 += angle_step_motor1
        current_angle_motor1 = max(0.0, min(180.0, current_angle_motor1 + angle_step_motor1))
        servo_motor.servo_motor_1_move(int(current_angle_motor1))    
        last_pos_motor1 = new_pos_motor1
        print(current_angle_motor1)
        
    if last_pos_motor2 != new_pos_motor2 and calibration_flag_motor2:
        delta_ticks_motor2 = new_pos_motor2 - last_pos_motor2
        angle_step_motor2 = delta_ticks_motor2 / (motor2_calibration / 180)
        current_angle_motor2 += angle_step_motor2
        current_angle_motor2 = max(0.0, min(180.0, current_angle_motor2 + angle_step_motor2))
        servo_motor.servo_motor_2_move(int(current_angle_motor2))    
        last_pos_motor2 = new_pos_motor2
        
    #time.sleep_ms(500)
    