import struct


def unpack_mbap(mbap):
    """ Parse MBAP of 7 bytes and return tuple with fields.

        >>> parse_mbap(b'\x00\x08\x00\x00\x00\x06\x01')
        (8, 0, 6, 1)

    :param mbap: Array of bytes.
    :return: Tuple with 4 values: Transaction identifier,  Protocol identifier,
        Length and Unit identifier.
    """
    # '>' indicates data is big-endian. Modbus uses this alignment. 'H' and 'B'
    # are format characters. 'H' is unsigned short of 2 bytes. 'B' is an
    # unsigned char of 1 byte.  HHHB sums up to 2 + 2 + 2 + 1 = 7 bytes.

    # TODO What it right exception to raise? Error code 04, Server failure,
    # seems most appropriate.
    return struct.unpack('>HHHB', mbap)
