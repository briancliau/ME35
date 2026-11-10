# collect_samples.py - run on the CAR ESP32 (MicroPython) to record the KNN samples.
# Needs veml6040.py on the board. Run it from Thonny (or any REPL) so you can press Enter.
# It writes KNN_FILE in the format car.py expects: [[r, g, b, w, "label"], ...]

import json
import time
from machine import Pin, I2C

import veml6040

# =====================================================================
# SETTINGS - keep the sensor settings identical to car.py
# =====================================================================
SAMPLES_FILE = "color_knn.json"   # must match KNN_FILE in car.py
LABELS = ["red", "floor"]         # the red label must match RED_LABEL in car.py
ROUNDS = 3                        # how many times each label is recorded
SAMPLES_PER_ROUND = 15            # readings taken each time
SAMPLE_DELAY_MS = 50              # keep >= SENSOR_INTEGRATION_MS so every reading is fresh
APPEND_TO_EXISTING = False        # True = keep samples already in the file and add to them

WAIT_FOR_ENTER = True             # True = wait for Enter at each step; False = use countdown
COUNTDOWN_S = 5                   # seconds before each recording when WAIT_FOR_ENTER is False

I2C_ID = 0
I2C_SDA_PIN = 21
I2C_SCL_PIN = 22
I2C_FREQ_HZ = 100000
SENSOR_INTEGRATION_MS = 40        # 40, 80, 160, 320, 640 or 1280
# =====================================================================

_IT_CONSTANTS = {
    40: veml6040.IT_40MS,
    80: veml6040.IT_80MS,
    160: veml6040.IT_160MS,
    320: veml6040.IT_320MS,
    640: veml6040.IT_640MS,
    1280: veml6040.IT_1280MS,
}


def wait_for_user(message):
    if WAIT_FOR_ENTER:
        input(message + "  [press Enter] ")
    else:
        print(message)
        for s in range(COUNTDOWN_S, 0, -1):
            print("  starting in", s)
            time.sleep(1)


def load_existing():
    try:
        with open(SAMPLES_FILE) as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = data.get("samples", [])
        print("Loaded {} existing samples".format(len(data)))
        return [list(s) for s in data]
    except (OSError, ValueError):
        print("No existing file, starting fresh")
        return []


def save(samples):
    with open(SAMPLES_FILE, "w") as f:
        json.dump(samples, f)
    print("Saved {} samples to {}".format(len(samples), SAMPLES_FILE))


def summary(samples):
    print("\n=== SUMMARY (min..max per channel) ===")
    for label in LABELS:
        rows = [s for s in samples if s[4] == label]
        if not rows:
            continue
        parts = []
        for idx, name in enumerate(("R", "G", "B", "W")):
            vals = [s[idx] for s in rows]
            parts.append("{} {}..{}".format(name, min(vals), max(vals)))
        print("{:>8} ({} samples): {}".format(label, len(rows), "  ".join(parts)))
    print("If two labels overlap heavily on every channel, add more varied samples.")


def main():
    i2c = I2C(I2C_ID, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=I2C_FREQ_HZ)
    sensor = veml6040.VEML6040(i2c)          # driver defaults to 1280 ms...
    sensor.set_integration_time(_IT_CONSTANTS[SENSOR_INTEGRATION_MS])   # ...so set ours
    time.sleep_ms(SENSOR_INTEGRATION_MS * 3)

    samples = load_existing() if APPEND_TO_EXISTING else []

    for rnd in range(1, ROUNDS + 1):
        for label in LABELS:
            wait_for_user("\nRound {}/{}: put the sensor over '{}' "
                          "(use a slightly different spot/angle each round)".format(rnd, ROUNDS, label))
            for i in range(SAMPLES_PER_ROUND):
                r, g, b, w = sensor.read_rgbw()
                samples.append([r, g, b, w, label])
                print("  {} {}/{}: R={} G={} B={} W={}".format(
                    label, i + 1, SAMPLES_PER_ROUND, r, g, b, w))
                time.sleep_ms(SAMPLE_DELAY_MS)

    save(samples)
    summary(samples)


main()
