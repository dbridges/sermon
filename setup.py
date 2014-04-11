# -*- coding: utf-8 -*-

import re
from setuptools import setup

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('sermon/sermon.py').read(),
    re.M
    ).group(1)


long_descr = """`Full Documentation
<http://github.com/dbridges/sermon>`_.
"""


setup(
    name='sermon',
    packages=['sermon'],
    license='GPL3',
    keywords='serial monitor console arduino',
    install_requires=['pyserial'],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Terminals :: Serial'
    ],
    entry_points={
        'console_scripts': ['sermon=sermon.sermon:main']
        },
    version=version,
    description='Serial device monitor and transmitter.',
    long_description=long_descr,
    author='Daniel Bridges',
    author_email='dan@dayofthenewdan.com',
    url='http://github.com/dbridges/sermon')
