"""Contains miscellaneous utilities"""

import time

def log_message(code, message):
    print '[' + time.strftime("%H:%M:%S", time.gmtime()) + ' - ' + code.center(6) + '] ' + str(message)
