""" Returns PDU for Modbus requests send over a serial line in RTU mode. """
import struct

from umodbus.client import pdu


def read_holding_registers(slave_id, starting_address, quantity):
    return struct.pack('>B', slave_id) + \
        pdu.read_holding_registers(starting_address, quantity)
