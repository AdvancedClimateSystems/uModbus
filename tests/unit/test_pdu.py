import struct
import pytest

from umodbus.client import pdu


@pytest.mark.parametrize('function, function_code', [
    (pdu.read_coils, 1),
    (pdu.read_discrete_inputs, 2),
    (pdu.read_holding_registers, 3),
    (pdu.read_input_registers, 4)
])
def test_read_methods(function, function_code):
    """ Test if returned PDU's are as expected. """
    starting_address, quantity = (1, 10)
    expected_pdu = struct.pack('>BHH', function_code, starting_address,
                               quantity)

    assert function(starting_address, quantity) == expected_pdu


@pytest.mark.parametrize('value, expected_value', [
    (0, 0),
    (1, 0xFF00),
    (2, 0xFF00),
])
def test_write_single_coil(value, expected_value):
    """ Test if returned PDU is as expected. """
    function_code, address = (5, 0)

    expected_pdu = struct.pack('>BHH', function_code, address,
                               expected_value)

    assert pdu.write_single_coil(address, value) == expected_pdu


def test_write_single_register():
    """ Test if returned PDU is as expected. """
    function_code, address, value = (6, 0, 1337)

    expected_pdu = struct.pack('>BHH', function_code, address, value)

    assert pdu.write_single_register(address, value) == expected_pdu


@pytest.mark.parametrize('values, expected_values', [
    ([1, 1, 0, 1], [11]),
    ([1, 1, 0, 0, 0, 0, 0, 0, 1], [3, 1]),
])
def test_write_mulitple_coils(values, expected_values):
    """ Test if returned PDU is as expected. """
    function_code, starting_address, quantity, byte_count = \
        (15, 0, len(values), len(expected_values))

    fmt = '>BHHB' + ('B' * byte_count)

    expected_pdu = struct.pack(fmt, function_code, starting_address, quantity,
                               byte_count, *expected_values)

    assert pdu.write_multiple_coils(starting_address, values) == \
        expected_pdu


def test_write_multiple_registers():
    """ Test if returned PDU is as expected. """
    values = [1337, 18]
    function_code, starting_address, quantity, byte_count = \
        (16, 0, len(values), 4)

    fmt = '>BHHBHH'

    expected_pdu = struct.pack(fmt, function_code, starting_address, quantity,
                               byte_count, *values)

    assert pdu.write_multiple_registers(starting_address, values) == \
        expected_pdu

