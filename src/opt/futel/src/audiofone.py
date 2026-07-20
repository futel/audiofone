#!/usr/bin/python3
"""
Main audiofone entrypoint.
To be run continuously on the pi.
"""

import context
from hookswitch import Hookswitch
from keypad import Keypad
from tones import Tones
from log import log

from enum import Enum, auto
import os
import time
import threading
import random

# BCM GPIO pin on the pi connected to the hookswitch.
HOOKSWITCH_PIN = 7
BUSY_TIMEOUT = 15.0 # seconds
audio_directory = "/mnt/futel"

# globals for the ongoing interaction
dialed_number = ''
dialplan = None
busy_timer = None
ring_timer = None
tones = None
keypad = None


class NumberValidity(Enum):
    INVALID_KEY = auto()
    NOT_PREFIX = auto()
    POSSIBLE_PREFIX = auto()


def play_busy():
    global dialplan
    global busy_timer
    # Check for a hookswitch state which should prevent audio, although we
    # shouldn't be active anyway, we don't consistently check this, etc.
    if(dialplan.is_onhook()):
        return
    log("Too long off hook...")
    busy_timer = None
    dialplan.dialtone_timeout()

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
    """Callback for when a key is pressed."""
    global dialplan
    if(dialplan.is_onhook()):
        return                  # Ignore keypresses when onhook.
    log("on_keydown %s" % key)
    tones.off()
    tones.key(key)
    cancel_timers()
    start_busy_timer()

def on_handset_pickup():
    """Callback for when the hookswitch is raised."""
    global dialplan
    global dialed_number
    dialplan.hook_up()
    dialed_number = ''
    tones.dialtone()
    start_busy_timer()

def on_hangup():
    """
    Callback for when the hookswitch is lowered.
    Set dialplan state, cancel all tones and timers.
    """
    global dialplan
    dialplan.hook_down()
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
    if soundfile is not None:
        return soundfile
    if not possible_number(number):
        return NumberValidity.NOT_PREFIX
    return NumberValidity.POSSIBLE_PREFIX

def start_number_event(soundfile):
    """
    Enter ringing state, start thread to play soundfile after timer.
    """
    global dialplan
    global ring_timer
    ring_time = random.randrange(4, 13)
    log("Ring for %d seconds" % (ring_time))
    tones.ring()
    cancel_timers()
    dialplan.complete_key()
    ring_timer = threading.Timer(
        ring_time, lambda: play_audio_after_ring(soundfile))
    ring_timer.start()

def play_audio_after_ring(soundfile):
    global dialplan
    global ring_timer
    dialplan.done_ringing(soundfile=soundfile)
    ring_timer = None

def soundfile_number(filename):
    """ Return number corresponding to soundfile. """
    filename = filename.split('.').pop(0)
    return filename.split('_').pop(0)

def get_soundfile(number):
    """ Return normalized soundfile name corresponding to number. """
    for filename in os.listdir(audio_directory):
        if soundfile_number(filename) == number:
            # Remove suffix, if there, player doesn't want it.
            # Assume only one . in filename.
            return filename.split('.').pop(0)
    return None

def possible_number(number):
    """ Return True if number should not receive an invalid notification. """
    possible_numbers = [
        soundfile_number(filename) for filename in os.listdir(audio_directory)]
    if len(number) < max(len(number) for number in possible_numbers):
        return True
    return False

def invalid_dialplan(number):
    """Return True if number matches a forbidden sequence."""
    if number.startswith("0"): return True
    if "#" in number: return True
    if "*" in number: return True
    return False

def main():
    """ Set up hardware and run the read/dispatch loop forever. """
    global dialplan
    global dialed_number
    global tones
    global keypad

    tones = Tones()
    tones.off()
    dialplan = context.get_dialplan(tones)

    # Hookswitch monitor. This will call the callbacks without blocking.
    hookswitch = Hookswitch(on_hook_up = on_handset_pickup,
                            on_hook_down = on_hangup,
                            pin = HOOKSWITCH_PIN)
    hookswitch.run()

    # Keypad monitor, we use it to busy wait for events.
    keypad = Keypad(on_keydown)

    while(True):
        # Busy wait until the keypad returns with key up result. Key down
        # results are handled with a callback, we busy wait for key up.
        k = keypad.read_key()
        if(k == ''):
            log("key read cancelled")
            continue
        dialplan.key_up()
        log(">> Key released => %s" %(k))

        if dialplan.is_onhook():
            tones.keys_off()
            continue            # Ignore keys when onhook.

        tones.off()             # This is a key release, stop playing tones.
        # Collect the number and add it to our global dialed_number.
        dialed_number = dialed_number + k
        soundfile = have_number(dialed_number)
        if soundfile is NumberValidity.INVALID_KEY:
            dialplan.dialtone_timeout()
        elif soundfile is NumberValidity.NOT_PREFIX:
            # XXX This should be a fast busy instead of slow busy.
            dialplan.dialtone_timeout()
        elif soundfile is NumberValidity.POSSIBLE_PREFIX:
            log("possible soundfile %s" % dialed_number)
        else:
            start_number_event(soundfile)


if __name__ == "__main__":
    main()
