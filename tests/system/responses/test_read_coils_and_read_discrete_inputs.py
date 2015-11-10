""" This module contains system tests for Modbus functions 01 Read Coils and 02
Read Discrete Inputs.

These functions return same type of responses, both for succesful exceptions
responses.

"""
import pytest
import struct

from ..validators import (validate_response_mbap, validate_function_code,
                          validate_single_bit_value_byte_count)


def unpack_single_bit_values(response):
    byte_count = struct.unpack('>B', response[8:9])[0]

    fmt = '>' + ('B' * byte_count)
    return struct.unpack(fmt, response[9:])


@pytest.mark.parametrize('function_code', [
    1,
    2,
])
def test_request_successfully(sock, mbap, function_code):
    """ Validate response PDU of a succesful request. """
    function_code, starting_address, quantity = (function_code, 0, 10)
    adu = mbap + struct.pack('>BHH', function_code, starting_address, quantity)

    sock.send(adu)
    resp = sock.recv(1024)

    validate_response_mbap(mbap, resp)
    validate_function_code(adu, resp)
    validate_single_bit_value_byte_count(adu, resp)

    assert unpack_single_bit_values(resp) == (170, 2)
