import struct
import pytest
import socket
from threading import Thread

from .server import app
from .rtu import app as rtu


@pytest.fixture(autouse=True, scope="session")
def tcp_server(request):
    t = Thread(target=app.serve_forever)
    t.start()

    def fin():
        app.shutdown()
        app.server_close()
        t.join()

    request.addfinalizer(fin)
    return app


@pytest.yield_fixture
def sock(tcp_server):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(tcp_server.socket.getsockname())

    yield sock

    sock.close()


@pytest.fixture
def rtu_server():
    return rtu


@pytest.fixture
def mbap():
    return struct.pack('>HHHB', 0, 0, 6, 1)
