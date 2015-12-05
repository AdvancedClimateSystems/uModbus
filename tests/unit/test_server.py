""" The module umodbus.server is mainly covered through system tests. Only
those parts which can't be tested by system tests should be tested using
unit tests.
"""
import pytest

from umodbus.server import RequestHandler


def test_handle_raising_exception():
    """ Test tests RequestHandler.handle() which is called when an instance
    of RequestHandler is created. This method should reraise exception if one
    occurs.
    """
    with pytest.raises(AttributeError):
        RequestHandler(None, None, None)
