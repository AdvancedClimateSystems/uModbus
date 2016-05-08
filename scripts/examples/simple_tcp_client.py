#!/usr/bin/env python
# scripts/examples/simple_tcp_client.py
import socket

from umodbus.client import tcp


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 502))

# Returns a message or Application Data Unit (ADU) specific for doing
# Modbus TCP/IP.
message = tcp.write_multiple_coils(slave_id=1, address=1, values=[1, 0, 1, 1])

# Response depends on Modbus function code. This particular returns the
# amount of coils written, in this case it isr3.
response = tcp.send_message(message, sock)

sock.close()
