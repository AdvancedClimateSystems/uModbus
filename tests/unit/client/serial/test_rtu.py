import pytest
from serial import serial_for_url

from umodbus.client.serial.rtu import send_message


def test_send_message_with_timeout():
    """ Test if TimoutError is raised when serial port doesn't receive data."""
    s = serial_for_url('loop://', timeout=0)

    with pytest.raises(TimeoutError):
        send_message(b'', s)
