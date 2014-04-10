# -*- coding: utf-8 -*-

"""
The main application run loop.
"""

__version__ = "0.0.1"

import os
import sys
if os.name == 'nt':
    print('sermon is not compatabile with Windows.')
    sys.exit()

import argparse
import glob
import threading
import time
import curses
import curses.textpad
import signal

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
    device and prints results to top window. Sends commands to serial device
    after they have been executed in the curses textpad.
    """
    def __init__(self, device, args):
        self.frame = args.frame
        self.append = args.append
        self.device = device
        self.serial = serial.Serial(device,
                                    baudrate=args.baudrate,
                                    bytesize=args.bytesize,
                                    parity=args.parity,
                                    stopbits=args.stopbits,
                                    xonxoff=args.xonxoff,
                                    rtscts=args.rtscts,
                                    dsrdtr=args.dsrdtr,
                                    timeout=0.1)
        self.serial.flushInput()
        self.serial.flushOutput()

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
        # curses initialization.
        curses.start_color()
        curses.use_default_colors()
        stdscr.clear()
        stdscr.addstr(curses.LINES - 1, 0, ': ')

        self.read_window = curses.newwin(curses.LINES - 1, curses.COLS)
        self.read_window.scrollok(True)

        self.send_window = curses.newwin(1, curses.COLS - 3,
                                         curses.LINES - 1, 2)

        stdscr.refresh()

        box = ConsoleTextbox(self.send_window)

        worker = threading.Thread(target=self.serial_read_worker)
        worker.daemon = True
        worker.start()

        while True:
            command = box.edit().strip('\n\r')
            command = ('%(frame)s%(command)s%(append)s%(frame)s' %
                       {'frame': self.frame,
                        'append': self.append,
                        'command': command})
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
    parser.add_argument('-l', '--list',
                        action='store_true',
                        default=False,
                        help='List available serial devices.')
    parser.add_argument('-b', '--baudrate',
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

    # If device is not specified, prompt user to select an available device.
    device = None
    if not commandline_args.device:
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
    else:
        device = commandline_args.device

    commandline_args.parity = parity_values[commandline_args.parity]
    commandline_args.stopbits = stopbits_values[commandline_args.stopbits]

    try:
        sermon = Sermon(device, commandline_args)
    except serial.serialutil.SerialException as e:
        print(str(e))
        sys.exit(1)

    sermon.start()
