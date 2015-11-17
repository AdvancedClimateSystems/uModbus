import os


class Config():
    """ Class to hold global configuration. """

    SINGLE_BIT_VALUE_FORMAT_CHARACTER = 'B'
    """ Format character used to (un)pack singlebit values (values used for
    writing from and writing to coils or discrete inputs) from structs.

    .. note:: Its value should not be changed. This attribute exists to be
        consistend with `MULTI_BIT_VALUE_FORMAT_CHARACTER`.
    """

    MULTI_BIT_VALUE_FORMAT_CHARACTER = 'H'
    """ Format character used to (un)pack multibit values (values used for
    writing from and writing to registers) from structs.

    The format character depends on size of the value and whether values are
    signed or unsigned.

    By default multibit values are unsigned and use 16 bits. The default format
    character used for (un)packing structs is 'H'.

    .. note:: Its value should not be set directly. Instead use
        :attr:`MULTI_BIT_VALUE_SIGNED` and :attr:`MULTI_BIT_VALUE_BIT_SIZE` to
        modify this value.

    """
    def __init__(self):
        self.MULTI_BIT_VALUE_SIGNED = os.environ.get('UMODBUS_SIGNED_VALUES',
                                                     False)
        self._set_multi_bit_value_format_character()

    def _set_multi_bit_value_format_character(self):
        """ Set format character for multibit values.

        The format character depends on size of the value and whether values are
        signed or unsigned.

        """
        self.MULTI_BIT_VALUE_FORMAT_CHARACTER = \
            self.MULTI_BIT_VALUE_FORMAT_CHARACTER.upper()

        if self.MULTI_BIT_VALUE_SIGNED:
            self.MULTI_BIT_VALUE_FORMAT_CHARACTER = \
                self.MULTI_BIT_VALUE_FORMAT_CHARACTER.lower()

    @property
    def MULTI_BIT_VALUE_SIGNED(self):
        """ Whether multibit values are signed or not. Default is False.

        This value can be set using the environment variable
        `UMODBUS_SIGNED_VALUES`.
        """
        return self._MULTI_BIT_VALUE_SIGNED

    @MULTI_BIT_VALUE_SIGNED.setter
    def MULTI_BIT_VALUE_SIGNED(self, value):
        """ Set signedness of multibit values.

        This method effects `Config.MULTI_BIT_VALUE_FORMAT_CHARACTER`.
        :param value: Boolean indicting if multibit values are signed or not.
        """
        self._MULTI_BIT_VALUE_SIGNED = value
        self._set_multi_bit_value_format_character()

    @property
    def MULTI_BIT_VALUE_BIT_SIZE(self):
        """ Bit size of multibit values. Default is 16.

        This value can be set using the environment variable
        `UMODBUS_BIT_SIZE`.
        """
        return self._MULTI_BIT_VALUE_BIT_SIZE

    @MULTI_BIT_VALUE_BIT_SIZE.setter
    def MULTI_BIT_VALUE_BIT_SIZE(self, value):
        """ Set bit size of multibit value.

        This method effects `Config.MULTI_BIT_VALUE_FORMAT_CHARACTER`.
        :param value: Number indication bit size.
        """
        self._MULTI_BIT_VALUE_SIGNED = value
        self._set_multi_bit_value_format_character()
