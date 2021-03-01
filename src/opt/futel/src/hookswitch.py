#!/usr/bin/env python3

import RPi.GPIO as GPIO

class Hookswitch:
    def __init__(self, on_hook_down, on_hook_up, pin = 26):
        self._on_hook_up = on_hook_up
        self._on_hook_down = on_hook_down
        self._pin = pin

    def run(self):
        GPIO.setup(self._pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        def state_changed(channel):
            if(GPIO.input(channel) == 0):
                self._on_hook_up()
            else:
                self._on_hook_down()

        GPIO.add_event_detect(self._pin, GPIO.BOTH, callback=state_changed)
