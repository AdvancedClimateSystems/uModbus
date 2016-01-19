import pytest
import struct

from umodbus.client import tcp


def unpack_single_bit_values(response):
    byte_count = struct.unpack('>B', response[8:9])[0]

    fmt = '>' + ('B' * byte_count)
    return struct.unpack(fmt, response[9:])


def unpack_multi_bit_values(response):
    byte_count = struct.unpack('>B', response[8:9])[0]

    fmt = '>' + ('H' * (byte_count // 2))
    return struct.unpack(fmt, response[9:])


@pytest.mark.parametrize('function', [
    tcp.read_coils,
    tcp.read_discrete_inputs,
])
def test_response_on_single_bit_value_read_requests(sock, function):
    """ Validate response of a succesful Read Coils or Read Discrete Inputs
    request.
    """
    slave_id, starting_address, quantity = (1, 0, 10)
    req_adu = function(slave_id, starting_address, quantity)

    assert tcp.send_message(req_adu, sock) == [0, 1, 0, 1, 0, 1, 0, 1, 0,  1]


@pytest.mark.parametrize('function', [
    tcp.read_holding_registers,
    tcp.read_input_registers,
])
def test_response_on_multi_bit_value_read_requests(sock, function):
    """ Validate response of a succesful Read Holding Registers or Read
    Input Registers request.
    """
    slave_id, starting_address, quantity = (1, 0, 10)
    req_adu = function(slave_id, starting_address, quantity)

    assert tcp.send_message(req_adu, sock) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


@pytest.mark.parametrize('function', [
    tcp.write_single_coil,
    tcp.write_single_register,
])
def test_response_single_value_write_request(sock, function):
    """ Validate responde of succesful Read Single Coil and Read Single
    Register request.
    """
    slave_id, starting_address, quantity = (1, 0, 0)
    req_adu = function(slave_id, starting_address, quantity)

    assert tcp.send_message(req_adu, sock) == 0


@pytest.mark.parametrize('function, values', [
    (tcp.write_multiple_coils, [1, 1]),
    (tcp.write_multiple_registers, [1337, 15]),
])
def test_response_multi_value_write_request(sock, function, values):
    """ Validate response of succesful Write Multiple Coils and Write Multiple
    Registers request.

    Both requests write 2 values, starting address is 0.
    """
    slave_id, starting_address = (1, 0)
    req_adu = function(slave_id, starting_address, values)

    assert tcp.send_message(req_adu, sock) == 2
