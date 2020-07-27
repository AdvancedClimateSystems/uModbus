import pytest

from umodbus.route import DataRule


endpoint = lambda slave_id, function_code, address: 0


def test_basic_route():
    rule = DataRule(endpoint, slave_ids=[1], function_codes=[1], addresses=[1])
    assert rule.match(slave_id=1, function_code=1, address=1)
    assert not rule.match(slave_id=0, function_code=1, address=1)
    assert not rule.match(slave_id=1, function_code=0, address=1)
    assert not rule.match(slave_id=1, function_code=1, address=0)


def test_other_iterables():
    # Other iterable types should work, not just lists
    rule = DataRule(endpoint,
                    slave_ids=set([1]), function_codes=[1], addresses=[1])
    assert rule.match(slave_id=1, function_code=1, address=1)


def test_wildcard_slave_id():
    rule = DataRule(endpoint, slave_ids=None, function_codes=[1], addresses=[1])
    assert rule.match(slave_id=1, function_code=1, address=1)


def test_wildcard_function_code():
    rule = DataRule(endpoint, slave_ids=[1], function_codes=None, addresses=[1])
    assert rule.match(slave_id=1, function_code=1, address=1)


def test_wildcard_address():
    rule = DataRule(endpoint, slave_ids=[1], function_codes=[1], addresses=None)
    assert rule.match(slave_id=1, function_code=1, address=1)
