""" Builtin types of confiture.schema
"""

import re
import sys
import numbers
import socket
import os.path

if sys.version_info[0] >= 3:
    import urllib.parse as urlparse
else:
    import urlparse

try:
    import ipaddr
except ImportError:
    IPADDR_ENABLED = False
else:
    IPADDR_ENABLED = True

from confiture.schema import Type, ValidationError


class Number(Type):

    """ A type representing a number (a float or an integer).
    """

    def validate(self, value):
        if not isinstance(value, numbers.Number):
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
        value = super(Float, self).validate(value)
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

    def __init__(self, encoding=None):
        super(String, self).__init__()
        self._encoding = encoding

    def validate(self, value):
        if self._encoding is not None:
            value = value.encode(self._encoding)
        return value

    def cast(self, value):
        return value


class _BaseRegex(String):

    """ Base class for regex types.
    """

    def __init__(self, regex, error='value doesn\'t match', **kwargs):
        super(_BaseRegex, self).__init__(**kwargs)
        self._regex = re.compile(regex)
        self._error = error

    def validate(self, value):
        value = super(_BaseRegex, self).validate(value)
        match = self._regex.match(value)
        if match is None:
            raise ValidationError(self._error)
        return match


class Regex(_BaseRegex):

    """ A string based type validated against a regex.
    """

    def validate(self, value):
        value = super(Regex, self).validate(value)
        return value.string


class NamedRegex(_BaseRegex):

    """ A string based type like Regex but returning named groups in dict.
    """

    def validate(self, value):
        value = super(NamedRegex, self).validate(value)
        return value.groupdict()


class RegexPattern(String):

    """ A re Python object.

    :param flags: python re compile `flag <http://docs.python.org/library/re.html#re.compile>`_

    Example in configuration::

        match = '/[a-z]+(-[a-z]+)?\.css'
    """

    def __init__(self, flags=0, **kwargs):
        super(RegexPattern, self).__init__(**kwargs)
        self.flags = flags

    def validate(self, value):
        value = super(RegexPattern, self).validate(value)
        # Try to compile regex object:
        try:
            value = re.compile(value, self.flags)
        except re.error:
            raise ValidationError('Bad format for regular expression')
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

    def __init__(self, version=None, **kwargs):
        if not IPADDR_ENABLED:
            raise RuntimeError('You must install the ipaddr package to use this type')
        super(IPAddress, self).__init__(**kwargs)
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


class IPSocketAddress(String):

    """ A string based type representing an (ip address, port) couple.

    This type return an IPSocketAddress.Address object.

    Example in configuration::

        interface = "0.0.0.0:80"
    """

    def __init__(self, default_addr='127.0.0.1', default_port=None, version=None, **kwargs):
        if not IPADDR_ENABLED:
            raise RuntimeError('You must install the ipaddr package to use this type')
        self._default_addr = default_addr
        self._default_port = default_port
        self._version = version
        super(IPSocketAddress, self).__init__(**kwargs)

    def validate(self, value):
        raw_addr, _, raw_port = value.partition(':')
        if not raw_addr:
            raw_addr = self._default_addr
        if not raw_port:
            if self._default_port is None:
                raise ValidationError('You must specify a port')
            else:
                raw_port = self._default_port

        try:
            addr = ipaddr.IPAddress(raw_addr, version=self._version)
        except (ValueError, ipaddr.AddressValueError) as err:
            raise ValidationError(str(err))

        try:
            port = int(raw_port)
        except ValueError:
            raise ValidationError('%r is not a port (not an integer)' % raw_port)
        if not 1 <= port <= 65535:
            raise ValidationError('%r is not a port (not in 1 - 65535 range)' % port)

        return self.Address(addr, port)

    class Address(object):

        def __init__(self, addr, port):
            self.addr = addr
            self.port = port

        def __repr__(self):
            return 'IPSocketAddress.Address(%s:%s)' % (self.addr, self.port)

        def to_tuple(self):
            return (str(self.addr), self.port)

        def _create_socket(self, type):
            if self.addr.version == 4:
                family = socket.AF_INET
            else:
                family = socket.AF_INET6
            return socket.socket(family, type)

        def to_listening_socket(self, type):
            sock = self._create_socket(type)
            sock.listen(self.to_tuple())
            return sock

        def to_socket(self, type):
            sock = self._create_socket(type)
            sock.connect(self.to_tuple())
            return sock

        def to_listening_tcp_socket(self):
            return self.to_listening_socket(socket.SOCK_STREAM)

        def to_listening_udp_socket(self):
            return self.to_listening_socket(socket.SOCK_DGRAM)

        def to_tcp_socket(self):
            return self.to_socket(socket.SOCK_STREAM)

        def to_udp_socket(self):
            return self.to_socket(socket.SOCK_DGRAM)


class Eval(String):

    """ A string base type evaluating string as Python expression.

    Example in configuration::

        sum = 'sum(range(3, 10))'

    .. warning::
        This type can be dangerous since any Python expression can be typed
        by the user, like __import__("sys").exit(). Use it at your own risk.
    """

    def __init__(self, locals=None, globals=None, **kwargs):
        super(Eval, self).__init__(**kwargs)
        if locals is None:
            self._locals = {}
        else:
            self._locals = locals
        if globals is None:
            self._globals = {}
        else:
            self._globals = globals

    def validate(self, value):
        value = super(Eval, self).validate(value)
        try:
            return eval(value, self._globals, self._locals)
        except Exception as err:
            raise ValidationError('Bad expression: %s' % err)


class Path(String):

    """ A string representing a filesystem path.

    It will expand '~' to user home directory and return an absolute path if
    you provide a relative path (this is usefull if you change the working
    directory of a process after configuration parsing).
    """

    def validate(self, value):
        value = super(Path, self).validate(value)
        return os.path.abspath(os.path.expanduser(value))
