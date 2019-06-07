#!/usr/bin/env python
# scripts/example/simple_rtu_client.py
import fcntl
import struct
from serial import Serial, PARITY_NONE

from umodbus.client.serial import rtu


def get_serial_port():
    """ Return serial.Serial instance, ready to use for RS485."""
    port = Serial(port='/dev/ttyS1', baudrate=9600, parity=PARITY_NONE,
                  stopbits=1, bytesize=8, timeout=1)

    fh = port.fileno()

    # A struct with configuration for serial port.
    serial_rs485 = struct.pack('hhhhhhhh', 1, 0, 0, 0, 0, 0, 0, 0)
    fcntl.ioctl(fh, 0x542F, serial_rs485)

    return port

serial_port = get_serial_port()

# Returns a message or Application Data Unit (ADU) specific for doing
# Modbus RTU.
message = rtu.write_multiple_coils(slave_id=1, address=1, values=[1, 0, 1, 1])

# Response depends on Modbus function code. This particular returns the
# amount of coils written, in this case it is.
response = rtu.send_message(message, serial_port)

serial_port.close()
