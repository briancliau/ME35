from machine import Pin
from machine import PWM
import uasyncio as asyncio


class Count(object):
    def __init__(self,A,B):
        self.A = Pin(A, Pin.IN)
        self.B = Pin(B, Pin.IN)
        self.counter = 0

        self.A.irq(self.cb,self.A.IRQ_FALLING|self.A.IRQ_RISING) #interrupt on line A
        self.B.irq(self.cb,self.B.IRQ_FALLING|self.B.IRQ_RISING) #interrupt on line B


    def cb(self,msg):
        other,inc = (self.B,1) if msg == self.A else (self.A,-1) #define other line and increment
        self.counter += -inc if msg.value()!=other.value() else  inc

    def value(self):
        return self.counter


class Motor(Count):
    def __init__(self,m1,m2, A, B):
        self.enc = Count(A,B)
        self.M1 = PWM(m1, freq=50, duty_u16=0)
        self.M2 = PWM(m2, freq=50, duty_u16=0)
        self.stop()

    def pos(self):
        print(self.enc.value())
        return self.enc.value()

    def stop(self):
        self.M1.duty_u16(0)
        self.M2.duty_u16(0)

    def start(self, direction = 0, speed = 50):
        if direction:
            self.M1.duty_u16(int(speed*65535/100))
            self.M2.duty_u16(0)
        else:
            self.M1.duty_u16(0)
            self.M2.duty_u16(int(speed*65535/100))


#IF you want to set up just the encoder use this
#count = Count(36,39)
#print(count.value())

#If you want to set up a motor with encoder
#Motor1 = Motor(14,27, 32,39) #first two are motor pins, last two are encoder pins
#Motor1.pos() # to read the encoder value for Motor 1
Motor1 = Motor(14,27,21,22)


# ---------- charger arm ----------
CHARGER_SPEED = 50          # motor speed in %
CHARGER_MOVE_MS = 2000      # how long the motor runs to go fully out or fully in
charger_extended = False    # assumes the charger is rolled IN when the program starts
_moving = False


async def _move(direction):
    global _moving
    _moving = True
    try:
        Motor1.start(direction, CHARGER_SPEED)
        await asyncio.sleep_ms(CHARGER_MOVE_MS)
    finally:
        Motor1.stop()           # always stop, even if the task is cancelled
        _moving = False


async def charger_out():
    global charger_extended
    while _moving:                          # wait if the arm is already moving
        await asyncio.sleep_ms(50)
    if charger_extended:
        return
    await _move(1)
    charger_extended = True


async def charger_in():
    global charger_extended
    while _moving:
        await asyncio.sleep_ms(50)
    if not charger_extended:
        return
    await _move(0)
    charger_extended = False

async def main():
    print("Test starting...")
    await charger_out()
    await asyncio.sleep(2)
    await charger_in()
    print("Test finished!")

if __name__ == "__main__":
    asyncio.run(main())
