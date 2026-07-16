import RPi.GPIO as GPIO

class Hookswitch:
    """
    Detect events on the given GPIO pin and call callbacks if it is opened or
    closed.
    For detecting whether the hookswitch is raised or lowered.
    """

    def __init__(self, on_hook_down, on_hook_up, pin=26):
        # Callback when hookswitch up is detected.
        self._on_hook_up = on_hook_up
        # Callback when hookswitch down is detected.
        self._on_hook_down = on_hook_down
        # Pin to watch for hookswitch up or down.
        self._pin = pin

    def run(self):
        """
        Set up callbacks for when the hookswitch pin goes up or down, and return.
        """
        GPIO.setup(self._pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        def state_changed(channel):
            if(GPIO.input(channel) == 0):
                self._on_hook_up()
            else:
                self._on_hook_down()

        GPIO.add_event_detect(self._pin, GPIO.BOTH, callback=state_changed)
