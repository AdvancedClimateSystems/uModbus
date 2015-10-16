import struct

from modbus.functions import function_factory, ReadCoils


def test_caching_of_function_factory():
    """ Equal calls to :meth:`function_factory` should return same response.
    """
    function_code = 1
    starting_address = 100
    quantity = 3

    pdu = struct.pack('>BHH', function_code, starting_address, quantity)

    # Call method twice, both with same input...
    function_1 = function_factory(pdu)
    function_2 = function_factory(pdu)

    # ...output should be the same.
    assert id(function_1) == id(function_2)

    starting_address = 101
    pdu = struct.pack('>BHH', function_code, starting_address, quantity)

    # But when called with different pdu...
    function_3 = function_factory(pdu)

    # ...output should not be the same as previous calls.
    assert id(function_1) is not id(function_3)


def test_function_factory_with_read_coils_pdu():
    """ :meth:`function_factory` should return correct instance. """
    function_code = 1
    starting_address = 100
    quantity = 3

    pdu = struct.pack('>BHH', function_code, starting_address, quantity)
    function = function_factory(pdu)

    assert isinstance(function, ReadCoils)
    assert function.function_code == function_code
    assert function.starting_address == starting_address
    assert function.quantity == quantity
