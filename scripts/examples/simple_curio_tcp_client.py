#!/usr/bin/env python
# scripts/examples/simple_curio_tcp_client.py
import curio
from argparse import ArgumentParser

from umodbus import conf
from umodbus.client import tcp
from umodbus.client.tcp.asynch import send_message


# Enable values to be signed (default is False).
conf.SIGNED_VALUES = True


class CurioStream:
    """Adapter from curio socket to StreamReader/Writer"""

    def __init__(self, sock):
        self.stream = sock.as_stream()
        self.data = None

    def write(self, data):
        self._data = data

    async def drain(self):
        if self._data:
            await self.stream.write(self._data)
            self._data = None

    async def readexactly(self, n):
        return await self.stream.read_exactly(n)


async def main():
    # Parse command line arguments
    parser = ArgumentParser()
    parser.add_argument("-a", "--address", default="localhost:502")

    args = parser.parse_args()
    if ":" not in args.address:
        args.address += ":502"
    host, port = args.address.rsplit(":", 1)
    port = int(port)

    sock = await curio.open_connection(host, port)
    stream = CurioStream(sock)

    # Returns a message or Application Data Unit (ADU) specific for doing
    # Modbus TCP/IP.
    message = tcp.write_multiple_coils(slave_id=1, starting_address=1, values=[1, 0, 1, 1])

    # Response depends on Modbus function code. This particular returns the
    # amount of coils written, in this case it is.
    response = await send_message(message, stream, stream)

    await sock.close()


curio.run(main)
