"""Contains miscellaneous utilities"""
# Grupo 14:
# 81900 - Nuno Anselmo
# 81936 - Liliana Oliveira
# 82047 - Andre Mendes

import time

DEBUG_LEVEL = 0

def log_message(code, message):
    """Formats and prints the given message"""
    print '[' + format_timestamp(time.time()) + ' - ' + code.center(5) + '] ' + str(message)

def format_timestamp(timestamp):
    """Formats a timestamp"""
    return time.strftime("%H:%M:%S", time.localtime(timestamp))
