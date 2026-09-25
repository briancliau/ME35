from machine import Pin, Timer

digit1 = Pin(36, Pin.OUT)
digit2 = Pin(39, Pin.OUT)

A_left  = Pin( 2, Pin.OUT)
B_left  = Pin(12, Pin.OUT)
C_left  = Pin(13, Pin.OUT)
D_left  = Pin(14, Pin.OUT)
E_left  = Pin(16, Pin.OUT)
F_left  = Pin(17, Pin.OUT)
G_left  = Pin(18, Pin.OUT)

A_right = Pin(19, Pin.OUT)
B_right = Pin(23, Pin.OUT)
C_right = Pin(25, Pin.OUT)
D_right = Pin(26, Pin.OUT)
E_right = Pin(27, Pin.OUT)
F_right = Pin(32, Pin.OUT)
G_right = Pin(33, Pin.OUT)

digit_flag = 0
display_timer = Timer(0)

left_count = 0
right_count = 0
    
def refresh_display(timer_obj):
    global digit_flag
    global left_count
    global right_count
    
    d1_left = left_count % 10
    d2_left = left_count / 10
    d1_right = right_count % 10
    d2_right = right_count / 10
    
    if digit_flag == 0:
        digit1.value(1)
        digit2.value(0)
        display_num_left(d1_left)
        display_num_right(d1_right)
        digit_flag = 1
    else:
        digit1.value(0)
        digit2.value(1)
        display_num_left(d2_left)
        display_num_right(d2_right)
        digit_flag = 0
        
def start():
    display_timer.init(period=5, mode=Timer.PERIODIC, callback=refresh_display)
        
def add_left():
    left_count = left_count + 1
    
def add_right():
    right_count = right_count + 1
    
def display_num_left(x):
    if x == 0:
        A_left.value(1)
        B_left.value(1)
        C_left.value(1)
        D_left.value(1)
        E_left.value(1)
        F_left.value(1)
        G_left.value(0)
    elif x == 1:
        A_left.value(1)
        B_left.value(1)
        C_left.value(0)
        D_left.value(0)
        E_left.value(0)
        F_left.value(0)
        G_left.value(0)
    elif x == 2:
        A_left.value(1)
        B_left.value(1)
        C_left.value(0)
        D_left.value(1)
        E_left.value(1)
        F_left.value(0)
        G_left.value(1)
    elif x == 3:
        A_left.value(1)
        B_left.value(1)
        C_left.value(1)
        D_left.value(1)
        E_left.value(0)
        F_left.value(0)
        G_left.value(1)
    elif x == 4:
        A_left.value(0)
        B_left.value(1)
        C_left.value(1)
        D_left.value(0)
        E_left.value(0)
        F_left.value(1)
        G_left.value(1)
    elif x == 5:
        A_left.value(1)
        B_left.value(0)
        C_left.value(1)
        D_left.value(1)
        E_left.value(0)
        F_left.value(1)
        G_left.value(1)
    elif x == 6:
        A_left.value(1)
        B_left.value(0)
        C_left.value(1)
        D_left.value(1)
        E_left.value(1)
        F_left.value(1)
        G_left.value(1)
    elif x == 7:
        A_left.value(1)
        B_left.value(1)
        C_left.value(1)
        D_left.value(0)
        E_left.value(0)
        F_left.value(0)
        G_left.value(0)
    elif x == 8:
        A_left.value(1)
        B_left.value(1)
        C_left.value(1)
        D_left.value(1)
        E_left.value(1)
        F_left.value(1)
        G_left.value(1)
    elif x == 9:
        A_left.value(1)
        B_left.value(1)
        C_left.value(1)
        D_left.value(1)
        E_left.value(0)
        F_left.value(1)
        G_left.value(1)
    else:
        A_left.value(0)
        B_left.value(0)
        C_left.value(0)
        D_left.value(0)
        E_left.value(0)
        F_left.value(0)
        G_left.value(0)
        
def display_num_right(x):
    if x == 0:
        A_right.value(1)
        B_right.value(1)
        C_right.value(1)
        D_right.value(1)
        E_right.value(1)
        F_right.value(1)
        G_right.value(0)
    elif x == 1:
        A_right.value(1)
        B_right.value(1)
        C_right.value(0)
        D_right.value(0)
        E_right.value(0)
        F_right.value(0)
        G_right.value(0)
    elif x == 2:
        A_right.value(1)
        B_right.value(1)
        C_right.value(0)
        D_right.value(1)
        E_right.value(1)
        F_right.value(0)
        G_right.value(1)
    elif x == 3:
        A_right.value(1)
        B_right.value(1)
        C_right.value(1)
        D_right.value(1)
        E_right.value(0)
        F_right.value(0)
        G_right.value(1)
    elif x == 4:
        A_right.value(0)
        B_right.value(1)
        C_right.value(1)
        D_right.value(0)
        E_right.value(0)
        F_right.value(1)
        G_right.value(1)
    elif x == 5:
        A_right.value(1)
        B_right.value(0)
        C_right.value(1)
        D_right.value(1)
        E_right.value(0)
        F_right.value(1)
        G_right.value(1)
    elif x == 6:
        A_right.value(1)
        B_right.value(0)
        C_right.value(1)
        D_right.value(1)
        E_right.value(1)
        F_right.value(1)
        G_right.value(1)
    elif x == 7:
        A_right.value(1)
        B_right.value(1)
        C_right.value(1)
        D_right.value(0)
        E_right.value(0)
        F_right.value(0)
        G_right.value(0)
    elif x == 8:
        A_right.value(1)
        B_right.value(1)
        C_right.value(1)
        D_right.value(1)
        E_right.value(1)
        F_right.value(1)
        G_right.value(1)
    elif x == 9:
        A_right.value(1)
        B_right.value(1)
        C_right.value(1)
        D_right.value(1)
        E_right.value(0)
        F_right.value(1)
        G_right.value(1)
    else:
        A_right.value(0)
        B_right.value(0)
        C_right.value(0)
        D_right.value(0)
        E_right.value(0)
        F_right.value(0)
        G_right.value(0)

