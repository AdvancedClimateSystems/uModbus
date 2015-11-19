class TestConfig:
    def test_defaults(self, config):
        """ Test whether defaults configuration values are correct. """
        assert config.SINGLE_BIT_VALUE_FORMAT_CHARACTER == 'B'
        assert config.MULTI_BIT_VALUE_FORMAT_CHARACTER == 'H'
        assert not config.SIGNED_VALUES

    def test_multi_bit_value_signed(self, config):
        """  Test if MULTI_BIT_VALUE_FORMAT_CHARACTER changes when setting
        signedness.
        """
        assert config.MULTI_BIT_VALUE_FORMAT_CHARACTER == 'H'
        config.SIGNED_VALUES = True
        assert config.MULTI_BIT_VALUE_FORMAT_CHARACTER == 'h'
