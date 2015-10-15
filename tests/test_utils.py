from modbus.utils import unpack_mbap


def test_unpack_mbap():
    """ MBAP should contain correct values for Transaction identifier, Protocol
    identifier, Length and Unit identifer.
    """
    assert unpack_mbap(b'\x00\x08\x00\x00\x00\x06\x01') ==\
        (8, 0, 6, 1)
