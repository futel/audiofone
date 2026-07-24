#!/usr/bin/python3
"""
Main audiofone entrypoint.
To be run continuously on the pi.
"""

# q&d way to configure which context to use
#import dialtone_context as context
import zoo_context as context


from hookswitch import Hookswitch
from keypad import Keypad
from log import log


# BCM GPIO pin on the pi connected to the hookswitch.
HOOKSWITCH_PIN = 7

def main():
    """ Set up hardware and run the read/dispatch loop forever. """
    # Keypad monitor, we use it to busy wait for events.
    keypad = Keypad()
    # Get dialplan state machine, which can cancel the keypad.
    dialplan = context.get_dialplan(keypad)
    # Set up the hookswitch to callback the dialplan transitions.
    hookswitch = Hookswitch(
        on_hook_up=dialplan.hook_up,
        on_hook_down=dialplan.hook_down,
        pin=HOOKSWITCH_PIN)
    hookswitch.run()

    while(True):
        # Tell the keypad to busy wait and call dialplan.key_press
        # when a key press happens, with the key as an argument, then
        # busy wait and return the key on key release or cancel.
        key = keypad.read_key(dialplan.key_press)
        # The key has been lifted or cancelled.
        if(key == ''):
            log("key read cancelled")
            continue
        # Callback the dialplan transition with the key released.
        dialplan.key_release(key=key)


if __name__ == "__main__":
    main()
