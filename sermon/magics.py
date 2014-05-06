# -*- coding: utf-8 -*-

"""
Handle Magic commands.
"""

import shlex
from .sermon import __version__


class MagicRunner(object):
    def __init__(self):
        self.cmds = {}

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

        cmd, *args = shlex.split(cmd_str)
        if cmd in self.cmds:
            return self.cmds[cmd](args)
        else:
            raise AttributeError("Command '%s' not found." % cmd)


magic = MagicRunner()


@magic.cmd('logon')
def logon(args):
    """
    Turns on logging.
    """
    return {'status': 'Logging started.', 'bytes_to_send': None}


@magic.cmd('version')
def version(args):
    """
    Returns the current version number.
    """
    return {'status': __version__, 'bytes_to_send': None}
