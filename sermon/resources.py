# -*- coding: utf-8 -*-

"""
Store general resouces like help strings, etc.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

import sermon

help_str = """Sermon Magic Commands

%help, %h
Display help.

%about, %a
Display information about Sermon.

%exit, %quit, %q
Exit sermon.

%send [FILE], %s [FILE]
Send the contents of the given file to the connected serial device.

%logstart [FILE], %ls [FILE]
Start logging all received data to the given file.

%logon, %lo
Resume logging after a %logoff. %logstart must be called prior to using %logoff or %logon.

%logoff, %lf
Temporarily stop logging. Logging can be resumed using %logon.

%clear, %c
Clear the received data window.

%version, %v
Display the current version."""

about_str = """

Sermon version %s

Copyright (C) 2014 Daniel Bridges
http://github.com/dbridges/sermon

Licensed under the GPLv3
""" % sermon.__version__

help_status_str = 'Sermon        q: exit        (j, k) or arrow keys: scroll'
