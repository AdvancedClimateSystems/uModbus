#!/usr/bin/env python
# scripts/examples/simple_tcp_client.py
from argparse import ArgumentParser
from socket import create_connection

from umodbus import conf
from umodbus.client import tcp

# Enable values to be signed (default is False).
conf.SIGNED_VALUES = True

# Parse command line arguments
parser = ArgumentParser()
parser.add_argument("-a", "--address", default="localhost:502")

args = parser.parse_args()
if ":" not in args.address:
    args.address += ":502"
host, port = args.address.rsplit(":", 1)
port = int(port)

# Returns a message or Application Data Unit (ADU) specific for doing
# Modbus TCP/IP.
message = tcp.write_multiple_coils(slave_id=1, starting_address=1, values=[1, 0, 1, 1])

with create_connection((host, port)) as sock:
    # Response depends on Modbus function code. This particular returns the
    # amount of coils written, in this case it is.
    response = tcp.send_message(message, sock)
