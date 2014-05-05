# -*- coding: utf-8 -*-

"""
Handle Magic commands.
"""

from .sermon import __version__

class MagicRunner(object):
    def __init__(self, serial=None):
        self.serial = serial
        self.cmds = {}

    def cmd(self, cmd):
        """
        A decorator to register a command.
        """
        def decorator(f):
            self.cmds[cmd] = f
            return f
        return decorator

    def execute(self, cmd):
        if cmd in self.cmds:
            return self.cmds[cmd]()
        else:
            raise AttributeError('Command not found.')

magic = MagicRunner()

@magic.cmd('version')
def version():
    return __version__

