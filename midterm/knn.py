import json
import time

UTC_OFFSET_H = 0             # main.py sets this; your offset from UTC (change by hand at daylight saving)

learning = True              # False = testing mode: nothing is stored, in RAM or in flash

# ======================= DEMO / TESTING SETTING =======================
# Set this to True for your demo tomorrow so it ALWAYS prompts to charge,
# regardless of battery level or time. Set back to False after the demo!
DEMO_ALWAYS_CHARGE = False 
# ======================================================================


def set_learning(flag):
    global learning
    learning = bool(flag)
    print("KNN learning:", "ON" if learning else "OFF (testing mode)")


# ---------- shared helpers (time only) ----------

def sync_time():
    """Set the clock over NTP (needs Wi-Fi). Sets the RTC to UTC."""
    import ntptime
    ntptime.settime()


def clock_ok():
    """False until the clock has been set (an unset ESP32 clock says year 2000)."""
    return time.localtime()[0] >= 2024


def now_features():
    t = time.localtime(time.time() + UTC_OFFSET_H * 3600)
    return (t[3] + t[4] / 60, t[6])          # (hour 0-24, weekday 0=Mon)


def _circ(a, b, period):
    d = abs(a - b)
    return min(d, period - d)


# ---------- one model per device ----------

class ChargeKNN:
    """Samples are [hour, weekday, battery, label]. label 1 = needed to charge, 0 = didn't."""

    def __init__(self, name, k=5, weekday_weight=0.5, battery_weight=2.0,
                 max_samples=300, save_every=5, threshold_rules=None, seed_fade=60):
        self.name = name
        self.data_file = name + "_data.json"
        self.k = k
        self.weekday_weight = weekday_weight
        self.battery_weight = battery_weight
        self.max_samples = max_samples
        self.save_every = save_every
        self.threshold_rules = threshold_rules or {}   # hour -> base threshold %
        self.seed_fade = seed_fade          # starter data is dropped after this many real samples
        self.seed_samples = []
        self.charging = False               # True = pause "didn't need to charge" logging
        self._unsaved = 0
        self.samples = self._load()

    # ----- storage -----

    def _load(self):
        try:
            with open(self.data_file) as f:
                return json.load(f)
        except (OSError, ValueError):
            return []

    def save(self):
        with open(self.data_file, "w") as f:
            json.dump(self.samples, f)
        self._unsaved = 0

    def _add(self, hour, weekday, battery, label, force_save=False):
        if not learning:
            return
        self.samples.append([hour, weekday, battery, label])
        if len(self.samples) > self.max_samples:
            self.samples = self.samples[-self.max_samples:]
        self._unsaved += 1
        if force_save or self._unsaved >= self.save_every:
            self.save()

    # ----- starter data (memory-optimized for ESP32) -----

    def seed(self):
        """Rule-of-thumb starter data with weekend +5% boost, optimized to fit ESP32 RAM."""
        self.seed_samples = []
        if len(self.samples) >= self.seed_fade:
            return
        
        # Step by 3 hours to keep sample count low and avoid MemoryError on ESP32
        for day in range(7):
            is_weekend = day >= 5  # Saturday = 5, Sunday = 6
            weekend_boost = 5 if is_weekend else 0

            for hour in range(0, 24, 3):
                base_thr = 25  # default fallback
                for h_start in sorted(self.threshold_rules.keys()):
                    if hour >= h_start:
                        base_thr = self.threshold_rules[h_start]

                limit = base_thr + weekend_boost

                for battery in [15, 35, 55, 75, 95]:
                    label = 1 if battery <= limit else 0
                    self.seed_samples.append([float(hour), day, battery, label])

        print("[{}] starter data: {} samples generated".format(self.name, len(self.seed_samples)))

    def _data(self):
        """Samples used for predictions: starter data + real data, until real data takes over."""
        if self.seed_samples and len(self.samples) >= self.seed_fade:
            self.seed_samples = []
        if self.seed_samples:
            return self.seed_samples + self.samples
        return self.samples

    # ----- logging -----

    def set_charging(self, state):
        self.charging = state

    def log_reading(self, battery):
        """Regular battery update while not asking/charging -> 'didn't need to charge'."""
        if self.charging or not learning:
            return
        hour, weekday = now_features()
        self._add(hour, weekday, battery, 0)
        print("[{}] reading {:.2f}h day {} {}% -> ok".format(self.name, hour, weekday, battery))

    def log_charge_event(self, battery):
        """Charger plugged in without being asked -> 'needed to charge'."""
        if not learning:
            return
        hour, weekday = now_features()
        self._add(hour, weekday, battery, 1, force_save=True)
        print("[{}] plugged in {:.2f}h day {} {}% -> charge".format(self.name, hour, weekday, battery))

    def log_answer(self, battery, label):
        """Joystick answer to the charger question: 1 = yes, I needed it; 0 = no."""
        if not learning:
            return
        hour, weekday = now_features()
        self._add(hour, weekday, battery, label, force_save=True)
        print("[{}] answer {:.2f}h day {} {}% -> {}".format(
            self.name, hour, weekday, battery, "charge" if label else "ok"))

    # ----- KNN -----

    def distance(self, p, q):
        dh = _circ(p[0], q[0], 24) / 12
        dd = _circ(p[1], q[1], 7) / 3.5
        db = (p[2] - q[2]) / 100
        return dh * dh + self.weekday_weight * dd * dd + self.battery_weight * db * db

    def predict(self, point, samples=None, k=None):
        """point = (hour, weekday, battery). Returns (label, confidence)."""
        if samples is None:
            samples = self._data()
        if k is None:
            k = self.k
        if not samples:
            return None, 0

        n_pos = sum(1 for s in samples if s[3] == 1)
        n_neg = len(samples) - n_pos
        if n_pos == 0:
            return 0, 1.0
        if n_neg == 0:
            return 1, 1.0

        w = {1: 1 / n_pos, 0: 1 / n_neg}      # balance rare charges against common readings
        k = min(k, len(samples))
        nb = sorted(samples, key=lambda s: self.distance((s[0], s[1], s[2]), point))[:k]
        score = {0: 0.0, 1: 0.0}
        for s in nb:
            score[s[3]] += w[s[3]]
        label = 1 if score[1] > score[0] else 0
        return label, score[label] / (score[0] + score[1])

    def should_charge(self, battery):
        # Demo override: if enabled, always force a charge prompt regardless of model/time/battery
        if DEMO_ALWAYS_CHARGE:
            return 1, 1.0
        
        hour, weekday = now_features()
        return self.predict((hour, weekday, battery))

    def learned_threshold(self, hour, weekday, step=5):
        """Battery % below which this model says 'charge' at the given time."""
        thr = None
        for b in range(0, 101, step):
            label, _ = self.predict((hour, weekday, b))
            if label == 1:
                thr = b
            else:
                break
        return thr

    def print_curve(self, weekday):
        for hour in range(6, 24, 2):
            print("[{}] {:02d}:00 charge below {}%".format(
                self.name, hour, self.learned_threshold(hour, weekday)))

    # ----- testing -----

    def evaluate(self, k=None, test_every=4):
        k = k or self.k
        train = [s for i, s in enumerate(self.samples) if i % test_every != 0]
        test = [s for i, s in enumerate(self.samples) if i % test_every == 0]
        if not train or not test:
            print("[{}] not enough real data yet".format(self.name))
            return None

        tp = tn = fp = fn = 0
        for hour, weekday, battery, actual in test:
            guess, _ = self.predict((hour, weekday, battery), samples=train, k=k)
            if guess == 1 and actual == 1:
                tp += 1
            elif guess == 0 and actual == 0:
                tn += 1
            elif guess == 1:
                fp += 1
            else:
                fn += 1

        acc = (tp + tn) / len(test)
        print("[{}] train {} / test {} / k={}".format(self.name, len(train), len(test), k))
        print("  caught {}  missed {}  false alarms {}  correct oks {}".format(tp, fn, fp, tn))
        print("  accuracy {:.0f}%".format(acc * 100))
        return acc


# ---------- Custom Rules based on your schedule ----------

iphone_rules = {
    0: 25,
    6: 75,
    9: 75,
    10: 70,
    11: 65,
    12: 50,
    13: 50,
    14: 45,
    18: 40,
    20: 30,
    23: 25
}

ipad_rules = {
    0: 20,
    6: 75,
    12: 50,
    15: 30
}

# iPhone model
iphone_model = ChargeKNN("iphone", k=5, weekday_weight=0.5, battery_weight=2.0,
                         threshold_rules=iphone_rules)

# iPad model
ipad_model = ChargeKNN("ipad", k=3, weekday_weight=1.0, battery_weight=1.5,
                       threshold_rules=ipad_rules)

models = {"iphone": iphone_model, "ipad": ipad_model}


def seed_all():
    for m in models.values():
        m.seed()
