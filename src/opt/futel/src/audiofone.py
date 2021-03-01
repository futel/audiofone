#!/usr/bin/python3

from hookswitch import Hookswitch
from keypad import Keypad
from tones import Tones
import RPi.GPIO as GPIO
import time

# main audiofone entrypoint

GPIO.setmode(GPIO.BOARD)
HOOKSWITCH_PIN = 26

tones = Tones()
tones.off()

def on_keydown(key):
    print("KEYDOWN %s" % (key))
    tones.off()
    tones.key(key)

keypad = Keypad(on_keydown)

def on_handset_pickup():
    print("Off hook")
    tones.dialtone()

def on_hangup():
    print("Hangup")
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
