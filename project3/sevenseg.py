from machine import Pin, Timer
import time

digit1 = Pin(32, Pin.OUT)
digit2 = Pin(15, Pin.OUT)

A = Pin( 2, Pin.OUT)
B = Pin(12, Pin.OUT)
C = Pin(13, Pin.OUT)
D = Pin(14, Pin.OUT)
E = Pin(16, Pin.OUT)
F = Pin(17, Pin.OUT)
G = Pin(19, Pin.OUT)

digit_flag = 0
display_timer = Timer(0)

lego_count = 0

def refresh_display(timer_obj):
    global digit_flag
    global lego_count
    
    d1 = lego_count % 10
    d2 = lego_count // 10
    
    if digit_flag == 0:
        digit1.value(1)
        digit2.value(0)
        display_num(d1)
        digit_flag = 1
    else:
        digit1.value(0)
        digit2.value(1)
        display_num(d2)
        digit_flag = 0
        
def start():
    display_timer.init(period=5, mode=Timer.PERIODIC, callback=refresh_display)
        
def add_lego():
    global lego_count
    lego_count = lego_count + 1
    
def display_num(x):
    if x == 0:
        A.value(0)
        B.value(0)
        C.value(0)
        D.value(0)
        E.value(0)
        F.value(0)
        G.value(1)
    elif x == 1:
        A.value(1)
        B.value(0)
        C.value(0)
        D.value(1)
        E.value(1)
        F.value(1)
        G.value(1)
    elif x == 2:
        A.value(0)
        B.value(0)
        C.value(1)
        D.value(0)
        E.value(0)
        F.value(1)
        G.value(0)
    elif x == 3:
        A.value(0)
        B.value(0)
        C.value(0)
        D.value(0)
        E.value(1)
        F.value(1)
        G.value(0)
    elif x == 4:
        A.value(1)
        B.value(0)
        C.value(0)
        D.value(1)
        E.value(1)
        F.value(0)
        G.value(0)
    elif x == 5:
        A.value(0)
        B.value(1)
        C.value(0)
        D.value(0)
        E.value(1)
        F.value(0)
        G.value(0)
    elif x == 6:
        A.value(0)
        B.value(1)
        C.value(0)
        D.value(0)
        E.value(0)
        F.value(0)
        G.value(0)
    elif x == 7:
        A.value(0)
        B.value(0)
        C.value(0)
        D.value(1)
        E.value(1)
        F.value(1)
        G.value(1)
    elif x == 8:
        A.value(0)
        B.value(0)
        C.value(0)
        D.value(0)
        E.value(0)
        F.value(0)
        G.value(0)
    elif x == 9:
        A.value(0)
        B.value(0)
        C.value(0)
        D.value(0)
        E.value(1)
        F.value(0)
        G.value(0)
    else:
        A.value(1)
        B.value(1)
        C.value(1)
        D.value(1)
        E.value(1)
        F.value(1)
        G.value(1)
