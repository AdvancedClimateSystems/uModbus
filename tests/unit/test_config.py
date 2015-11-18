class TestConfig:

    def test_defaults(self, config):
        assert config.SINGLE_BIT_VALUE_FORMAT_CHARACTER == 'B'
        assert config.MULTI_BIT_VALUE_FORMAT_CHARACTER == 'H'
        assert not config.MULTI_BIT_VALUE_SIGNED

    def test_multi_bit_value_signed(self, config):
        assert config.MULTI_BIT_VALUE_FORMAT_CHARACTER == 'H'
        config.MULTI_BIT_VALUE_SIGNED = True
        assert config.MULTI_BIT_VALUE_FORMAT_CHARACTER == 'h'
