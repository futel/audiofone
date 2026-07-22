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


def on_keydown(key):
    """Callback for when a key is pressed."""
    global dialplan
    # XXX We should instead handle a key_down from onhook correctly as
    #     a nop. Put more in the state machine and have the correct
    #     lack of action from onhook source, probably.
    # XXX Also need to handle keydown, keyup as a noop from busy,
    #     ringing, audio.
    if(dialplan.is_onhook()):
        return                  # Ignore keypresses when onhook.
    log("on_keydown %s" % key)
    tones.off()
    tones.key(key)
    dialplan.cancel_timers()    # XXX
    dialplan.start_busy_timer() # XXX

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
        # Busy wait until the keypad returns with key up result. Key down
        # results are handled with a callback, we busy wait for key up.
        key = keypad.read_key(on_keydown)
        if(key == ''):
            log("key read cancelled")
            continue
        dialplan.key_up(key=key)


if __name__ == "__main__":
    main()
