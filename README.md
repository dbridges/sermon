# Sermon

### SERMON IS CURRENTLY UNDER ACTIVE DEVELOPMENT

A command line serial monitor and transmitter written in python. Sermon performs the same function as the Arduino Serial Monitor, but is available on the command line. It depends on pyserial and python 2.7+ or python 3.3+ (may work with other versions).

### Examples

```
usage: sermon [-h] [-n] [-r] [-l] [port] [baudrate]
```

List available serial ports:
```
$ sermon -l
/dev/tty.Bluetooth-Incoming-Port
/dev/tty.Bluetooth-Modem
/dev/tty.usbserial-A601EI5P
```

Connect to a serial port with a baudrate of 115200 kbps:

```
$ sermon /dev/tty.usbserial-A601EI5P 115200
```

With no arguments `sermon` queries the user to select an available port and defaults to a baudrate of 115200.

```
$ sermon

	1. /dev/tty.Bluetooth-Incoming-Port
	2. /dev/tty.Bluetooth-Modem
	3. /dev/tty.usbserial-A601EI5P

Select desired device [1-3]:
```

### Usage

```
$ sermon -h
usage: sermon.py [-h] [-n] [-r] [-l] [port] [baudrate]

Monitors specified serial port.

positional arguments:
  port        The path to the serial port.
  baudrate    Baudrate, defaults to 115200.

optional arguments:
  -h, --help  show this help message and exit
  -n          Appends '\n' to commands before they are sent.
  -r          Appends '\r' to commands before they are sent.
  -l          List available serial ports.
```
