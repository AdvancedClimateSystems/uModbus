import struct

from umodbus.client.tcp import (create_request_adu, create_mbap_header,
                                read_discrete_inputs, read_holding_registers,
                                read_input_registers)


def validate_mbap_fields(mbap, slave_id, pdu):
    """ Check if fields in MBAP header contain expected values. """
    transaction_id = struct.unpack('>H', mbap[:2])[0]
    protocol_id = struct.unpack('>H', mbap[2:4])[0]
    length = struct.unpack('>H', mbap[4:6])[0]
    unit_id = struct.unpack('>B', mbap[6:])[0]

    assert len(mbap) == 7
    assert 0 <= transaction_id <= 65536
    assert protocol_id == 0
    assert length == len(pdu) + 1
    assert unit_id == slave_id


def test_create_request_adu():
    """ Validate MBAP header of ADU and check if ADU contains correct PDU. """
    pdu = b'\x01'
    slave_id = 1
    adu = create_request_adu(slave_id, pdu)

    # 9 is length MBAP (7 bytes) with length of PDU (1 byte)
    assert len(adu) == 8
    assert adu[7:] == pdu
    validate_mbap_fields(adu[:7], slave_id, pdu)


def test_create_mbap_header():
    """ Validate fields of MBAP header. """
    pdu = b'\x01x02'
    slave_id = 1
    mbap = create_mbap_header(slave_id, pdu)

    validate_mbap_fields(mbap, slave_id, pdu)
