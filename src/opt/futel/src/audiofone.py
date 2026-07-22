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

import time

# BCM GPIO pin on the pi connected to the hookswitch.
HOOKSWITCH_PIN = 7

# globals for the ongoing interaction
dialplan = None
tones = None
keypad = None


def on_hangup():
    """
    Callback for when the hookswitch is lowered.
    Set dialplan state, cancel all tones and timers.
    """
    global dialplan
    dialplan.hook_down()
    keypad.cancel()             # XXX

def main():
    """ Set up hardware and run the read/dispatch loop forever. """
    global dialplan
    global tones
    global keypad

    tones = Tones()
    tones.off()

    # Keypad monitor, we use it to busy wait for events.
    keypad = Keypad()

    dialplan = context.get_dialplan(tones)

    # Hookswitch monitor. This will call the callbacks without blocking.
    hookswitch = Hookswitch(on_hook_up=dialplan.hook_up,
                            on_hook_down=on_hangup,
                            pin=HOOKSWITCH_PIN)
    hookswitch.run()

    while(True):
        # Tell the keypad to busy wait and call dialplan.key_press
        # when a key press happens, with the key as an argument, then
        # busy wait and return the key.
        key = keypad.read_key(dialplan.key_press)
        # The key has been lifted or cancelled.
        if(key == ''):
            log("key read cancelled")
            continue
        dialplan.key_release(key=key)


if __name__ == "__main__":
    main()
