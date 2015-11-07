import sys
import struct
import logging
from logging import StreamHandler, Formatter
from functools import wraps

from umodbus import log


def log_to_stream(stream=sys.stdout, level=logging.WARNING,
                  fmt=logging.BASIC_FORMAT):
    """ Add :class:`logging.StreamHandler` to logger which logs to a stream.

    :param stream. Stream to log to, default STDOUT.
    :param level: Log level, default WARNING.
    :param fmt: String with log format, default is BASIC_FORMAT.
    """
    fmt = Formatter(fmt)
    handler = StreamHandler()
    handler.setFormatter(fmt)

    log.setLevel(level)
    log.addHandler(handler)


def unpack_mbap(mbap):
    """ Parse MBAP of 7 bytes and return tuple with fields.

        >>> parse_mbap(b'\x00\x08\x00\x00\x00\x06\x01')
        (8, 0, 6, 1)

    :param mbap: Array of 7 bytes.
    :return: Tuple with 4 values: Transaction identifier,  Protocol identifier,
        Length and Unit identifier.
    """
    # '>' indicates data is big-endian. Modbus uses this alignment. 'H' and 'B'
    # are format characters. 'H' is unsigned short of 2 bytes. 'B' is an
    # unsigned char of 1 byte.  HHHB sums up to 2 + 2 + 2 + 1 = 7 bytes.

    # TODO What it right exception to raise? Error code 04, Server failure,
    # seems most appropriate.
    return struct.unpack('>HHHB', mbap)


def pack_mbap(transaction_id, protocol_id, length, unit_id):
    """ Create and return response MBAP.

    :param transaction_id: Transaction id.
    :param protocol_id: Protocol id.
    :param length: Length of following bytes in ADU.
    :param unit_id: Unit id.
    :return: Byte array of 7 bytes.
    """
    return struct.pack('>HHHB', transaction_id, protocol_id, length, unit_id)


def memoize(f):
    """ Decorator which caches function's return value each it is called.
    If called later with same arguments, the cached value is returned.
    """
    cache = {}

    @wraps(f)
    def inner(arg):
        if arg not in cache:
            cache[arg] = f(arg)
        return cache[arg]
    return inner


def integer_to_binary_list(n):
    """ Convert number to list representing number in binary.

        >>> integer_to_binary_list(10)
        [1, 0, 1, 0]

    :param n: Number.
    :return: List with zeroes and ones.
    """
    return [int(x) for x in bin(n)[2:]]
