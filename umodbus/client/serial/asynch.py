"""
Async I/O. Send ModBus RTU message over any asynchonous communication
transport.
"""

from .rtu import (
    raise_for_exception_adu,
    expected_response_pdu_size_from_request_pdu,
    parse_response_adu,
)


async def send_message(adu, reader, writer):
    """ Send ADU over asyncio reader/writer and return parsed response.

    :param adu: Request ADU.
    :param reader: stream reader (ex: serial_asyncio.StreamReader)
    :param writer: stream writer (ex: serial_asyncio.StreamWriter)
    :return: Parsed response from server.
    """
    writer.write(adu)
    await writer.drain()

    # Check exception ADU (which is shorter than all other responses) first.
    exception_adu_size = 5
    response_error_adu = await reader.readexactly(exception_adu_size)
    raise_for_exception_adu(response_error_adu)

    expected_response_size = expected_response_pdu_size_from_request_pdu(adu[1:-2]) + 3
    response_remainder = await reader.readexactly(
        expected_response_size - exception_adu_size
    )

    return parse_response_adu(response_error_adu + response_remainder, adu)
