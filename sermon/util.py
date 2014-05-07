# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

import argparse
import sys
import glob

from serial.tools import list_ports


class ArgumentParseError(Exception):
    pass


class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParseError(message)


def beep():
    sys.stdout.write('\a')


def limit(n, minimum, maximum):
    """
    Limits n to be within minimum and maximum.
    """
    if n < minimum:
        return minimum
    elif n > maximum:
        return maximum
    return n


def serial_devices():
    """
    Returns a list of the available serial devices.
    """
    if sys.platform == 'darwin' and sys.version_info.major == 3:
        # pyserial's builtin port detection not working on mac with python 3
        return glob.glob('/dev/cu.*')
    else:
        return [p[0] for p in list_ports.comports()]


def print_serial_devices():
    """
    Prints all of the available serial devices.
    """
    devices = serial_devices()
    if len(devices) == 0:
        print('No serial devices found.')
        return
    for p in devices:
        print(p)
