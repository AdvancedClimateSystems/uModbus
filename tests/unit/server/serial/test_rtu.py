import pytest
from serial import Serial, serial_for_url
from umodbus.server.serial.rtu import RTUServer, get_char_size


@pytest.fixture
def rtu_server():
    return RTUServer()


def test_get_char_size():
    """ Test if correct char size is calculated. """
    assert get_char_size(11) == 1
    assert get_char_size(19201) == 0.0005


def test_rtu_server_create_response_adu(rtu_server):
    assert rtu_server.create_response_adu({'unit_id': 1}, b'') == b'\x01~\x80'


def test_rtu_server_serial_port(rtu_server):
    """" Test if RTUServer.serial_port sets correct timeout and
    inter_byte_timeout. """
    serial_port = Serial(baudrate=19201)
    rtu_server.serial_port = serial_port

    assert rtu_server.serial_port.timeout == 0.00175
    assert rtu_server.serial_port.inter_byte_timeout == 0.00075


def test_rtu_server_send_empty_message(rtu_server):
    rtu_server.serial_port = serial_for_url('loop://')
    rtu_server.serial_port.write(b'')

    with pytest.raises(ValueError):
        rtu_server.serve_once()
