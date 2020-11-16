#!/usr/bin/env python
# scripts/examples/simple_async_tcp_client.py
import asyncio

from umodbus import conf
from umodbus.client import tcp
from umodbus.client.asynch import send_message


# Enable values to be signed (default is False).
conf.SIGNED_VALUES = True


async def main():
    reader, writer = await asyncio.open_connection('localhost', 502)

    # Returns a message or Application Data Unit (ADU) specific for doing
    # Modbus TCP/IP.
    message = tcp.write_multiple_coils(slave_id=1, starting_address=1, values=[1, 0, 1, 1])

    # Response depends on Modbus function code. This particular returns the
    # amount of coils written, in this case it is.
    response = await send_message(message, reader, writer)

    writer.close()
    await writer.wait_closed()


asyncio.run(main())
