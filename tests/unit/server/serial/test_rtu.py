from umodbus.server.serial.rtu import RTUServer


class test_rtu_server_create_response_adu():
    server = RTUServer()
    assert server.create_response_adu({'unit_id': 1}, b'') == \
            b'\x01~\x80'
