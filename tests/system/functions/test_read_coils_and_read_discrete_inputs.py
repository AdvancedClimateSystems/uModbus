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


@pytest.mark.parametrize('function_code, quantity', [
    (1, 0),
    (2, 0),
    (1, 0x07D0 + 1),
    (2, 0x07D0 + 1),
])
def test_request_with_invalid_addres(sock, mbap, function_code, quantity):
    """ Validate response PDU of request returning excpetion response with
    error code 3.
    """
    function_code, starting_address, quantity = (function_code, 0, quantity)
    adu = mbap + struct.pack('>BHH', function_code, starting_address, quantity)

    sock.send(adu)
    resp = sock.recv(1024)

    validate_response_mbap(mbap, resp)
    assert struct.unpack('>BB', resp[-2:]) == (0x80 + function_code, 3)


@pytest.mark.parametrize('function_code', [
    1,
    2,
])
def test_request_with_invalid_value(sock, mbap, function_code):
    """ Validate response PDU of request returning excpetion response with
    error code 2.
    """
    function_code, starting_address, quantity = (function_code, 9, 2)
    adu = mbap + struct.pack('>BHH', function_code, starting_address, quantity)

    sock.send(adu)
    resp = sock.recv(1024)

    validate_response_mbap(mbap, resp)
    assert struct.unpack('>BB', resp[-2:]) == (0x80 + function_code, 2)


@pytest.mark.parametrize('function_code', [
    1,
    2,
])
def test_request_with_server_failure(sock, mbap, function_code):
    """ Validate response PDU of request returning excpetion response with
    error code 4.
    """
    function_code, starting_address, quantity = (function_code, 666, 1)
    adu = mbap + struct.pack('>BHH', function_code, starting_address, quantity)

    sock.send(adu)
    resp = sock.recv(1024)

    validate_response_mbap(mbap, resp)
    assert struct.unpack('>BB', resp[-2:]) == (0x80 + function_code, 4)
