# -*- coding: utf-8 -*-

"""
Handle Magic commands.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

import os
import shlex

import sermon
from sermon.util import ThrowingArgumentParser


class MagicRunner(object):
    def __init__(self, app=None):
        self.cmds = {}
        self.app = app

    def cmd(self, cmd):
        """
        A decorator to register a magic command. This decorator should be
        applied to all magic commands.

        Parameters
        ----------
        cmd : str
            A string to be used for the given command. The string should be
            concise and not contain any whitespace.
        """
        def decorator(f):
            self.cmds[cmd] = f
            return f
        return decorator

    def execute(self, cmd_str):
        """
        Tries to execute the given magic command.

        Paramters
        ---------
        cmd_str : str
            The entire command line text with the opening % removed.

        Returns
        -------
        response : dict or None
            The dict should have the following keys: 'status', 'bytes_to_send'.
        """
        split_str = shlex.split(cmd_str)
        cmd = split_str[0]
        args = split_str[1:] if len(split_str) > 1 else []
        if cmd in self.cmds:
            return self.cmds[cmd](self.app, args)
        else:
            raise AttributeError("Command '%s' not found." % cmd)


magic = MagicRunner()


@magic.cmd('logstart')
def logstart(app, cmd_args):
    """
    Starts logging received serial data to specified logfile.
    """
    parser = ThrowingArgumentParser()
    parser.add_argument('filename', type=str)
    args = parser.parse_args(cmd_args)
    filename = os.path.expanduser(args.filename)

    try:
        f = open(filename, 'w')
        f.close()
    except:
        raise ValueError('Invalid filename specified.')

    app.logfile = filename
    app.logging = True

    return {'status': 'Logging to %s started.' % app.logfile,
            'bytes_to_send': None}


@magic.cmd('logon')
def logon(app, args):
    """
    Resumes logging. Logging must have already been started with %logstart.
    """
    if app.logfile is None:
        raise ValueError("Logging must first be started with %logstart.")
    app.logging = True
    return {'status': 'Logging resumed.',
            'bytes_to_send': None}


@magic.cmd('logoff')
def logoff(app, args):
    """
    Turns off logging.
    """
    app.logging = False
    return {'status': 'Logging stopped.',
            'bytes_to_send': None}


@magic.cmd('version')
def version(app, args):
    """
    Returns the current version number.
    """
    return {'status': 'version ' + sermon.__version__,
            'bytes_to_send': None}


@magic.cmd('send')
def send(app, cmd_args):
    """
    Sends the contents of the given file to the serial device.
    """
    parser = ThrowingArgumentParser()
    parser.add_argument('filename', type=str)
    args = parser.parse_args(cmd_args)
    filename = os.path.expanduser(args.filename)

    try:
        with open(filename, 'rb') as f:
            data = f.read()
    except:
        raise ValueError('Unable to read file.')

    return {'status': 'Sent %s' % filename,
            'bytes_to_send': data}


@magic.cmd('clear')
def clear(app, args):
    """
    Clears the received data window.
    """
    app.receive_window.set_text('')
    return {'status': None,
            'bytes_to_send': None}

@magic.cmd('exit')
def exit(app, args):
    """
    Exits the app.
    """
    app.exit()
    return {'status': None,
            'bytes_to_send': None}
