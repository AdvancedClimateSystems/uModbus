""" The module umodbus.server is mainly covered through system tests. Only
those parts which can't be tested by system tests should be tested using
unit tests.
"""
import struct
import pytest

from umodbus.exceptions import ServerDeviceFailureError
from umodbus.client.tcp import read_coils
from umodbus.server.tcp import RequestHandler


@pytest.fixture
def meta_data():
    return {
        'transaction_id': 1337,
        'protocol_id': 0,
        'length': 1,
        'unit_id': 5,
    }


@pytest.fixture
def mbap_header():
    transaction_id = 1337
    protocol_id = 0
    length = 1
    unit_id = 5

    return struct.pack('>HHHB', transaction_id, protocol_id, length, unit_id)


@pytest.fixture
def request_handler(monkeypatch):
    # handle() is called when after creating a RequestHandler. This
    # causes an error because it wants to read from a socket. Mock it out so
    # this error doesn't occur.
    monkeypatch.setattr(RequestHandler, 'handle', lambda _: None)
    return RequestHandler(None, None, None)


def test_handle_raising_exception():
    """ Test tests RequestHandler.handle() which is called when an instance
    of RequestHandler is created. This method should reraise exception if one
    occurs.
    """
    with pytest.raises(AttributeError):
        RequestHandler(None, None, None)


def test_request_handler_get_meta_data(request_handler, mbap_header,
                                       meta_data):
    assert request_handler.get_meta_data(mbap_header) == meta_data


def test_request_handler_get_meta_data_raising_error(request_handler):
    with pytest.raises(ServerDeviceFailureError):
        request_handler.get_meta_data('')


def def_test_get_request_pdu(request_handler, mbap_header):
    pdu = read_coils(1, 1, 1)
    assert request_handler.get_request_pdu(mbap_header + pdu) == pdu


def test_response_adu(request_handler, mbap_header, meta_data):
    assert len(request_handler.create_response_adu(meta_data, '')) == 7
