__author__ = 'romilly'

import time
import sys
import serial
import serial.tools.list_ports
from contextlib import contextmanager

HIGH = 1
LOW = 0
DEFAULT_PORT='/dev/ttyACM0'

def _port():
    def osx_port():
        for portname, description, id in serial.tools.list_ports.comports():
            if 'tty.usbmodem' in portname: return portname
        raise serial.SerialException('No serial port on OS/X in: ' + str(serial.tools.list_ports.comports()))

    if 'linux' in sys.platform: return DEFAULT_PORT
    if 'darwin' in sys.platform: return osx_port()
    raise serial.SerialException('No serial port for platform: ' + sys.platform)

@contextmanager
def closing(closeable):
    try:
        yield closeable
    finally:
        closeable.close()

class SerialTransportException(serial.SerialException):
    """Failure in communicating with device"""

class SerialHalfDuplexTransport:
    def __init__(self, port=_port(), baud=115200):
        self._ser = serial.Serial(port, baud)
        self._receive()

    def _receive(self):
        return self._ser.readline()

    def _send(self, text):
        self._ser.write(text + '\n')
        self._ser.flush()

    def ask(self, text):
        self._send(text)
        return self._receive().strip()

    def close(self):
        self._ser.close()

OK = 0
class Arduino():
    def __init__(self, port=_port()):
        self._transport = SerialHalfDuplexTransport(port=port)
        time.sleep(0.1)

    def ask(self, *requests):
        return _error_checked(self._transport.ask(_do(requests)))

    def close(self):
        self._transport.close()

def _do(requests): return "".join(requests)
def _error_checked(result):
#    if len(result) == 0: raise SerialTransportException("Empty response from Arduino")
#    if result[0] != OK:
    return result[1:]


def on_pin(number): return str(number) + 'd'
def wait_millis(millis): return str(millis) + 'm'
def wait_micros(micros): return str(micros) + 'u'
def digital_write(value): return str(value) + 'o'
def digital_read(): return 'i'
def whois(): return "?"
def print_value(): return 'p'

def repeat(count, *requests):
    return command('{', count) + _do(requests) + '}'


