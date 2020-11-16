#!/usr/bin/env python
# scripts/examples/simple_async_tcp_client.py
import asyncio
from argparse import ArgumentParser

from umodbus import conf
from umodbus.client import tcp
from umodbus.client.tcp.asynch import send_message


# Enable values to be signed (default is False).
conf.SIGNED_VALUES = True


async def main():
    # Parse command line arguments
    parser = ArgumentParser()
    parser.add_argument("-a", "--address", default="localhost:502")

    args = parser.parse_args()
    if ":" not in args.address:
        args.address += ":502"
    host, port = args.address.rsplit(":", 1)
    port = int(port)

    reader, writer = await asyncio.open_connection(host, port)

    # Returns a message or Application Data Unit (ADU) specific for doing
    # Modbus TCP/IP.
    message = tcp.write_multiple_coils(slave_id=1, starting_address=1, values=[1, 0, 1, 1])

    # Response depends on Modbus function code. This particular returns the
    # amount of coils written, in this case it is.
    response = await send_message(message, reader, writer)

    writer.close()
    await writer.wait_closed()


asyncio.run(main())
