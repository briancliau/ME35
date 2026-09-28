from machine import Pin, PWM
from machine import Pin, SoftI2C
import time
import math
from time import ticks_ms, ticks_diff
import sevenseg
import motor

# Cannot use 34, 35 (buttons), 21, 22 (I2C), 4, 5 (Servo Motors)

button_Play = Pin(34, Pin.IN, Pin.PULL_UP)
button_Train = Pin(35, Pin.IN, Pin.PULL_UP)

i2c = SoftI2C(scl = Pin(22), sda = Pin(21))

print(i2c.scan())

DEBOUNCE_MS = 200
last_press = 0

pressed_flag = False
STATE_PLAY = False
STATE_TRAIN = True

def playButton(p):
    global STATE_PLAY
    global STATE_TRAIN
    STATE_PLAY = True
    STATE_TRAIN = False


def trainButton(p):
    global pressed_flag
    global STATE_TRAIN
    STATE_TRAIN = True
    pressed_flag = True

    
button_Train.irq(trigger=Pin.IRQ_RISING, handler=trainButton)
button_Play.irq(trigger=Pin.IRQ_RISING, handler=playButton)

import veml6040
sensor = veml6040.VEML6040(i2c)

sensor.trigger_measurement()
sevenseg.start()
   
def k_nearest_neighbor(x,y,z, k =1):
    distances = []
    for index, d in enumerate(data):
        dist = math.sqrt((x-d[0])**2+(y-d[1])**2+(z-d[2])**2)
        distances.append([dist,d[3]])
    
    distances.sort()
    distances = distances[:k] #get k distances
    classes = []
    for dist in distances:
        classes.append(dist[1])
    print("k classes", classes)
    most_number_of_closest_classes = max(set(classes), key = classes.count)
    print("max classes ", most_number_of_closest_classes)
    
    return most_number_of_closest_classes


       
data = []
color = ""
index = 0

while True:
    red, green, blue, white = sensor.read_rgbw()
    if(STATE_TRAIN and pressed_flag):
        print(red, green, blue, white)
        index = index+1
        if index <= 11:
            color = "red"
        elif index >12 and index<22:
            color = "black"
        else:
            color = "unrecognized"

        data.append((red, green, blue, color))
        pressed_flag = False
           
    if(STATE_PLAY):
        i = 0
        sorted_flag = False
        while i < 10 and sorted_flag == False:
            what_class1 = k_nearest_neighbor(red, green, blue,3)
            what_class2 = k_nearest_neighbor(red, green, blue,3)
            what_class3 = k_nearest_neighbor(red, green, blue,3)
            print(what_class1)
            print(what_class2)
            print(what_class3)
            if (what_class1 == what_class2 == what_class3):
                sorted_flag = True
            else:
                sorted_flag = False
            i = i + 1
        print(what_class1)
        
        if what_class1 == "red":
            motor.put_in_1()
            sevenseg.add_lego()
        elif what_class1 == "black":
            motor.put_in_2()
            sevenseg.add_lego()
        else:
            motor.put_in_middle()     
        time.sleep(1.0)
        STATE_PLAY = False
        motor.put_in_middle()
        
    time.sleep(0.1)
