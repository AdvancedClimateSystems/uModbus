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


def validate_response_error(resp, function_code, error_code):
    assert struct.unpack('>BB', resp[-2:]) == \
        (0x80 + function_code, error_code)


def validate_function_code(request, response):
    """ Validate if Function code in request and response equal. """
    assert struct.unpack('>B', request[7:8])[0] == \
        struct.unpack('>B', response[7:8])[0]


def validate_single_bit_value_byte_count(request, response):
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


def validate_multi_bit_value_byte_count(request, response):
    """ Check of byte count field contains actual byte count and if byte count
    matches with the amount of requests quantity.
    """
    byte_count = struct.unpack('>B', response[8:9])[0]

    quantity = struct.unpack('>H', request[-2:])[0]
    expected_byte_count = quantity * 2

    assert byte_count == len(response[9:])
    assert byte_count == expected_byte_count
