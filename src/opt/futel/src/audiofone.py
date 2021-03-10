#!/usr/bin/python3

from hookswitch import Hookswitch
from keypad import Keypad
from tones import Tones
from log import log
import RPi.GPIO as GPIO

from enum import Enum, auto
import time
import threading
import random

# main audiofone entrypoint

GPIO.setmode(GPIO.BOARD)
HOOKSWITCH_PIN = 26
BUSY_TIMEOUT = 15.0 # seconds
dialed_number = ''
busy_timer = None
ring_timer = None

tones = Tones()
tones.off()


class Hookstate(Enum):
    ON = auto()
    BUSY_WAIT = auto()
    OFF = auto()
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
    Perform event for number.
    """
    global ring_timer
    global hookstate
    log("*** YOU DID IT! %s" % (number))

    # look up number
    # if not exist play busy signal
    # if exists, random delay 3-10 seconds
    #    after delay play signal

    soundfile = get_soundfile(number)
    log("SOUNDFILE is %s" %(soundfile))
    if soundfile is '':
        go_fast_busy()
        return

    # Enter ringing state, start thread to play soundfile after timer
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
    if number == '7592868': # internal test number
        return 'margarets_monologue'
    # TODO: Verify file exists on disk in known locations
    # If it does, return the number without path
    return ''

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
    if hookstate == Hookstate.OFF: tones.off()
    else: tones.keys_off()
    if(hookstate == Hookstate.OFF):
        dialed_number = dialed_number + k
        if(invalid_dialplan(dialed_number)):
            go_busy()
            continue
        if(len(dialed_number) == 7):
            have_number(dialed_number)
            dialed_number = ''
