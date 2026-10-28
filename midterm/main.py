import time
import uasyncio as asyncio
from time import ticks_ms, ticks_diff, ticks_add

import server
import knn
import joystick
import expressions
import buzzer
import LED

# ======================= SETTINGS =======================
LEARNING = True             # True = real use (KNN learns). False = testing (KNN stores nothing).
UTC_OFFSET_H = 0            # your offset from UTC; change it by hand at daylight saving

ANNOYED_AFTER_S = 60        # no answer after 1 minute  -> annoyed (orange eyes)
MAD_AFTER_S = 300           # no answer after 5 minutes -> mad (red eyes)
MAD_REPEAT_S = 5            # once mad, repeat the mad sound this often until you answer
PROMPT_TIMEOUT_S = 600      # auto-cancel prompt and return to idle after 10 minutes of no answer
MIN_CONFIDENCE = 0.6        # how sure the KNN must be before it prompts
COOLDOWN_AFTER_NO_S = 3600  # after you answer "no", don't ask about that device again for this long
ACK_EYES_S = 3              # eyes duration after you answer
FOCUS_EYES_S = 5            # eyes for focus-reminder events
# ========================================================


def ensure_clock():
    """The KNN needs the real time. Try NTP if the clock hasn't been set."""
    if knn.clock_ok():
        return True
    for _ in range(2):
        try:
            knn.sync_time()
            break
        except Exception as e:
            print("NTP failed:", e)
    return knn.clock_ok()


# ---------------- part 1: charger reminder ----------------

class ChargeReminder:
    """Reminder system without DC motor."""

    def __init__(self):
        self.state = "idle"
        self.device = None                  # who the reminder is out for
        self.level = 0                      # battery % when we asked
        self.asked_at = 0
        self.stage = 0                      # 0 patient, 1 annoyed, 2 mad
        self.mad_last = 0                   # when the mad sound last played
        self.cooldown_until = {"iphone": None, "ipad": None}

    def _cooling(self, device):
        until = self.cooldown_until[device]
        return until is not None and ticks_diff(until, ticks_ms()) > 0

    async def on_reading(self, device, level):
        """Decide whether to prompt the user based on KNN."""
        if level < 0:
            return
        if self.state != "idle":
            return                    # busy waiting for an answer
        if self._cooling(device):
            return
        if not ensure_clock():
            print("Clock not set, skipping KNN decision")
            return

        label, conf = knn.models[device].should_charge(level)
        print("[{}] {}% -> KNN says {} ({}% sure)".format(
            device, level, "CHARGE" if label == 1 else "ok", int(conf * 100)))
        
        if label == 1 and conf >= MIN_CONFIDENCE:
            await self.start(device, level)
        else:
            knn.models[device].log_reading(level)

    async def start(self, device, level):
        self.state = "waiting"
        self.device = device
        self.level = level
        self.asked_at = ticks_ms()
        self.stage = 0
        self.mad_last = 0
        joystick.reset()                        # forget stray gestures
        LED.indicator(device, True)
        expressions.happy()                     # green eyes + chirp: "charge me?"
        buzzer.play("happy")
        print("[{}] prompting user to charge (battery at {}%)".format(device, level))

    async def tick(self):
        """Call often: reads the joystick, escalates states, and auto-timeouts if ignored."""
        if self.state != "waiting":
            return
        
        answer = joystick.take_answer()
        if answer is not None:
            await self.answer(answer)
            return

        waited = ticks_diff(ticks_ms(), self.asked_at) // 1000

        # Auto-timeout: if ignored for too long, reset to idle so the bot doesn't lock up permanently
        if waited >= PROMPT_TIMEOUT_S:
            print("[{}] prompt ignored for too long, timing out back to idle".format(self.device))
            expressions.clear()
            LED.indicator(self.device, False)
            self.state = "idle"
            self.device = None
            return

        if self.stage < 2 and waited >= MAD_AFTER_S:
            self.stage = 2
            self.mad_last = ticks_ms()
            expressions.mad()
            buzzer.play("mad")
        elif self.stage < 1 and waited >= ANNOYED_AFTER_S:
            self.stage = 1
            expressions.annoyed()
            buzzer.play("annoyed")
        elif self.stage == 2 and ticks_diff(ticks_ms(), self.mad_last) >= MAD_REPEAT_S * 1000:
            self.mad_last = ticks_ms()
            buzzer.play("mad")                  # still no answer: growl again

    async def answer(self, answer):
        device, level = self.device, self.level
        model = knn.models[device]
        expressions.clear()
        LED.indicator(device, False)

        if answer == "yes":
            expressions.happy(hold_s=ACK_EYES_S)    # "thanks, got it"
            buzzer.play("happy")
            model.log_answer(level, 1)
            print("[{}] yes: logged charge need".format(device))
        else:
            # Wrong KNN prediction -> sad eyes & sound
            if hasattr(expressions, "eyes_sad"):
                expressions.eyes_sad(hold_s=ACK_EYES_S)
            else:
                expressions.sad(hold_s=ACK_EYES_S)
            buzzer.play("sad")
            
            model.log_answer(level, 0)
            self.cooldown_until[device] = ticks_add(ticks_ms(), COOLDOWN_AFTER_NO_S * 1000)
            print("[{}] no: wrong KNN prediction, logged ok and cooling down".format(device))

        self.state = "idle"
        self.device = None

    async def force(self, device):
        """Test helper: skip the KNN and prompt right now."""
        if self.state != "idle":
            print("Busy ({}), ignoring /ask".format(self.state))
            return
        level = server.iphone_battery if device == "iphone" else server.ipad_battery
        await self.start(device, level if level >= 0 else 30)


reminder = ChargeReminder()
inbox = []                                      # events from the server, handled by main()


def on_battery(device, level):
    inbox.append(("battery", device, level))


def on_ask(device):
    inbox.append(("ask", device))


def on_answer(value):
    joystick.confirmed_action = value           # same thing the joystick button sets


# ---------------- part 2: focus reminder ----------------

def on_focus_event(event, result):
    if result == "good":
        expressions.happy(hold_s=FOCUS_EYES_S)
        buzzer.play("happy")
    elif event == "1":
        expressions.annoyed(hold_s=FOCUS_EYES_S)
        buzzer.play("annoyed")
    else:
        expressions.mad(hold_s=FOCUS_EYES_S)
        buzzer.play("mad")


# ---------------- server hooks ----------------

def status():
    return ("iphone={}% ipad={}% | reminder: {} {} | learning={}".format(
        server.iphone_battery, server.ipad_battery, reminder.state, reminder.device or "-",
        "on" if knn.learning else "off"))


async def main():
    knn.UTC_OFFSET_H = UTC_OFFSET_H
    knn.set_learning(LEARNING)

    # Hook up server callbacks properly
    server.on_battery = on_battery
    server.on_event = on_focus_event
    server.get_status = status
    server.on_ask = on_ask
    server.on_answer = on_answer

    server.connect_wifi()
    ensure_clock()
    knn.seed_all()

    asyncio.create_task(joystick.joystick_task())
    await server.start()

    while True:
        while inbox:
            item = inbox.pop(0)
            if item[0] == "battery":
                _, device, level = item
                if reminder.state == "idle":
                    await reminder.on_reading(device, level)
            elif item[0] == "ask":
                await reminder.force(item[1])

        await reminder.tick()
        await asyncio.sleep_ms(100)


if __name__ == "__main__":
    asyncio.run(main())