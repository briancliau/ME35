import network
import urequests
import time
import wifi
from machine import Pin, PWM

wifi.connect_wifi()

ISS_URL = "http://api.open-notify.org/iss-now.json"
response = urequests.get(ISS_URL)
data = response.json()
response.close()

print(data)

import urequests
DATE_URL = "https://aisenseapi.com/services/v1/datetime/-0400"
reply = urequests.get(DATE_URL)
# print(reply.json()['datetime'])
string = reply.json()['datetime']
hour = string[11:13]
hour_int = int(hour)
minute = string[14:16]
minute_int = int(minute)
if (hour_int > 12):
    hour_int = hour_int - 12 
    print(hour_int)
    print(minute)
    
else:
    print(hour_int)
    print(minute_int)


pwm_h = PWM(Pin(4))
pwm_h.freq(50)
pwm_m = PWM(Pin(5))
pwm_m.freq(50)


servo_h = 1638 + ((hour_int - 1)/11)*6554
servo_h = round(servo_h)
servo_m = 1638 + ((180 - (3*minute_int))/180)*6554
servo_m = round(servo_m)
print(servo_h)
print (servo_m)
pwm_h.duty_u16(servo_h)
pwm_m.duty_u16(servo_m)




    

    

    
    
    





