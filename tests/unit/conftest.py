import pytest

from umodbus.config import Config


@pytest.fixture
def config():
    return Config()
