from machine import ADC, Pin
import uasyncio as asyncio
from time import ticks_ms, ticks_diff

x_axis = ADC(Pin(36))
y_axis = ADC(Pin(39))
x_axis.atten(ADC.ATTN_11DB)
y_axis.atten(ADC.ATTN_11DB)

LOW = 20000
HIGH = 40000
PRESS = 65000        # x at max = button pressed
WINDOW_MS = 1500     # low and high must both happen within this time
POLL_MS = 20

last_action = None        # "yes" or "no", set by the gestures
confirmed_action = None   # set when the button confirms last_action


def reset():
    """Forget any half-finished gesture or old answer (call when a new question starts)."""
    global last_action, confirmed_action
    last_action = None
    confirmed_action = None


def take_answer():
    """Return 'yes', 'no' or None, and clear it so it is only read once."""
    global confirmed_action
    answer = confirmed_action
    confirmed_action = None
    return answer


class Sweep:
    """Detects an axis going low AND high within WINDOW_MS."""

    def __init__(self):
        self.seen_low = False
        self.seen_high = False
        self.start = 0
        self.locked = False   # after a trigger, wait until the stick is back at center

    def reset(self):
        self.seen_low = False
        self.seen_high = False

    def update(self, value, now):
        if value < LOW:
            zone = -1
        elif value > HIGH:
            zone = 1
        else:
            zone = 0

        if self.locked:
            if zone == 0:
                self.locked = False
            return False

        # window expired without completing both sides
        if (self.seen_low or self.seen_high) and ticks_diff(now, self.start) > WINDOW_MS:
            self.reset()

        if zone != 0:
            if not (self.seen_low or self.seen_high):
                self.start = now
            if zone == -1:
                self.seen_low = True
            else:
                self.seen_high = True

        if self.seen_low and self.seen_high:
            self.reset()
            self.locked = True
            return True
        return False


async def joystick_task():
    global last_action, confirmed_action

    x_sweep = Sweep()
    y_sweep = Sweep()
    was_pressed = False

    while True:
        now = ticks_ms()
        x = x_axis.read_u16()
        y = y_axis.read_u16()

        pressed = x >= PRESS

        if pressed:
            # button press: ignore x for gestures so it can't count as "high"
            x_sweep.reset()
            if not was_pressed:                 # rising edge only
                if last_action is not None:
                    confirmed_action = last_action
                    print("Confirmed:", confirmed_action)
                    last_action = None          # one confirm per action
                else:
                    print("Pressed, but nothing to confirm")
        else:
            x_triggered = x_sweep.update(x, now)
            y_triggered = y_sweep.update(y, now)

            if x_triggered:
                last_action = "yes"
                y_sweep.reset()
                print("Indicated: yes")
            elif y_triggered:
                last_action = "no"
                x_sweep.reset()
                print("Indicated: no")

        was_pressed = pressed
        await asyncio.sleep_ms(POLL_MS)


# Stand-alone demo: only runs when you run joystick.py directly, not when main.py imports it.
if __name__ == "__main__":
    async def main():
        asyncio.create_task(joystick_task())
        while True:
            await asyncio.sleep(1)

    asyncio.run(main())
