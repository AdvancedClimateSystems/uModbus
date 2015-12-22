import struct
import pytest

from umodbus.client.pdu import (read_coils, read_discrete_inputs,
                                read_holding_registers, read_input_registers)


@pytest.mark.parametrize('function, function_code', [
    (read_coils, 1),
    (read_discrete_inputs, 2),
    (read_holding_registers, 3),
    (read_input_registers, 4)
])
def test_read_methods(function, function_code):
    """ Test if returned PDU's are as expected. """
    starting_address, quantity = (1, 10)
    expected_pdu = struct.pack('>BHH', function_code, starting_address,
                               quantity)

    assert function(starting_address, quantity) == expected_pdu
