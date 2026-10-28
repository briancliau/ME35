"""test_charger.py - proves the charger reminder works on the real hardware.

HOW TO RUN
  1. Stop main.py first (Stop / Ctrl+C in Thonny) so two programs don't fight over the pins.
  2. Open this file in Thonny and press Run.
  3. Follow the WATCH and DO lines it prints.

No Wi-Fi needed: it fakes the clock (4 pm on a Wednesday) and feeds a low-battery reading
straight in. KNN learning is switched off, so nothing is saved.

What it proves
  - the KNN says "charge" for a low battery and "ok" for a healthy one
  - the arm really moves out (checked with the encoder counts) and the indicator LED lights
  - the eyes go green -> orange -> red, with sounds, if you don't answer
  - joystick YES leaves the charger out, joystick NO rolls it back in
"""
import uasyncio as asyncio
from time import ticks_ms, ticks_diff

import knn
import joystick
import dc_motor
import buzzer
import expressions
import LED
import main

# ---------------- test settings ----------------
REAL_TIMES = False        # False: annoyed after 10 s, mad after 20 s. True: the real 60 s / 300 s
TEST_ANNOYED_S = 10
TEST_MAD_S = 20
ANSWER_TIMEOUT_S = 60     # how long you get to use the joystick
RUN_HARDWARE_SMOKE_TEST = True

results = []


def check(name, ok, note=""):
    results.append((name, ok))
    print("{}  {}  {}".format("PASS" if ok else "FAIL", name, note))


def arm_pos():
    return dc_motor.Motor1.enc.value()


async def wait_for(condition, timeout_s):
    """Keep the reminder running until condition() is true.
    Returns seconds since the question was asked, or None on timeout."""
    r = main.reminder
    start = ticks_ms()
    while ticks_diff(ticks_ms(), start) < timeout_s * 1000:
        await r.tick()
        if condition():
            return ticks_diff(ticks_ms(), r.asked_at) / 1000
        await asyncio.sleep_ms(100)
    return None


# ---------------- 1. hardware smoke test ----------------

async def test_hardware():
    print("\n== 1. HARDWARE SMOKE TEST ==")
    print("WATCH: eyes green, orange, red (each with its sound), then both indicator LEDs blink")
    for mood, seconds in (("happy", 1.5), ("annoyed", 1.5), ("mad", 2.5)):
        expressions.express(mood)
        await asyncio.sleep(seconds)
    expressions.clear()
    for device in ("iphone", "ipad"):
        LED.indicator(device, True)
        await asyncio.sleep(1)
        LED.indicator(device, False)

    print("WATCH: the arm goes OUT, then back IN")
    p0 = arm_pos()
    await dc_motor.charger_out()
    p1 = arm_pos()
    await dc_motor.charger_in()
    p2 = arm_pos()
    print("encoder: start {}  out {}  back {}".format(p0, p1, p2))
    check("Motor: encoder counted while going out", p1 != p0)
    check("Motor: encoder counted while coming back", p2 != p1)


# ---------------- 2. KNN decision ----------------

def test_knn():
    print("\n== 2. KNN DECISION ==")
    phone = knn.iphone_model
    knn.now_features = lambda: (16.0, 2)
    label, _ = phone.should_charge(40)
    check("KNN: 40% at 4 pm -> charge", label == 1)
    label, _ = phone.should_charge(90)
    check("KNN: 90% at 4 pm -> ok", label == 0)
    knn.now_features = lambda: (20.0, 2)
    label, _ = phone.should_charge(60)
    check("KNN: 60% at 8 pm -> ok", label == 0)
    knn.now_features = lambda: (16.0, 2)


# ---------------- 3. charger out, escalation, YES ----------------

async def test_out_escalate_yes():
    print("\n== 3. CHARGER OUT -> ANNOYED -> MAD -> YES ==")
    r = main.reminder
    plays = []                                # remember every sound that gets played
    real_play = buzzer.play

    def counting_play(name):
        plays.append(name)
        real_play(name)
    buzzer.play = counting_play
    p0 = arm_pos()
    await r.on_reading("iphone", 10)          # a low reading, as if it came from the phone
    p1 = arm_pos()

    check("Low battery starts a request", r.state == "waiting")
    check("Arm pushed out (motor flag)", dc_motor.charger_extended)
    check("Encoder shows the arm moved", p1 != p0, "({} -> {})".format(p0, p1))
    print("WATCH: iPhone indicator ON, eyes GREEN, happy chirp.")
    print("DO: do NOT touch the joystick yet.")

    t = await wait_for(lambda: r.stage >= 1, main.ANNOYED_AFTER_S + 5)
    check("Annoyed after {} s".format(main.ANNOYED_AFTER_S),
          t is not None and abs(t - main.ANNOYED_AFTER_S) <= 2,
          "({})".format("{:.1f} s".format(t) if t is not None else "never"))
    print("WATCH: eyes ORANGE and the annoyed sound.")

    t = await wait_for(lambda: r.stage >= 2, main.MAD_AFTER_S + 5)
    check("Mad after {} s".format(main.MAD_AFTER_S),
          t is not None and abs(t - main.MAD_AFTER_S) <= 2,
          "({})".format("{:.1f} s".format(t) if t is not None else "never"))
    print("WATCH: eyes RED and the mad growls.")

    # still no answer: the mad sound should repeat every MAD_REPEAT_S seconds
    n0 = plays.count("mad")
    print("DO: keep waiting {} s and listen: the mad growl should repeat every {} s.".format(
        2 * main.MAD_REPEAT_S + 1, main.MAD_REPEAT_S))
    await wait_for(lambda: False, 2 * main.MAD_REPEAT_S + 1)
    repeats = plays.count("mad") - n0
    check("Mad sound repeats every {} s".format(main.MAD_REPEAT_S), repeats >= 2,
          "({} repeats in {} s)".format(repeats, 2 * main.MAD_REPEAT_S + 1))

    print("DO: answer YES now - move the stick LEFT and RIGHT, then press the button.")
    t = await wait_for(lambda: r.state == "charging", ANSWER_TIMEOUT_S)
    check("Joystick YES -> charger stays out", t is not None and dc_motor.charger_extended)
    pa = arm_pos()
    await asyncio.sleep(2)
    check("Arm did not move after YES", abs(arm_pos() - pa) <= 2)
    print("WATCH: green eyes for a moment, then eyes off; indicator LED still ON.")

    print("Simulating the phone reaching 96% ...")
    await r.on_reading("iphone", 96)
    check("Fully charged -> arm rolled back in", r.state == "idle" and not dc_motor.charger_extended)
    print("WATCH: the iPhone indicator LED should be OFF again.")
    print("encoder: start {}  out {}  now {}".format(p0, p1, arm_pos()))


# ---------------- 4. charger out, NO ----------------

async def test_no():
    print("\n== 4. CHARGER OUT -> NO ==")
    r = main.reminder
    await r.force("iphone")                   # skip the KNN and ask right now
    check("Request started", r.state == "waiting" and dc_motor.charger_extended)
    print("DO: answer NO now - move the stick UP and DOWN, then press the button.")
    t = await wait_for(lambda: r.state == "idle", ANSWER_TIMEOUT_S)
    check("Joystick NO -> charger rolled back in", t is not None and not dc_motor.charger_extended)


# ---------------- run everything ----------------

async def cleanup():
    expressions.clear()
    LED.indicator("iphone", False)
    LED.indicator("ipad", False)
    await dc_motor.charger_in()


def summary():
    passed = sum(1 for _, ok in results if ok)
    print("\n==== {} of {} checks passed ====".format(passed, len(results)))
    for name, ok in results:
        if not ok:
            print("FAILED:", name)


async def run():
    if not hasattr(main.reminder, "force") or not hasattr(main, "MAD_REPEAT_S"):
        print("main.py on the board is out of date. Re-upload main.py and server.py, then run again.")
        return
    knn.set_learning(False)                   # never write test data
    knn.clock_ok = lambda: True               # fake clock: no Wi-Fi/NTP needed
    knn.now_features = lambda: (16.0, 2)      # 4 pm, Wednesday
    if not REAL_TIMES:
        main.ANNOYED_AFTER_S = TEST_ANNOYED_S
        main.MAD_AFTER_S = TEST_MAD_S
    main.COOLDOWN_AFTER_NO_S = 1
    knn.seed_all()
    asyncio.create_task(joystick.joystick_task())

    if RUN_HARDWARE_SMOKE_TEST:
        await test_hardware()
    test_knn()
    await test_out_escalate_yes()
    await test_no()
    await cleanup()
    summary()


if __name__ == "__main__":
    asyncio.run(run())