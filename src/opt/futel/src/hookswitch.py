#!/usr/bin/env python2

import RPi.GPIO as GPIO
import datetime
import subprocess
import sys
import time

PIN = 7

GPIO.setmode(GPIO.BCM)          # pin numbering?
GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

hookswitch_up_state = False

def log(line):
    print(line)
    sys.stdout.flush()

def hookswitch_up():
    """ Play dialtone, if not playing, and toggle state. """
    global hookswitch_up_state
    if hookswitch_up_state is False:
        hookwitch_up_state = True
        log("play_dialtone")

def hookswitch_down():
    """ Stop playing dialtone, if playing, and toggle state. """
    global hookswitch_up_state
    if hookswitch_up_state is True:
        hookwitch_up_state = False
        log("terminate_dialtone")

def button_callback(channel):
    if GPIO.input(PIN):
        log("rising")         # release switch
        hookswitch_down()
    else:
        log("falling")        # contact switch
        hookswitch_up()

GPIO.add_event_detect(PIN, GPIO.BOTH, callback=button_callback)

while True:
    log("cycle")
    time.sleep(5)
