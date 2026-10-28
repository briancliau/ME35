"""Robot moods: eye colour + sound together.

    expressions.happy()             # green eyes + happy sound, stays until changed
    expressions.annoyed()           # yellowish-orange eyes + annoyed sound
    expressions.mad()               # red eyes + mad sound
    expressions.happy(hold_s=5)     # show for 5 seconds, then go back to the previous mood
    expressions.clear()             # eyes off
"""
import uasyncio as asyncio
import LED
import buzzer

base = None          # mood the eyes settle back to (None = eyes off)
_revert = None       # task that restores the base mood after a short expression

_EYES = {"happy": LED.eyes_happy, "annoyed": LED.eyes_annoyed, "mad": LED.eyes_mad, "sad": LED.eyes_sad}


def _apply(mood):
    if mood is None:
        LED.eyes_off()
    else:
        _EYES[mood]()


async def _revert_later(seconds):
    await asyncio.sleep(seconds)
    _apply(base)


def express(mood, hold_s=None, sound=True):
    """hold_s=None: becomes the new base mood. hold_s=N: shows for N seconds, then reverts."""
    global base, _revert
    if _revert is not None:
        _revert.cancel()
        _revert = None
    _apply(mood)
    if hold_s is None:
        base = mood
    else:
        _revert = asyncio.create_task(_revert_later(hold_s))
    if sound:
        buzzer.play(mood)


def happy(hold_s=None):
    express("happy", hold_s)


def annoyed(hold_s=None):
    express("annoyed", hold_s)


def mad(hold_s=None):
    express("mad", hold_s)

def sad(hold_s=None):
    express("sad", hold_s)

def clear():
    """Eyes off, and forget the base mood."""
    global base, _revert
    if _revert is not None:
        _revert.cancel()
        _revert = None
    base = None
    LED.eyes_off()
