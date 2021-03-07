#!/usr/bin/python3

from hookswitch import Hookswitch
from keypad import Keypad
from tones import Tones
import RPi.GPIO as GPIO
import time
import threading
import random

# main audiofone entrypoint

GPIO.setmode(GPIO.BOARD)
HOOKSWITCH_PIN = 26
BUSY_TIMEOUT = 15.0 # seconds
hookstate = 'on'
dialed_number = ''
busy_timer = None
ring_timer = None

tones = Tones()
tones.off()

def play_busy():
    global hookstate
    global busy_timer
    if(hookstate == 'on'): return
    print("Too long off hook...")
    busy_timer = None
    go_busy()

def go_busy():
    global hookstate
    print("going BUSY")
    hookstate = 'busy wait'
    tones.off()
    tones.busy()

def start_busy_timer():
    global busy_timer
    print("starting busy timer")
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
    print("on keydown")
    # global hookstate
    # if(hookstate == 'on'): return
    # print("KEYDOWN %s hooksate %s" % (key, hookstate))
    # if hookstate == 'off': tones.off()
    # tones.key(key)
    # if hookstate == 'off':
    #     cancel_timers()
    #     start_busy_timer()

def on_handset_pickup():
    global hookstate
    global dialed_number
    print("Off hook")
    hookstate = 'off'
    dialed_number = ''
    tones.dialtone()
    start_busy_timer()

def on_hangup():
    global hookstate
    print("Hangup")
    hookstate = 'on'
    tones.off()
    keypad.cancel()
    cancel_timers()

def have_number(number):
    global ring_timer
    global hookstate
    print("*** YOU DID IT! %s" % (number))

    # look up number
    # if not exist play busy signal
    # if exists, random delay 3-10 seconds
    #    after delay play signal

    soundfile = get_soundfile(number)
    print("SOUNDFILE is %s" %(soundfile))
    if soundfile is '':
        tones.busy()
        return

    ring_time = random.randrange(4, 13)
    print("Ring for %d seconds" % (ring_time))
    tones.ring()
    hookstate = 'ringing'
    cancel_timers()
    ring_timer = threading.Timer(ring_time, lambda: play_audio_after_ring(soundfile))
    ring_timer.start()

def play_audio_after_ring(soundfile):
    global hookstate
    global ring_timer
    print("DEBUG: play() %s" %(soundfile))
    tones.off()
    tones.play_audio(soundfile)
    hookstate = 'playing audio'
    ring_timer = None

def get_soundfile(number):
    if number == '7592868': # internal test number
        return 'margarets_monologue'
    # TODO: Verify file exists on disk in known locations
    # If it does, return the number without path
    return ''

def play_audiofile(filename):
    global busy_timer
    busy_timer = threading.Timer(BUSY_TIMEOUT, play_busy)
    busy_timer.start()

def invalid_dialplan(number):
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
        print("key read cancelled")
        continue
    print(">> Key released => %s" %(k))
    if hookstate == 'off': tones.off()
    else: tones.keys_off()
    if(hookstate == 'off'):
        dialed_number = dialed_number + k
        if(invalid_dialplan(dialed_number)):
            go_busy()
            continue
        if(len(dialed_number) == 7):
            have_number(dialed_number)
            dialed_number = ''
