from umodbus.utils import unpack_mbap, pack_mbap


def test_unpack_mbap():
    """ MBAP should contain correct values for Transaction identifier, Protocol
    identifier, Length and Unit identifer.
    """
    assert unpack_mbap(b'\x00\x08\x00\x00\x00\x06\x01') == (8, 0, 6, 1)


def test_pack_mbap():
    """ Byte array should contain correct encoding of Transaction identifier,
    Protocol identifier, Length and Unit identifier.
    """
    assert pack_mbap(8, 0, 6, 1) == b'\x00\x08\x00\x00\x00\x06\x01'
