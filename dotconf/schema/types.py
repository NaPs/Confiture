""" Builtin types of dotconf.schema
"""

from dotconf.schema import Type, ValidationError


class Number(Type):

    """ A type representing a number (a float or an integer).
    """

    def validate(self, value):
        if not isinstance(value, int) and not isinstance(value, float):
            raise ValidationError('%r is not a number' % value)
        else:
            return value

    def cast(self, value):
        return float(value)


class Integer(Number):

    """ A type representing an integer in the configuration.

    Example in configuration::

        my_integer = 42
        my_integer = 42.0  # Will also match this type
    """

    def __init__(self):
        super(Integer, self).__init__()

    def validate(self, value):
        value = super(Integer, self).validate(value)
        if int(value) == value:
            return int(value)
        else:
            raise ValidationError('%r is not an integer value' % value)

    def cast(self, value):
        return int(value)


class Float(Number):

    """ A type representing a float in the configuration.

    Example in configuration::

        my_float = 42.2
        my_float = 42  # All values matched by the Integer type also match
                       # for the Float type
    """

    def __init__(self):
        super(Float, self).__init__()

    def validate(self, value):
        value = super(self, Float).validate(value)
        return float(value)


class Boolean(Type):

    """ A type representing a boolean value in the configuration.

    Example in configuration::

        my_boolean = yes
    """

    is_argparse_flag = True

    def __init__(self):
        super(Boolean, self).__init__()

    def validate(self, value):
        if value is not True and value is not False:
            raise ValidationError('%r is not a boolean value' % value)
        return value

    def cast(self, value):
        return bool(value)


class String(Type):

    """ A type representing a string in the configuration.

    :param regex: if provided, the string will be validated to match with the
                  regex

    Example in configuration::

        my_string = "hello, world!"

    """

    def __init__(self, regex=None):
        super(String, self).__init__()
        self._regex = regex

    def validate(self, value):
        return str(value)

    def cast(self, value):
        return value
