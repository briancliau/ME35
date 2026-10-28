from machine import Pin, PWM

# ---------- RGB eyes (common-anode: duty 0 = fully on) ----------
red1 = PWM(Pin(5))
green1 = PWM(Pin(18))
blue1 = PWM(Pin(19))
red1.freq(50)
green1.freq(50)
blue1.freq(50)

red2 = PWM(Pin(13))
green2 = PWM(Pin(25))
blue2 = PWM(Pin(26))
red2.freq(50)
green2.freq(50)
blue2.freq(50)


def set_rgb(r, g, b):
    red1.duty_u16(int(((255-r) / 255) * 65535))
    green1.duty_u16(int(((255-g) / 255) * 65535))
    blue1.duty_u16(int(((255-b) / 255) * 65535))
    red2.duty_u16(int(((255-r) / 255) * 65535))
    green2.duty_u16(int(((255-g) / 255) * 65535))
    blue2.duty_u16(int(((255-b) / 255) * 65535))


# ---------- eye colours ----------
def eyes_off():
    set_rgb(64, 64, 64)

def eyes_happy():
    set_rgb(0, 255, 0)          # green

def eyes_annoyed():
    set_rgb(255, 120, 0)        # yellowish orange (raise the middle number for more yellow)

def eyes_mad():
    set_rgb(255, 0, 0)          # red
    
def eyes_sad():
    set_rgb(0, 0, 255)


# ---------- device indicator LEDs (which device the charger is out for) ----------
iPhone = Pin(2, Pin.OUT)
iPad   = Pin(12, Pin.OUT)

def iPhone_charge():
    iPhone.value(1)

def iPhone_no_charge():
    iPhone.value(0)

def iPad_charge():
    iPad.value(1)

def iPad_no_charge():
    iPad.value(0)

iPad__no_charge = iPad_no_charge      # old (misspelled) name, kept so nothing breaks


def indicator(device, on):
    """device is 'iphone' or 'ipad'."""
    pin = iPhone if device == "iphone" else iPad
    pin.value(1 if on else 0)


# Common-anode LEDs light up at duty 0, so switch the eyes off explicitly at start-up.
eyes_off()

