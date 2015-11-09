import pytest
import struct


def validate_transaction_id(request_mbap, response):
    """ Check if Transaction id in request and response is equal. """
    assert struct.unpack('>H', request_mbap[:2]) == \
        struct.unpack('>H', response[:2])


def validate_protocol_id(request_mbap, response):
    """ Check if Protocol id in request and response is equal. """
    assert struct.unpack('>H', request_mbap[2:4]) == \
        struct.unpack('>H', response[2:4])


def validate_length(response):
    """ Check if Length field contains actual length of response. """
    assert struct.unpack('>H', response[4:6])[0] == len(response[6:])


def validate_unit_id(request_mbap, response):
    """ Check if Unit id in request and response is equal. """
    assert struct.unpack('>B', request_mbap[6:7]) == \
        struct.unpack('>B', response[6:7])


def validate_response_mbap(request_mbap, response):
    """ Validate if fields in response MBAP contain correct values. """
    validate_transaction_id(request_mbap, response)
    validate_protocol_id(request_mbap, response)
    validate_length(response)
    validate_unit_id(request_mbap, response)


def validate_function_code(request, response):
    """ Validate if Function code in request and response equal. """
    assert struct.unpack('>B', request[7:8])[0] == \
        struct.unpack('>B', response[7:8])[0]


def validate_byte_count(request, response):
    """ Check of byte count field contains actual byte count and if byte count
    matches with the amount of requests quantity.
    """
    byte_count = struct.unpack('>B', response[8:9])[0]

    quantity = struct.unpack('>H', request[-2:])[0]
    expected_byte_count = quantity // 8

    if quantity % 8 != 0:
        expected_byte_count = (quantity // 8) + 1

    assert byte_count == len(response[9:])
    assert byte_count == expected_byte_count


def unpack_single_bit_values(response):
    byte_count = struct.unpack('>B', response[8:9])[0]

    fmt = '>' + ('B' * byte_count)
    return struct.unpack(fmt, response[9:])


def test_read_coils_successfully(sock, mbap):
    """ Validate response PDU of a succesful request. """
    function_code, starting_address, quantity = (1, 0, 10)
    adu = mbap + struct.pack('>BHH', function_code, starting_address, quantity)

    sock.send(adu)
    resp = sock.recv(1024)

    validate_response_mbap(mbap, resp)
    validate_function_code(adu, resp)
    validate_byte_count(adu, resp)

    assert unpack_single_bit_values(resp) == (170, 2)


@pytest.mark.parametrize('quantity', [
    0,
    0x07D0 + 1,
])
def test_read_coils_with_invalid_addres(sock, mbap, quantity):
    """ Validate response PDU of request returning excpetion response with
    error code 3.
    """
    function_code, starting_address, quantity = (1, 0, quantity)
    adu = mbap + struct.pack('>BHH', function_code, starting_address, quantity)

    sock.send(adu)
    resp = sock.recv(1024)

    validate_response_mbap(mbap, resp)
    assert struct.unpack('>BB', resp[-2:]) == (0x81, 3)


def test_read_coils_with_invalid_value(sock, mbap):
    """ Validate response PDU of request returning excpetion response with
    error code 2.
    """
    function_code, starting_address, quantity = (1, 9, 2)
    adu = mbap + struct.pack('>BHH', function_code, starting_address, quantity)

    sock.send(adu)
    resp = sock.recv(1024)

    validate_response_mbap(mbap, resp)
    assert struct.unpack('>BB', resp[-2:]) == (0x81, 2)


def test_read_coils_with_server_failure(sock, mbap):
    """ Validate response PDU of request returning excpetion response with
    error code 2.
    """
    function_code, starting_address, quantity = (1, 666, 1)
    adu = mbap + struct.pack('>BHH', function_code, starting_address, quantity)

    sock.send(adu)
    resp = sock.recv(1024)

    validate_response_mbap(mbap, resp)
    assert struct.unpack('>BB', resp[-2:]) == (0x81, 4)
