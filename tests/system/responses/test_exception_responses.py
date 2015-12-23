import pytest
import struct
from functools import partial

from ..validators import validate_response_mbap
from umodbus.client import tcp


@pytest.mark.parametrize('function, quantity', [
    (tcp.read_coils, 0),
    (tcp.read_discrete_inputs, 0),
    (tcp.read_holding_registers, 0),
    (tcp.read_input_registers, 0),
    (tcp.read_coils, 0x07D0 + 1),
    (tcp.read_discrete_inputs, 0x07D0 + 1),
    (tcp.read_holding_registers, 0x007D + 1),
    (tcp.read_input_registers, 0x007D + 1),
])
def test_request_returning_invalid_data_value_error(sock, function, quantity):
    """ Validate response PDU of request returning excepetion response with
    error code 3.
    """
    slave_id, starting_address = (1, 0)
    adu = function(slave_id, starting_address, quantity)

    mbap = adu[:7]
    function_code = int(adu[7])

    sock.send(adu)
    resp = sock.recv(1024)

    validate_response_mbap(mbap, resp)
    assert struct.unpack('>BB', resp[-2:]) == (0x80 + function_code, 3)


@pytest.mark.parametrize('function', [
    (partial(tcp.read_coils, 1, 9, 2)),
    (partial(tcp.read_discrete_inputs, 1, 9, 2)),
    (partial(tcp.read_holding_registers, 1, 9, 2)),
    (partial(tcp.read_input_registers, 1, 9, 2)),
    (partial(tcp.write_single_coil, 1, 11, 0)),
    (partial(tcp.write_single_register, 1, 11, 1337)),
    (partial(tcp.write_multiple_coils, 1, 9, [1, 1])),
    (partial(tcp.write_multiple_registers, 1, 9, [1337, 15])),
])
def test_request_returning_invalid_data_address_error(sock, function):
    """ Validate response PDU of request returning excepetion response with
    error code 2.
    """
    adu = function()

    mbap = adu[:7]
    function_code = int(adu[7])

    sock.send(adu)
    resp = sock.recv(1024)

    validate_response_mbap(mbap, resp)
    assert struct.unpack('>BB', resp[-2:]) == (0x80 + function_code, 2)


@pytest.mark.parametrize('function', [
    (partial(tcp.read_coils, 1, 666, 1)),
    (partial(tcp.read_discrete_inputs, 1, 666, 1)),
    (partial(tcp.read_holding_registers, 1, 666, 1)),
    (partial(tcp.read_input_registers, 1, 666, 1)),
    (partial(tcp.write_single_coil, 1, 666, 0)),
    (partial(tcp.write_single_register, 1, 666, 1337)),
    (partial(tcp.write_multiple_coils, 1, 666, [1])),
    (partial(tcp.write_multiple_registers, 1, 666, [1337])),
])
def test_request_returning_server_device_failure_error(sock, function):
    """ Validate response PDU of request returning excepetion response with
    error code 4.
    """
    adu = function()

    mbap = adu[:7]
    function_code = int(adu[7])

    sock.send(adu)
    resp = sock.recv(1024)

    validate_response_mbap(mbap, resp)
    assert struct.unpack('>BB', resp[-2:]) == (0x80 + function_code, 4)
