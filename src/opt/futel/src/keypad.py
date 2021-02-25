
import time
import RPi.GPIO as GPIO

# row scan, column callbacks

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

    def __init__(self):
        self._cancelled = False
        self._current_row = -1
        self._keydown = False
        # TODO: get all this shit out of the constructor
        GPIO.setup(PINS['row0'], GPIO.OUT)
        GPIO.setup(PINS['row1'], GPIO.OUT)
        GPIO.setup(PINS['row2'], GPIO.OUT)
        # GPIO.setup(PINS['row3'], GPIO.OUT)
        GPIO.output(PINS['row0'], GPIO.HIGH)
        GPIO.output(PINS['row1'], GPIO.HIGH)
        GPIO.output(PINS['row2'], GPIO.HIGH)
        # GPIO.output(PINS['row3'], GPIO.LOW)
        GPIO.setup(PINS['col0'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(PINS['col1'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # GPIO.setup(PINS['col2'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def cancel(self):
        self._cancelled = True

    # def column_changed(self, ch):
    #     row = self._current_row
    #     row_pin = PINS[row]
    #     row_value = GPIO.input(row_pin)
    #     col_value = GPIO.input(ch)
    #     print("oh boi %s col ??%d :: %d %d" % (row, ch, row_value, col_value))
    # def column_changed(self, col):
    #     def col_changed(ch):
    #         row = self._current_row
    #         if(row == -1):
    #             return
    #         colname = "col%d" % (col)
    #         # row_pin = PINS[row]
    #         # row_value = GPIO.input(row_pin)
    #         col_value = GPIO.input(ch)
    #         print("falling row%d %s :: %s %d" % (row, colname, DIGITS[row][col], col_value))
    #     return col_changed

    # def read_key(self):
    #     GPIO.add_event_detect(PINS['col0'], GPIO.BOTH,
    #         callback=self.column_changed(0))
    #     while(not self._cancelled):
    #         for row in [0, 1]:
    #             row_pin = PINS["row%d" % (row)]
    #             self._current_row = row
    #             GPIO.output(row_pin, GPIO.LOW)
    #             time.sleep(0.333);
    #             GPIO.output(row_pin, GPIO.HIGH)
    #             self._current_row = -1

    def read_key(self):
        """ blocking/polling method that returns '' if cancelled or a key if seen """
        while(not self._cancelled):
            for row in [0, 1, 2]:
                key = self._scan_row(row)
                if self._cancelled : return ''
                if key != '' : return key
        return '' # cancelled

    # def _xscan_row(self, row):
    #     # GPIO.add_event_detect(11, GPIO.RISING)
    #     # GPIO.output(32, GPIO.LOW)
    #     # if GPIO.event_detected(11):
    #     print("HEY YES DETECTED! %d" % (GPIO.input(11)))
    #     # GPIO.remove_event_detect(11)
    #
    #
    def _scan_row(self, row):
        self._enable_detect()
        key = self._detect(row)
        self._remove_detect()
        return key
    #
    #
    def _detect(self, row):
        GPIO.output(PINS['row%d' % (row)], GPIO.LOW)
        time.sleep(0.050)   # for debugging, this should be like 5-25ms in practice
        GPIO.output(PINS['row%d' % (row)], GPIO.HIGH)
        # TODO: Very much want to debounce, or at least wait until falling edge
        if GPIO.event_detected(PINS['col0']) : return DIGITS[row][0]
        if GPIO.event_detected(PINS['col1']) : return DIGITS[row][1]
    #     if GPIO.event_detected(PINS['col2']) : return DIGITS[row][2]
        return ''
    #
    def _enable_detect(self):
        self._enable_safely(PINS['col0'])
        self._enable_safely(PINS['col1'])
        # GPIO.add_event_detect(PINS['col2'], GPIO.FALLING)

    def _enable_safely(self, pin):
        try:
            GPIO.add_event_detect(pin, GPIO.BOTH)
        except:
            print("Shit failed, just trying again because fuck it")
            GPIO.add_event_detect(pin, GPIO.BOTH)

    def _remove_detect(self):
        GPIO.remove_event_detect(PINS['col0'])
        GPIO.remove_event_detect(PINS['col1'])
    #     GPIO.remove_event_detect(PINS['col2'])


if __name__ == "__main__":
    GPIO.setmode(GPIO.BOARD)
    k = Keypad()
    # GPIO.output(PINS['row0'], GPIO.HIGH)
    while(True):
        print("Waiting for a key")
        # time.sleep(0.500)
        digit = k.read_key()
        print("Saw digit: %s" % (digit))
