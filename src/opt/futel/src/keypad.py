
import time
import RPi.GPIO as GPIO
from log import log

# row scan, column detects

PINS = {
    'row0': 32, # GPIO 12
    'row1': 36, # GPIO 16
    'row2': 38, # GPIO 20
    'row3': 40, # GPIO 21
    'col0': 11, # GPIO 17
    'col1': 13, # GPIO 27
    'col2': 15  # GPIO 22
}
DIGITS = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['*', '0', '#'],
]

class Keypad:

    def __init__(self, on_keydown):
        self._cancelled = False
        self._on_keydown = on_keydown
        # TODO: get all this shit out of the constructor
        GPIO.setup(PINS['row0'], GPIO.OUT)
        GPIO.setup(PINS['row1'], GPIO.OUT)
        GPIO.setup(PINS['row2'], GPIO.OUT)
        GPIO.setup(PINS['row3'], GPIO.OUT)
        self._all_rows_high()
        GPIO.setup(PINS['col0'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(PINS['col1'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(PINS['col2'], GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def cancel(self):
        self._cancelled = True

    def read_key(self):
        """
        Busy wait until we detect a keydown or cancel. On keydown, callback and
        busy wait until we detect a keyup or cancel, then return token for what
        we detected.
        """
        self._cancelled = False
        self._all_rows_high()
        self._remove_detect()
        self._enable_detect(GPIO.BOTH)
        while(not self._cancelled):
            for row in [0, 1, 2, 3]:
                rowpin = PINS['row%d' % (row)]
                GPIO.output(rowpin, GPIO.LOW)
                time.sleep(0.025)
                for col in [0, 1, 2]:
                    colpin = PINS['col%d' % (col)]
                    if(GPIO.event_detected(colpin)):
                        key_name = DIGITS[row][col]

                        self._on_keydown(key_name)  # Invoke keydown callback

                        while(not GPIO.event_detected(colpin)):
                            if GPIO.input(colpin) == 1: break
                            if(self._cancelled): return ''
                            # log("DEBUG still down %s" % (key_name))
                            time.sleep(0.025)
                        return key_name
                GPIO.output(rowpin, GPIO.HIGH)
        return '' # cancelled

    def _enable_detect(self, direction):
        self._enable_safely(PINS['col0'], direction)
        self._enable_safely(PINS['col1'], direction)
        self._enable_safely(PINS['col2'], direction)

    def _enable_safely(self, pin, direction):
        try:
            GPIO.add_event_detect(pin, direction, bouncetime=150)
        except:
            log("Configuring pin detect failed, trying again.")
            GPIO.add_event_detect(pin, direction, bouncetime=150)

    def _remove_detect(self):
        GPIO.remove_event_detect(PINS['col0'])
        GPIO.remove_event_detect(PINS['col1'])
        GPIO.remove_event_detect(PINS['col2'])

    def _all_rows_high(self):
        GPIO.output(PINS['row0'], GPIO.HIGH)
        GPIO.output(PINS['row1'], GPIO.HIGH)
        GPIO.output(PINS['row2'], GPIO.HIGH)
        GPIO.output(PINS['row3'], GPIO.HIGH)

if __name__ == "__main__":
    # test method
    GPIO.setmode(GPIO.BOARD)
    def on_keydown(key_name):
        log("down %s" % (key_name))
    k = Keypad(on_keydown)
    while(True):
        log("Waiting for a key...")
        digit = k.read_key()
        log("Saw key: %s" % (digit))
