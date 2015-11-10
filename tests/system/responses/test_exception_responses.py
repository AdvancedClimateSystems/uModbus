import pytest
import struct

from ..validators import validate_response_mbap


@pytest.mark.parametrize('function_code, quantity', [
    (1, 0),
    (2, 0),
    (3, 0),
    (4, 0),
    (1, 0x07D0 + 1),
    (2, 0x07D0 + 1),
    (3, 0x007D + 1),
    (4, 0x007D + 1),
])
def test_request_returning_invalid_data_value_error(sock, mbap, function_code,
                                                    quantity):
    """ Validate response PDU of request returning excepetion response with
    error code 3.
    """
    function_code, starting_address, quantity = (function_code, 0, quantity)
    adu = mbap + struct.pack('>BHH', function_code, starting_address, quantity)

    sock.send(adu)
    resp = sock.recv(1024)

    validate_response_mbap(mbap, resp)
    assert struct.unpack('>BB', resp[-2:]) == (0x80 + function_code, 3)


@pytest.mark.parametrize('function_code, adu', [
    (1, struct.pack('>BHH', 1, 9, 2)),
    (2, struct.pack('>BHH', 2, 9, 2)),
    (3, struct.pack('>BHH', 3, 9, 2)),
    (4, struct.pack('>BHH', 4, 9, 2)),
    (5, struct.pack('>BHH', 5, 11, 0xFF00)),
    (6, struct.pack('>BHH', 6, 11, 1337)),
    (15, struct.pack('>BHHBB', 15, 9, 2, 1, 3)),
    (16, struct.pack('>BHHBHH', 16, 9, 2, 4, 1337, 15)),
])
def test_request_returning_invalid_data_address_error(sock, mbap, function_code,
                                                      adu):
    """ Validate response PDU of request returning excepetion response with
    error code 2.
    """
    sock.send(mbap + adu)
    resp = sock.recv(1024)

    validate_response_mbap(mbap, resp)
    assert struct.unpack('>BB', resp[-2:]) == (0x80 + function_code, 2)


@pytest.mark.parametrize('function_code, pdu', [
    (1, struct.pack('>BHH', 1, 666, 1)),
    (2, struct.pack('>BHH', 2, 666, 1)),
    (3, struct.pack('>BHH', 3, 666, 1)),
    (4, struct.pack('>BHH', 4, 666, 1)),
    (5, struct.pack('>BHH', 5, 666, 0)),
    (6, struct.pack('>BHH', 6, 666, 1337)),
    (15, struct.pack('>BHHBB', 15, 666, 1, 1, 1)),
    (16, struct.pack('>BHHHH', 16, 666, 2, 2, 1337)),
])
def test_request_returning_server_device_failure_error(sock, mbap,
                                                       function_code, pdu):
    """ Validate response PDU of request returning excepetion response with
    error code 4.
    """
    sock.send(mbap + pdu)
    resp = sock.recv(1024)

    validate_response_mbap(mbap, resp)
    assert struct.unpack('>BB', resp[-2:]) == (0x80 + function_code, 4)
