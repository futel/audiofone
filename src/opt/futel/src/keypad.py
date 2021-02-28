
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
        GPIO.setup(PINS['row3'], GPIO.OUT)
        GPIO.output(PINS['row0'], GPIO.HIGH)
        GPIO.output(PINS['row1'], GPIO.HIGH)
        GPIO.output(PINS['row2'], GPIO.HIGH)
        GPIO.output(PINS['row3'], GPIO.HIGH)
        GPIO.setup(PINS['col0'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(PINS['col1'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(PINS['col2'], GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def cancel(self):
        self._cancelled = True

    def read_key(self):
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
                        print("down %s" % (key_name)
                        while(not GPIO.event_detected(colpin)):
                            print("still down %d" % (col))
                            time.sleep(0.025)
                        return key_name
                GPIO.output(rowpin, GPIO.HIGH)



    def xxread_key(self):
        self._enable_safely(PINS['col0'], GPIO.BOTH)
        GPIO.output(PINS['row0'], GPIO.LOW)
        while(True):
            if(GPIO.event_detected(PINS['col0'])):
                print("edge")
            time.sleep(0.100)

    def xread_key(self):
        row,col = self._wait_for_key_down()
        print("KEY DOWN: row%d col%d" % (row,col))
        # TODO: Call a callback on keydown
        self._wait_for_key_up(row,col)
        print("KEY UP: row%d col%d" % (row,col))
        return DIGITS[row][col]

        # self._remove_detect()
        # self._enable_detect()
        # while(not self._cancelled):
        #     for row in [0, 1, 2, 3]:
        #         key = self._scan_row(row)
        #         if self._cancelled : return ''
        #         if key != '' : return key
        # return '' # cancelled

    def _wait_for_key_down(self):
        self._remove_detect()
        self._enable_detect(GPIO.FALLING)
        while(not self._cancelled):
            for row in [0, 1, 2, 3]:
                col = self._detect(row)
                if self._cancelled : return [-1,-1] # cancelled
                if col > -1 : return [row,col]
        return [-1, -1] # cancelled

    def _wait_for_key_up(self, row, col):
        print("DEBUG: waiting for key up");
        pin = PINS['col%d' % (col)]
        GPIO.remove_event_detect(pin)
        self._enable_safely(pin, GPIO.RISING)
        GPIO.output(PINS['row%d' % (row)], GPIO.HIGH)
        while(not GPIO.event_detected(pin)):
            print("zzzz")
            time.sleep(0.250)

    def _detect(self, row):
        GPIO.output(PINS['row%d' % (row)], GPIO.LOW)
        time.sleep(0.025)   # for debugging, this should be like 5-25ms in practice

        # GPIO.output(PINS['row%d' % (row)], GPIO.HIGH)
        # TODO: Very much want to debounce, or at least wait until falling edge
        if GPIO.event_detected(PINS['col0']) :
            print("SHIT")
            return 0
        if GPIO.event_detected(PINS['col1']) : return 1
        if GPIO.event_detected(PINS['col2']) : return 2
        return -1
    #
    def _enable_detect(self, direction):
        self._enable_safely(PINS['col0'], direction)
        self._enable_safely(PINS['col1'], direction)
        self._enable_safely(PINS['col2'], direction)

    def _enable_safely(self, pin, direction):
        try:
            GPIO.add_event_detect(pin, direction)
        except:
            print("Configuring pin detect failed, trying again.")
            GPIO.add_event_detect(pin, direction)

    def _remove_detect(self):
        GPIO.remove_event_detect(PINS['col0'])
        GPIO.remove_event_detect(PINS['col1'])
        GPIO.remove_event_detect(PINS['col2'])


if __name__ == "__main__":
    GPIO.setmode(GPIO.BOARD)
    k = Keypad()
    while(True):
        print("Waiting for a key")
        digit = k.read_key()
        print("Saw digit: %s" % (digit))
