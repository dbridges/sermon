import re
from setuptools import setup

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('sermon/sermon.py').read(),
    re.M
    ).group(1)


with open('README.md', 'rb') as f:
    long_descr = f.read().decode('utf-8')


setup(
    name='sermon',
    packages=['sermon'],
    entry_points={
        'console_scripts': ['sermon=sermon.sermon:main']
        },
    version=version,
    description='Serial port monitor and transmitter.',
    long_description=long_descr,
    author='Daniel Bridges',
    author_email='dan@dayofthenewdan.com',
    url='http://github.com/dbridges/sermon')
