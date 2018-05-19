import pytest
from serial import serial_for_url

from umodbus.client.serial.rtu import send_message, read_coils


def test_send_message_with_timeout():
    """ Test if TimoutError is raised when serial port doesn't receive enough
    data.
    """
    s = serial_for_url('loop://', timeout=0)
    # as we are using a loop, we need the request will be read back as response
    # to test timeout we need a request with a response that needs more bytes
    message = read_coils(slave_id=0, starting_address=1, quantity=40)

    with pytest.raises(ValueError):
        send_message(message, s)
