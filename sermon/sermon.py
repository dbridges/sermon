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
    The main serial monitor class. Starts a read thread that polls serial
    port and prints results to top window. Sends commands to serial port after
    they have been executed in the curses textpad.
    """
    def __init__(self, port, args):
        self.port = port
        self.serial = serial.Serial(port, args.baudrate, timeout=0.1)

    def serial_read_worker(self):
        n = 0
        while True:
            time.sleep(0.2)
            self.read_window.addstr('hello %d\n' % n)
            self.read_window.noutrefresh()
            self.send_window.noutrefresh()
            curses.doupdate()
            n += 1

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
            message = box.edit()
            self.read_window.addstr(message)
            self.read_window.refresh()
            self.send_window.erase()
            self.send_window.refresh()

    def start(self):
        try:
            curses.wrapper(self.main)
        except KeyboardInterrupt:
            sys.exit()

    def end(self):
        self.serial.close()


def serial_ports():
    """
    Returns a list of the available serial ports.
    """
    if os.name == 'nt':
        # windows
        ports = []
        for i in range(256):
            try:
                s = serial.Serial(i)
                s.close()
                ports.append('COM%d' % (i+1))
            except serial.SerialException:
                pass
        return ports
    else:
        return glob.glob('/dev/tty.*')  # Need this for python3 on mac.


def print_serial_ports():
    """
    Prints all of the available serial ports.
    """
    ports = serial_ports()
    if len(ports) == 0:
        print('No serial devices found.')
        return
    for p in ports:
        print(p)


def main():
    # Setup command line arguments
    parser = argparse.ArgumentParser(
        description='Monitors specified serial port.')
    parser.add_argument('-n',
                        action='store_true',
                        help="Appends '\\n' to commands before they are sent.")
    parser.add_argument('-r',
                        action='store_true',
                        help="Appends '\\r' to commands before they are sent.")
    parser.add_argument('port',
                        default=False,
                        help='The path to the serial port.',
                        nargs='?')
    parser.add_argument('baudrate',
                        help='Baudrate, defaults to 115200.',
                        default=115200,
                        nargs='?',
                        type=int)
    parser.add_argument('-l',
                        action='store_true',
                        default=False,
                        help='List available serial ports.')

    commandline_args = parser.parse_args()

    # List serial ports and exit for argument '-l'
    if commandline_args.l:
        print_serial_ports()
        sys.exit()

    # If port is not specified, try to find which one to use.
    port = None
    if not commandline_args.port:
        if len(serial_ports()) > 0:
            for p in serial_ports():
                response = input('Use %s [y/n]: ' % p)
                if 'y' in response.lower():
                    port = p
                    break
        else:
            print('No serial devices found.')
            sys.exit(1)
    else:
        port = commandline_args.port

    try:
        sermon = Sermon(port, commandline_args)
    except serial.serialutil.SerialException:
        print('Could not open port %s' % port)
        sys.exit(1)
    #sermon.start()
