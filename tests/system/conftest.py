import struct
import pytest
import socket
import asyncio
from threading import Thread

from .tcp_server import app as tcp
from .rtu_server import app as rtu, StreamReader, StreamWriter


@pytest.fixture(autouse=True, scope="session")
def tcp_server(request):
    t = Thread(target=tcp.serve_forever)
    t.start()

    def fin():
        tcp.shutdown()
        tcp.server_close()
        t.join()

    request.addfinalizer(fin)
    return tcp


@pytest.yield_fixture
def sock(tcp_server):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(tcp_server.socket.getsockname())

    yield sock

    sock.close()


@pytest.yield_fixture
async def async_tcp_streams(tcp_server):
    host, port = tcp_server.socket.getsockname()
    reader, writer = await asyncio.open_connection(host, port)

    yield reader, writer

    writer.close()
    if hasattr(writer, 'wait_closed'):
        await writer.wait_closed()



@pytest.fixture
def rtu_server():
    return rtu


@pytest.fixture
async def async_serial_streams(rtu_server):
    reader = StreamReader(rtu_server.serial_port)
    writer = StreamWriter(rtu_server.serial_port)
    return reader, writer



@pytest.fixture
def mbap():
    return struct.pack('>HHHB', 0, 0, 6, 1)
