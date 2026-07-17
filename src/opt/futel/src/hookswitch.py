from gpiozero import Button

class Hookswitch:
    """
    Detect events on the given GPIO pin and call callbacks if it is opened or
    closed.
    For detecting whether the hookswitch is raised or lowered.
    Pin is a BCM GPIO number.
    """

    def __init__(self, on_hook_down, on_hook_up, pin=7):
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
        # pull_up: the pin idles high and is pulled low when the switch closes,
        # so a press (pin low) is hook up and a release (pin high) is hook down.
        self._button = Button(self._pin, pull_up=True)
        self._button.when_pressed = self._on_hook_up
        self._button.when_released = self._on_hook_down
