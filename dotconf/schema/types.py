""" Builtin types of dotconf.schema
"""

import re
import urlparse

try:
    import ipaddr
except ImportError:
    IPADDR_ENABLED = False
else:
    IPADDR_ENABLED = True

from dotconf.schema import Type, ValidationError


class Number(Type):

    """ A type representing a number (a float or an integer).
    """

    def validate(self, value):
        if not isinstance(value, int) and not isinstance(value, float) \
            and not isinstance(value, long):
            raise ValidationError('%r is not a number' % value)
        else:
            return value

    def cast(self, value):
        return float(value)


class Integer(Number):

    """ A type representing an integer in the configuration.

    :param min: define the minimum acceptable value value of the integer
    :param max: define the maximum acceptable value value of the integer

    Example in configuration::

        my_integer = 42
        my_integer = 42.0  # Will also match this type
    """

    def __init__(self, min=None, max=None):
        super(Integer, self).__init__()
        self._min = min
        self._max = max

    def validate(self, value):
        value = super(Integer, self).validate(value)
        if int(value) == value:
            value = int(value)
            if self._min is not None and value < self._min:
                raise ValidationError('%r is lower than the minimum (%d)'
                                      % (value, self._min))
            elif self._max is not None and value > self._max:
                raise ValidationError('%r is greater than the maximum (%d)'
                                      % (value, self._max))
            return value
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

    Example in configuration::

        my_string = "hello, world!"

    """

    def __init__(self):
        super(String, self).__init__()

    def validate(self, value):
        return str(value)

    def cast(self, value):
        return value


class Regex(String):

    """ A string base type validated against a regex.
    """

    def __init__(self, regex, error='value doesn\'t match'):
        super(String, self).__init__()
        self._regex = re.compile(regex)
        self._error = error

    def validate(self, value):
        value = super(Regex, self).validate(value)
        if not self._regex.match(value):
            raise ValidationError(self._error)
        return value


class IPAddress(String):

    """ A string based type representing an ipv4 or ipv6 address.

    This type require the "ipaddr" package to work and will return an
    :class:`ipaddr.IPAddress` object.

    :param version: type or ip address to validate, can be 4 (ipv4 addresses
        only), 6 (ipv6 addresses only), or None (both).

    Example in configuration::

        interface = "127.0.0.1"
    """

    def __init__(self, version=None):
        if not IPADDR_ENABLED:
            raise
        super(IPAddress, self).__init__()
        self._version = version

    def validate(self, value):
        try:
            return ipaddr.IPAddress(value, version=self._version)
        except (ValueError, ipaddr.AddressValueError) as err:
            raise ValidationError(str(err))


class IPNetwork(IPAddress):

    """ A string based type representing an ipv4 or ipv6 network.

    This type require the "ipaddr" package to work and will return an
    :class:`ipaddr.IPNetwork` object.

    :param version: type or ip address to validate, can be 4 (ipv4 addresses
        only), 6 (ipv6 addresses only), or None (both).

    Example in configuration::

        allow = "10.0.0.0/8"
    """

    def validate(self, value):
        try:
            return ipaddr.IPNetwork(value, version=self._version)
        except ipaddr.AddressValueError:
            raise ValidationError('%r does not appear to be an IPv%s address'
                                  % (value, self._version))
        except ValueError as err:
            raise ValidationError(str(err))


class Url(String):

    """ A string based type representing an URL.

    This type return an urlparse.ParseResult object.

    Example in configuration::

        proxy = "http://proxy:3128"
    """

    def validate(self, value):
        try:
            return urlparse.urlparse(value)
        except ValueError as err:
            raise ValidationError(str(err))
