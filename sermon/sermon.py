# -*- coding: utf-8 -*-

"""
The main application run loop.
"""

__version__ = "0.0.1"

import argparse
import glob
import os
import sys
import threading
import time
import curses
import curses.textpad
import signal

import serial

try:
   input = raw_input
except NameError:
   pass

class ConsoleTextbox(curses.textpad.Textbox):
    """
    Implements a single line console like text box with history.
    """

    KEY_BACKSPACE_MAC = 0x7F
    KEY_NEWLINE = ord('\n')
    KEY_RETURN = ord('\r')

    def __init__(self, win, insert_mode=False):
        super(ConsoleTextbox, self).__init__(win, insert_mode)
        self.history = []
        self.history_pos = 0

    def validator(self, ch):
        if ch == self.KEY_RETURN or ch == self.KEY_NEWLINE:
            return curses.ascii.ctrl(ord('g'))
        if ch == self.KEY_BACKSPACE_MAC:
            return curses.ascii.ctrl(ord('h'))
        else:
            return ch

    def edit(self):
        text = super(ConsoleTextbox, self).edit(self.validator)
        self.history.append(text)
        return text


class Sermon:
    """
    The main serial monitor class. Starts a read thread that polls the serial
    device and prints results to top window. Sends commands to serial device after
    they have been executed in the curses textpad.
    """
    def __init__(self, device, args):
        self.device = device
        self.serial = serial.Serial(device, args.baudrate, timeout=0.1)

    def serial_read_worker(self):
        """
        Reads serial device and prints results to upper curses window.
        """
        while True:
            time.sleep(0.1)
            num_bytes = self.serial.inWaiting()
            if num_bytes < 1:
                continue
            data = self.serial.read(num_bytes)
            self.read_window.addstr(data.decode('utf-8'))
            self.read_window.noutrefresh()
            self.send_window.noutrefresh()
            curses.doupdate()

    def main(self, stdscr):
        # curses initialization
        stdscr.clear()
        stdscr.addstr(curses.LINES - 1, 0, '> ')

        self.read_window = curses.newwin(curses.LINES - 2, curses.COLS)
        self.read_window.scrollok(True)

        self.send_window = curses.newwin(2, curses.COLS - 4,
                                         curses.LINES - 1, 2)

        stdscr.hline(curses.LINES - 2, 0, curses.ACS_HLINE, curses.COLS)

        stdscr.refresh()

        box = ConsoleTextbox(self.send_window)

        worker = threading.Thread(target=self.serial_read_worker)
        worker.daemon = True
        worker.start()

        while True:
            command = box.edit().strip('\n\r')
            if self.args.n:
                command += '\n'
            if self.args.r:
                command += '\r'
            self.serial.write(command.encode('utf-8'))
            self.send_window.erase()
            self.send_window.refresh()

    def start(self):
        curses.wrapper(self.main)

    def end(self):
        self.serial.close()


def serial_devices():
    """
    Returns a list of the available serial devices.
    """
    if os.name == 'nt':
        # windows
        devices = []
        for i in range(256):
            try:
                s = serial.Serial(i)
                s.close()
                devices.append('COM%d' % (i+1))
            except serial.SerialException:
                pass
        return devices
    else:
        return glob.glob('/dev/tty.*')  # Need this for python3 on mac.


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


def signal_handler(signal, frame):
    """
    Handle KeyboardInterrupt.
    """
    sys.exit()


def main():
    signal.signal(signal.SIGINT, signal_handler)
    # Setup command line arguments
    parser = argparse.ArgumentParser(
        description='Monitors specified serial device.')
    parser.add_argument('-n',
                        action='store_true',
                        help="Appends '\\n' to commands before they are sent.")
    parser.add_argument('-r',
                        action='store_true',
                        help="Appends '\\r' to commands before they are sent.")
    parser.add_argument('device',
                        default=False,
                        help='The path to the serial device.',
                        nargs='?')
    parser.add_argument('baudrate',
                        help='Baudrate, defaults to 115200.',
                        default=115200,
                        nargs='?',
                        type=int)
    parser.add_argument('-l',
                        action='store_true',
                        default=False,
                        help='List available serial devices.')

    commandline_args = parser.parse_args()

    # List serial devices and exit for argument '-l'
    if commandline_args.l:
        print_serial_devices()
        sys.exit()

    # If device is not specified, prompt user to select an available device.
    device = None
    if not commandline_args.device:
        devices = serial_devices()
        if len(devices) > 0:
            print('')
            [print('\t%d. %s' % (n+1, devices[n])) for n in range(len(devices))]
            print('')
            device_num = input('Select desired device [%d-%d]: ' % (1, len(devices)))
            try:
                device = devices[int(device_num) - 1]
            except (ValueError, IndexError):
                print('\nInvalid device selection.')
                sys.exit(1)
        else:
            print('No serial devices found.')
            sys.exit(1)
    else:
        device = commandline_args.device

    try:
        sermon = Sermon(device, commandline_args)
    except serial.serialutil.SerialException:
        print('Could not open device %s' % device)
        sys.exit(1)

    sermon.start()
