import pytest
import socket
import struct
from threading import Thread

from .server import app


@pytest.fixture(autouse=True, scope="module")
def server(request):
    t = Thread(target=app.serve_forever)
    t.start()

    def fin():
        app.shutdown()
        app.server_close()
        t.join()

    request.addfinalizer(fin)
    return app


@pytest.yield_fixture
def sock(server):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server.socket.getsockname())

    yield sock

    sock.close()


@pytest.fixture
def mbap():
    return struct.pack('>HHHB', 0, 0, 6, 1)
