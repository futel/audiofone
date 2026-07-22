#!/usr/bin/python3
"""
Main audiofone entrypoint.
To be run continuously on the pi.
"""

import context
from hookswitch import Hookswitch
from keypad import Keypad
import dialnumbers
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

def start_number_event(soundfile):
    """
    Enter ringing state, start thread to play soundfile after timer.
    """
    global dialplan
    tones.ring()
    dialplan.cancel_timers()    # XXX
    dialplan.complete_key(soundfile=soundfile)

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
        k = keypad.read_key(on_keydown)
        if(k == ''):
            log("key read cancelled")
            continue
        dialplan.key_up()
        log(">> Key released => %s" %(k))

        if dialplan.is_onhook():
            # XXX We should instead handle a key_up from onhook correctly as
            #     a nop. Put more in the state machine and have the correct
            #     lack of action from onhook source, probably.
            # XXX Also need to handle keydown, keyup as a noop from busy,
            #     ringing, audio.
            tones.keys_off()
            continue            # Ignore keys when onhook.

        tones.off()             # This is a key release, stop playing tones.
        # Collect the number and add it to dialed_number.
        dialplan.dialed_number = dialplan.dialed_number + k # XXX
        soundfile = dialnumbers.have_number(dialplan.dialed_number)
        if soundfile is dialnumbers.NumberValidity.INVALID_KEY:
            dialplan.dialtone_timeout()
        elif soundfile is dialnumbers.NumberValidity.NOT_PREFIX:
            # XXX This should be a fast busy instead of slow busy.
            dialplan.dialtone_timeout()
        elif soundfile is dialnumbers.NumberValidity.POSSIBLE_PREFIX:
            log("possible soundfile %s" % dialplan.dialed_number)
        else:
            start_number_event(soundfile)


if __name__ == "__main__":
    main()
