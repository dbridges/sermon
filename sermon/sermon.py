# -*- coding: utf-8 -*-

"""
The main application run loop.
"""

from __future__ import print_function
from __future__ import unicode_literals

__version__ = "0.0.4"

import os
import sys
if os.name == 'nt':
    print('sermon is not compatabile with Windows.')
    sys.exit()

import argparse
import glob
import threading
import curses
import curses.textpad
import re
import time
import logging

import serial
from serial.tools import list_ports

try:
    input = raw_input
except NameError:
    pass


parity_values = {'none': serial.PARITY_NONE,
                 'even': serial.PARITY_EVEN,
                 'odd': serial.PARITY_ODD,
                 'mark': serial.PARITY_MARK,
                 'space': serial.PARITY_SPACE}

stopbits_values = {'1': serial.STOPBITS_ONE,
                   '1.5': serial.STOPBITS_ONE_POINT_FIVE,
                   '2': serial.STOPBITS_TWO}


class ConsoleTextbox(curses.textpad.Textbox, object):
    """
    Implements a single line console like text box with history.
    """

    KEY_BACKSPACE_MAC = 0x7F
    KEY_NEWLINE = ord('\n')
    KEY_RETURN = ord('\r')

    def __init__(self, win, insert_mode=True):
        super(ConsoleTextbox, self).__init__(win, insert_mode)
        self.history = []
        self.history_pos = 0

    def validator(self, ch):
        if ch == self.KEY_RETURN or ch == self.KEY_NEWLINE:
            return curses.ascii.ctrl(ord('g'))
        elif ch == self.KEY_BACKSPACE_MAC:
            return curses.ascii.ctrl(ord('h'))
        elif ch == curses.KEY_UP:
            # Cycle backwards in history, unless already as far back as we can
            # go.
            if self.history_pos == len(self.history):
                # Already as far as we can go in history.
                curses.beep()
                return False
            self.history_pos = limit(self.history_pos + 1,
                                     1, len(self.history))
            self.win.erase()
            self.win.addstr(
                self.history[-self.history_pos])
            self.win.refresh()
        elif ch == curses.KEY_DOWN:
            # Cycle forwards in history.
            if self.history_pos == 1:
                self.history_pos = 0
                self.win.erase()
                self.win.refresh()
                return False
            elif self.history_pos == 0:
                curses.beep()
                return False

            self.history_pos = limit(self.history_pos - 1,
                                     1, len(self.history))
            self.win.erase()
            self.win.addstr(
                self.history[-self.history_pos])
            self.win.refresh()
        else:
            return ch

    def edit(self):
        text = super(ConsoleTextbox, self).edit(self.validator)
        logging.debug(repr(text))
        self.history.append(text.strip())
        self.history_pos = 0
        return text


class Sermon:
    """
    The main serial monitor class. Starts a read thread that polls the serial
    device and prints results to top window. Sends commands to serial device
    after they have been executed in the curses textpad.
    """
    def __init__(self, device, args):
        self.worker = None
        self.kill = False
        self.frame = args.frame
        self.append = args.append.encode('latin1').decode('unicode_escape')
        self.frame = args.frame.encode('latin1').decode('unicode_escape')
        self.byte_list_pattern = re.compile('(\$\(([^\)]+)\))')
        self.device = device
        self.serial = serial.Serial(device,
                                    baudrate=args.baud,
                                    bytesize=args.bytesize,
                                    parity=args.parity,
                                    stopbits=args.stopbits,
                                    xonxoff=args.xonxoff,
                                    rtscts=args.rtscts,
                                    dsrdtr=args.dsrdtr,
                                    timeout=0.1)
        time.sleep(0.1)
        self.serial.flushInput()

    def serial_read_worker(self):
        """
        Reads serial device and prints results to upper curses window.
        """
        while not self.kill:
            data = self.serial.read()
            if len(data) > 0:
                # Need to reverse \r and \n for curses, otherwise it just
                # clears the current line instead of making a new line. Also,
                # translate single \n to \n\r so curses returns to the first
                # column.
                try:
                    if data == b'\r':
                        continue
                    elif data == b'\n':
                        self.read_window.addstr('\n\r')
                    else:
                        self.read_window.addstr(data)
                except UnicodeEncodeError or TypeError:
                    # Handle null bytes in string.
                    raise
                self.read_window.noutrefresh()
                self.send_window.noutrefresh()
                curses.doupdate()

    def write_list_of_bytes(self, string):
        split_str = [s.strip() for s in string.split(',')]
        for s in split_str:
            try:
                self.serial.write(chr(int(s, 0) & 255).encode('latin1'))
            except:
                pass

    def write_command(self, command):
        processed_command = ('%(frame)s%(command)s%(append)s%(frame)s' %
                             {'frame': self.frame,
                              'append': self.append,
                              'command': command})
        # matches list of bytes $(0x08, 0x09, ... )
        strings = self.byte_list_pattern.split(processed_command)
        n = 0
        while n < len(strings) - 1:
            if self.byte_list_pattern.match(strings[n]):
                # list of bytes
                self.write_list_of_bytes(strings[n+1])
                n += 2
            else:
                self.serial.write(strings[n].encode('latin1'))
                n += 1
        self.serial.write(strings[-1].encode('latin1'))

    def main(self, stdscr):
        # curses initialization.
        curses.start_color()
        curses.use_default_colors()
        stdscr.clear()
        stdscr.addstr(curses.LINES - 1, 0, ': ')

        self.read_window = curses.newwin(curses.LINES - 1, curses.COLS)
        self.read_window.scrollok(True)
        self.read_window.erase()

        self.send_window = curses.newwin(1, curses.COLS - 3,
                                         curses.LINES - 1, 2)
        self.send_window.erase()

        stdscr.refresh()

        box = ConsoleTextbox(self.send_window)

        self.worker = threading.Thread(target=self.serial_read_worker)
        self.worker.daemon = True
        self.worker.start()

        while not self.kill:
            self.write_command(box.edit())
            self.send_window.erase()
            self.send_window.refresh()

        while self.worker.is_alive():
            pass

        self.serial.close()

    def start(self):
        curses.wrapper(self.main)

    def stop(self):
        self.kill = True


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


def main():
    # Setup command line arguments
    logging.basicConfig(filename='example.log', level=logging.DEBUG)
    parser = argparse.ArgumentParser(
        description='Monitors specified serial device.')
    parser.add_argument('-v', '--version',
                        action='store_true',
                        default=False,
                        help='Show version.')
    parser.add_argument('-l', '--list',
                        action='store_true',
                        default=False,
                        help='List available serial devices.')
    parser.add_argument('-b', '--baud',
                        help='Baudrate, defaults to 115200.',
                        default=115200,
                        type=int)
    parser.add_argument('--append',
                        type=str,
                        default='',
                        help='Append given string to every command.')
    parser.add_argument('--frame',
                        type=str,
                        default='',
                        help='Frame command with given string.')
    parser.add_argument('--bytesize',
                        choices=[5, 6, 7, 8],
                        default=8,
                        type=int,
                        help='Number of data bits, defaults to 8.')
    parser.add_argument('--parity',
                        choices=list(parity_values.keys()),
                        default='none',
                        help='Enable parity checking, defaults to none.')
    parser.add_argument('--stopbits',
                        choices=['1', '1.5', '2'],
                        default='1',
                        help='Number of stop bits, defaults to 1.')
    parser.add_argument('--xonxoff',
                        action='store_true',
                        help='Enable software flow control.')
    parser.add_argument('--rtscts',
                        action='store_true',
                        help='Enable hardware (RTS/CTS) flow control.')
    parser.add_argument('--dsrdtr',
                        action='store_true',
                        help='Enable hardware (DSR/DTR) flow control.')
    parser.add_argument('device',
                        default=False,
                        help='Device name or path.',
                        nargs='?')

    commandline_args = parser.parse_args()

    # List serial devices and exit for argument '-l'
    if commandline_args.list:
        print_serial_devices()
        sys.exit()
    elif commandline_args.version:
        print(__version__)
        sys.exit()

    # If device is not specified, prompt user to select an available device.
    device = None
    if not commandline_args.device:
        try:
            devices = serial_devices()
            if len(devices) > 0:
                print('')
                for n in range(len(devices)):
                    print('\t%d. %s' % (n+1, devices[n]))
                print('')
                device_num = input('Select desired device [%d-%d]: '
                                   % (1, len(devices)))
                try:
                    device = devices[int(device_num) - 1]
                except (ValueError, IndexError):
                    print('\nInvalid device selection.')
                    sys.exit(1)
            else:
                print('No serial devices found.')
                sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(1)
    else:
        device = commandline_args.device

    commandline_args.parity = parity_values[commandline_args.parity]
    commandline_args.stopbits = stopbits_values[commandline_args.stopbits]

    try:
        sermon = Sermon(device, commandline_args)
    except serial.serialutil.SerialException as e:
        print(str(e))
        sys.exit(1)

    try:
        sermon.start()
    except KeyboardInterrupt:
        sermon.stop()
