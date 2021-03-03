#!/usr/bin/python3

from hookswitch import Hookswitch
from keypad import Keypad
from tones import Tones
import RPi.GPIO as GPIO
import time
import threading

# main audiofone entrypoint

GPIO.setmode(GPIO.BOARD)
HOOKSWITCH_PIN = 26
BUSY_TIMEOUT = 15.0 # seconds
hookstate = 'on'
dialed_number = ''
busy_timer = None

tones = Tones()
tones.off()

def play_busy():
    global hookstate
    global busy_timer
    if(hookstate == 'on'): return
    print("Too long off hook...going BUSY")
    hookstate = 'busy wait'
    tones.off()
    tones.busy()
    busy_timer = None

def start_busy_timer():
    global busy_timer
    print("starting busy timer")
    cancel_busy_timer()
    busy_timer = threading.Timer(BUSY_TIMEOUT, play_busy)
    busy_timer.start()

def cancel_busy_timer():
    global busy_timer
    if busy_timer is not None:
        busy_timer.cancel()
    busy_timer = None

def on_keydown(key):
    global hookstate
    if(hookstate != 'off'): return
    print("KEYDOWN %s" % (key))
    tones.off()
    tones.key(key)
    cancel_busy_timer()
    start_busy_timer()

keypad = Keypad(on_keydown)

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
    cancel_busy_timer()

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
    if not hookstate == 'busy wait': tones.off()
    if(hookstate == 'off'):
        dialed_number = dialed_number + k
        if(len(dialed_number) == 7):
            print("*** YOU DID IT! %s" % (dialed_number))
            tones.ring()
            dialed_number = ''
            start_busy_timer()
