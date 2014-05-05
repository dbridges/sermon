# -*- coding: utf-8 -*-

"""
The main application run loop.
"""

from __future__ import print_function
from __future__ import unicode_literals

__version__ = "0.0.6"

import os
import sys
if os.name == 'nt':
    print('sermon is not compatabile with Windows.')
    sys.exit()

import argparse
import glob
import threading
import re
import time

import serial
from serial.tools import list_ports
import urwid

from .magics import magic

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


class ConsoleEdit(urwid.Edit):
    def __init__(self, callback, *args, **kwargs):
        super(ConsoleEdit, self).__init__(*args, **kwargs)
        self.callback = callback
        self.history = []
        self.history_pos = 0

    def keypress(self, size, key):
        if key == 'enter':
            self.callback(self.edit_text)
            self.history.append(self.edit_text)
            self.history_pos = 0
            self.set_edit_text('')
            return False
        elif key == 'up':
            # Cycle backwards in history, unless already as far back as we can
            # go.
            if self.history_pos == len(self.history):
                # Already as far as we can go in history.
                beep()
                return
            self.history_pos = limit(self.history_pos + 1,
                                     1, len(self.history))
            self.set_edit_text(
                self.history[-self.history_pos])
            self.set_edit_pos(len(self.edit_text))
        elif key == 'down':
            # Cycle forwards in history.
            if self.history_pos == 1:
                self.history_pos = 0
                return False
            elif self.history_pos == 0:
                beep()
                return

            self.history_pos = limit(self.history_pos - 1,
                                     1, len(self.history))
            self.set_edit_text(
                self.history[-self.history_pos])
            self.set_edit_pos(len(self.edit_text))
            return
        else:
            return super(ConsoleEdit, self).keypress(size, key)


class Sermon():
    """
    The main serial monitor class. Starts a read thread that polls the serial
    device and prints results to top window. Sends commands to serial device
    after they have been executed in the curses textpad.
    """
    def __init__(self, device, args):
        # Receive display widgets
        self.receive_text = urwid.Text('')
        body = urwid.ListBox([self.receive_text, urwid.Text('')])
        body.set_focus(1)

        # Draw main frame with status header and footer for commands.
        self.header = urwid.Text('', 'right')
        self.frame = urwid.Frame(body,
                                 header=urwid.AttrMap(self.header, 'statusbar'),
                                 footer=ConsoleEdit(self.on_edit_done, ': '),
                                 focus_part='footer')
        palette = [
            ('error', 'light red', 'black'),
            ('status', 'dark green', 'black'),
            ('statusbar', '', 'black')
        ]
        self.loop = urwid.MainLoop(self.frame, palette)

        self.fd = self.loop.watch_pipe(self.received_output)

        self.kill = False
        self.append_text = args.append.encode(
            'latin1').decode('unicode_escape')
        self.frame_text = args.frame.encode('latin1').decode('unicode_escape')
        self.byte_list_pattern = re.compile(
            '(\$\(([^\)]+?)\))|(\${([^\)]+?)})')
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
        self.header.set_text(('status',
                                    'Connected to %s' % self.serial.name))

        self.worker = threading.Thread(target=self.serial_read_worker)
        self.worker.daemon = True

    def on_edit_done(self, edit_text):
        """
        Callback called when editing is completed (after enter is pressed)
        """
        self.header.set_text(('status', 'Connected to %s' % self.serial.name))
        if edit_text[0] == '%':
            # Handle magic command.
            try:
                result = magic.execute(edit_text[1:])
            except Exception as e:
                self.header.set_text(('error', str(e)))
            return
        processed_command = ('%(frame)s%(command)s%(append)s%(frame)s' %
                             {'frame': self.frame_text,
                              'append': self.append_text,
                              'command': edit_text})
        # matches list of bytes $(0x08, 0x09, ... )
        strings = self.byte_list_pattern.split(processed_command)
        n = 0
        while n < len(strings) - 1:
            if strings[n] is None or strings[n] == '':
                n += 1
            elif self.byte_list_pattern.match(strings[n]):
                # list of bytes
                self.write_list_of_bytes(strings[n+1])
                n += 2
            else:
                self.serial.write(strings[n].encode('latin1'))
                n += 1
        self.serial.write(strings[-1].encode('latin1'))

    def received_output(self, data):
        self.receive_text.set_text(self.receive_text.text +
                                   data.decode('latin1'))

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
                    else:
                        os.write(self.fd, data)
                except UnicodeEncodeError or TypeError:
                    # Handle null bytes in string.
                    raise

    def write_list_of_bytes(self, string):
        byte_data = [int(s.strip(), 0) for s in string.split(',')]
        self.serial.write(bytearray(byte_data))

    def start(self):
        self.worker.start()
        self.loop.run()

    def stop(self):
        self.kill = True
        while self.worker.is_alive():
            pass
        self.serial.close()


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

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


def main():
    # Setup command line arguments
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
