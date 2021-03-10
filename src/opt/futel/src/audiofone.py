#!/usr/bin/python3
"""
# main audiofone entrypoint
"""

from hookswitch import Hookswitch
from keypad import Keypad
from tones import Tones
from log import log
import RPi.GPIO as GPIO

from enum import Enum, auto
import time
import threading
import random

GPIO.setmode(GPIO.BOARD)
HOOKSWITCH_PIN = 26
BUSY_TIMEOUT = 15.0 # seconds
dialed_number = ''
busy_timer = None
ring_timer = None

tones = Tones()
tones.off()

# q&d lookup structure, intended to be temporary
numbers = {
    '7592868': '7592868_margarets_monologue'}


class NumberValidity(Enum):
    INVALID_KEY = auto()
    NOT_PREFIX = auto()
    POSSIBLE_PREFIX = auto()


class Hookstate(Enum):
    ON = auto()                 # hook down
    OFF = auto()                # hook up and collecting keypresses
    BUSY_WAIT = auto()
    RINGING = auto()
    PLAYING_AUDIO = auto()


hookstate = Hookstate.ON

def play_busy():
    global hookstate
    global busy_timer
    # Check for a hookswitch state which should prevent audio, although we
    # shouldn't be active anyway.
    # XXX should we instead check for not OFF?
    if(hookstate == Hookstate.ON):
        return
    log("Too long off hook...")
    busy_timer = None
    go_busy()

def go_busy():
    """ Set hookstate and play tones. """
    global hookstate
    log("going BUSY")
    hookstate = Hookstate.BUSY_WAIT
    tones.off()
    tones.busy()

def go_fast_busy():
    """ Set hookstate and play tones. """
    global hookstate
    log("going BUSY")
    hookstate = Hookstate.BUSY_WAIT
    tones.off()
    tones.busy()

def start_busy_timer():
    global busy_timer
    log("starting busy timer")
    cancel_timers()
    busy_timer = threading.Timer(BUSY_TIMEOUT, play_busy)
    busy_timer.start()

def cancel_timers():
    cancel_busy_timer()
    cancel_ring_timer()

def cancel_busy_timer():
    global busy_timer
    if busy_timer is not None:
        busy_timer.cancel()
    busy_timer = None

def cancel_ring_timer():
    global ring_timer
    if ring_timer is not None:
        ring_timer.cancel()
    ring_timer = None

def on_keydown(key):
    global hookstate
    if(hookstate == Hookstate.ON): return
    log("KEYDOWN %s hooksate %s" % (key, hookstate))
    if hookstate == Hookstate.OFF: tones.off()
    tones.key(key)
    if hookstate == Hookstate.OFF:
        cancel_timers()
        start_busy_timer()

def on_handset_pickup():
    global hookstate
    global dialed_number
    log("Off hook")
    hookstate = Hookstate.OFF
    dialed_number = ''
    tones.dialtone()
    start_busy_timer()

def on_hangup():
    global hookstate
    log("Hangup")
    hookstate = Hookstate.ON
    tones.off()
    keypad.cancel()
    cancel_timers()

def have_number(number):
    """
    Return soundfile or enum for number.
    """
    if(invalid_dialplan(number)):
        return NumberValidity.INVALID_KEY
    soundfile = get_soundfile(number)
    if soundfile is None:
        if not possible_soundfile(number):
            return NumberValidity.NOT_PREFIX
        return NumberValidity.POSSIBLE_PREFIX
    return soundfile

def start_number_event(soundfile):
    """
    Enter ringing state, start thread to play soundfile after timer.
    """
    global ring_timer
    global hookstate

    ring_time = random.randrange(4, 13)
    log("Ring for %d seconds" % (ring_time))
    tones.ring()
    hookstate = Hookstate.RINGING
    cancel_timers()
    ring_timer = threading.Timer(
        ring_time, lambda: play_audio_after_ring(soundfile))
    ring_timer.start()

def play_audio_after_ring(soundfile):
    global hookstate
    global ring_timer
    log("DEBUG: play() %s" %(soundfile))
    tones.off()
    tones.play_audio(soundfile)
    hookstate = Hookstate.PLAYING_AUDIO
    ring_timer = None

def get_soundfile(number):
    """ Return soundfile name corresponding to number. """
    return numbers.get(number)

def possible_soundfile(number):
    """ Return True if number might be a valid prefix. """
    return len(number) < max(len(k) for k in numbers.keys())

def invalid_dialplan(number):
    """Return True if number matches a forbidden sequence."""
    if number.startswith("0"): return True
    if "#" in number: return True
    if "*" in number: return True
    return False

keypad = Keypad(on_keydown)

hookswitch = Hookswitch(on_hook_up = on_handset_pickup,
                        on_hook_down = on_hangup,
                        pin = HOOKSWITCH_PIN)
hookswitch.run()

while(True):
    k = keypad.read_key()
    if(k == ''):
        log("key read cancelled")
        continue
    log(">> Key released => %s" %(k))
    if hookstate == Hookstate.OFF:
        tones.off()
    else:
        tones.keys_off()
    if(hookstate == Hookstate.OFF):
        dialed_number = dialed_number + k
        soundfile = have_number(dialed_number)
        if soundfile is NumberValidity.INVALID_KEY:
            go_busy()
        elif soundfile is NumberValidity.NOT_PREFIX:
            go_fast_busy()
        elif soundfile is NumberValidity.POSSIBLE_PREFIX:
            pass
        else:
            start_number_event(soundfile)
