import pytest

from umodbus.server.serial import AbstractSerialServer


@pytest.fixture
def abstract_serial_server():
    return AbstractSerialServer()


def test_abstract_serial_server_get_meta_data(abstract_serial_server):
    """ Test if meta data is correctly extracted from request. """
    assert abstract_serial_server.get_meta_data(b'\x01x\02\x03') ==\
        {'unit_id': 1}


def test_abract_serial_server_shutdown(abstract_serial_server):
    assert abstract_serial_server._shutdown_request is False

    abstract_serial_server.shutdown()

    assert abstract_serial_server._shutdown_request is True
