import struct
import pytest

from umodbus.client.serial.redundancy_check import (get_crc, validate_crc,
                                                    CRCError)


def test_get_crc():
    """ Test if correct CRC is calculated. """
    # Values are equal to those used in example in MODBUS over serial line
    # specification and implementation guide V1.02, chapter 6.2.2.
    assert struct.unpack('<H', get_crc(b'\x02\x07')) ==\
        struct.unpack('<H', b'\x41\x12')


def test_validate_valid_crc():
    """" Method should not raise assertion error. """
    validate_crc(b'\x02\x07', b'\x41\x12')


def test_validate_invalid_crc():
    """" Method should raise assertion error. """
    with pytest.raises(CRCError):
        validate_crc(b'\x02\x07', b'\x41\x11')
