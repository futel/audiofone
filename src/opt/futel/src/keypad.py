import time
from gpiozero import Button, OutputDevice

# row scan, column detects
# Pins are BCM GPIO numbers.

PINS = {
    'row0': 12,
    'row1': 16,
    'row2': 20,
    'row3': 21,
    'col0': 17,
    'col1': 27,
    'col2': 22
}
DIGITS = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['*', '0', '#'],
]

class Keypad:
    """
    Detect events on GPIO pins and call callbacks if they are opened or
    closed.
    For detecting when keys are pressed or released.
    """

    def __init__(self):
        self._cancelled = False
        # TODO: get all this shit out of the constructor
        self._rows = [
            OutputDevice(PINS['row%d' % (row)], initial_value=True)
            for row in [0, 1, 2, 3]
        ]
        # Columns idle high (pull_up) and read low when a scanned row drives
        # their key low; Button.is_pressed is True in that low state.
        self._cols = [
            Button(PINS['col%d' % (col)], pull_up=True)
            for col in [0, 1, 2]
        ]

    def cancel(self):
        self._cancelled = True

    def read_key(self, on_keydown):
        """
        Busy wait until we detect a keydown or cancel. On keydown, callback and
        busy wait until we detect a keyup or cancel, then return token for what
        we detected.
        """
        self._cancelled = False
        self._all_rows_high()
        while(not self._cancelled):
            for row in [0, 1, 2, 3]:
                self._rows[row].off()
                time.sleep(0.025)
                for col in [0, 1, 2]:
                    if(self._cols[col].is_pressed):
                        key_name = DIGITS[row][col]

                        on_keydown(key_name)  # Invoke keydown callback

                        while(self._cols[col].is_pressed):
                            if(self._cancelled): return ''
                            time.sleep(0.025)
                        return key_name
                self._rows[row].on()
        return '' # cancelled

    def _all_rows_high(self):
        for row in self._rows:
            row.on()

if __name__ == "__main__":
    # test method
    from log import log
    def on_keydown(key_name):
        log("down %s" % (key_name))
    k = Keypad()
    while(True):
        log("Waiting for a key...")
        digit = k.read_key(on_keydown)
        log("Saw key: %s" % (digit))
