#!/usr/bin/python3

from hookswitch import Hookswitch
from keypad import Keypad
from tones import Tones
import RPi.GPIO as GPIO
import time

# main audiofone entrypoint

GPIO.setmode(GPIO.BOARD)
HOOKSWITCH_PIN = 26
hookstate = 'on'
dialed_number = ''

tones = Tones()
tones.off()

def on_keydown(key):
    global hookstate
    if(hookstate == 'on'): return
    print("KEYDOWN %s" % (key))
    tones.off()
    tones.key(key)

keypad = Keypad(on_keydown)

def on_handset_pickup():
    global hookstate
    global dialed_number
    print("Off hook")
    hookstate = 'off'
    dialed_number = ''
    tones.dialtone()

def on_hangup():
    global hookstate
    print("Hangup")
    hookstate = 'on'
    tones.off()
    keypad.cancel()

hookswitch = Hookswitch(on_hook_up = on_handset_pickup,
                        on_hook_down = on_hangup,
                        pin = HOOKSWITCH_PIN)
hookswitch.run()

while(True):
    k = keypad.read_key()
    print(">> Key released => %s" %(k))
    tones.off()
    if(hookstate == 'off'):
        dialed_number = dialed_number + k
        if(len(dialed_number) == 7):
            print("*** YOU DID IT! %s" % (dialed_number))
            dialed_number = ''
