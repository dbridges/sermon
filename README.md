# Sermon

A command line serial monitor and transmitter written in python for use in posix systems. Sermon is not compatible with windows. Sermon performs the same function as the Arduino Serial Monitor, but is available on the command line. It depends on pyserial and python 2.7+ or python 3.3+ (may work with other versions).

### Examples

```
usage: sermon [-h] [-n] [-r] [-l] [device] [baudrate]
```

List available serial devices:
```
$ sermon -l
/dev/tty.Bluetooth-Incoming-device
/dev/tty.Bluetooth-Modem
/dev/tty.usbserial-A601EI5P
```

Connect to a serial device with a baudrate of 115200 kbps:

```
$ sermon -b 115200 /dev/tty.usbserial-A601EI5P
```

With no arguments `sermon` queries the user to select an available device and defaults to a baudrate of 115200.

```
$ sermon

	1. /dev/tty.Bluetooth-Incoming-device
	2. /dev/tty.Bluetooth-Modem
	3. /dev/tty.usbserial-A601EI5P

Select desired device [1-3]:
```

### Usage

```
$ sermon -h
usage: sermon-runner.py [-h] [-l] [-b BAUD] [--append APPEND] [--frame FRAME]
                        [--bytesize {5,6,7,8}]
                        [--parity {even,none,space,odd,mark}]
                        [--stopbits {1,1.5,2}] [--xonxoff] [--rtscts]
                        [--dsrdtr]
                        [device]

Monitors specified serial device.

positional arguments:
  device                Device name or path.

optional arguments:
  -h, --help            show this help message and exit
  -l, --list            List available serial devices.
  -b BAUD, --baud BAUD  Baudrate, defaults to 115200.
  --append APPEND       Append given string to every command.
  --frame FRAME         Frame command with given string.
  --bytesize {5,6,7,8}  Number of data bits, defaults to 8.
  --parity {even,none,space,odd,mark}
                        Enable parity checking, defaults to none.
  --stopbits {1,1.5,2}  Number of stop bits, defaults to 1.
  --xonxoff             Enable software flow control.
  --rtscts              Enable hardware (RTS/CTS) flow control.
  --dsrdtr              Enable hardware (DSR/DTR) flow control.
```

### Todo

- Add magic commands to execute special functions (ex. send the contents of a file over the serial port).
- Log all received data to a file.
- Allow raw bytes to be sent over command line, tentative syntax: ```$(0x7D,0x7B,0xFF)```
