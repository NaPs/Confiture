""" Classes used to represent the configuration tree.
"""


from itertools import chain
from collections import defaultdict


class Position(object):

    """ Position of a statement in a file.
    """

    def __init__(self, file_, lineno, pos):
        self.file = file_
        self.lineno = lineno
        self.pos = pos

    def __repr__(self):
        return '<Position file=%s lineno=%s pos=%s>' % (self.file, self.lineno, self.pos)

    def __str__(self):
        return 'in %s, line %d, position %d' % (self.file, self.lineno, self.pos)

class ConfigValue(object):

    """ Represent a value in the configuration.
    """

    def __init__(self, name, value, position=Position('?', 0, 0)):
        self._name = name
        self._value = value
        self._position = position

    def __repr__(self):
        return '<ConfigValue %r (%s)>' % (self._value, self._position)

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def position(self):
        return self._position


class ConfigSection(object):

    """ Represent a (sub-)section of the configuration.

    :param name: the name of the section (or __top__ for top section)
    :param parent: the parent section (or None for top section)
    :param position: the position of the section in configuration
    """

    def __init__(self, name, parent=None, args=None, position=Position('?', 0, 0)):
        self._name = name
        self._parent = parent
        self._args = args
        self._position = position
        self._subsections = defaultdict(lambda: [])
        self._values = {}

    def __repr__(self):
        return "<Section '%s'>" % self.name

    def __contains__(self, name):
        return name in self._values or name in self._subsections

    #
    # Public API -- Tree construction methods
    #   These methods are intended as internal usage for the configuration
    #   tree construction by the parser or the schema system.
    #

    def register(self, child, name=None):
        """ Register a child on this section.

        :param child: ConfigValue or ConfigSection object to register
        """
        if name is None:
            name = child.name
        if isinstance(child, ConfigValue):
            if name in self:
                raise KeyError('A child with this name already exists')
            self._values[name] = child
        elif isinstance(child, ConfigSection):
            if name in self._values:
                raise KeyError('A child with this name already exists')
            self._subsections[name].append(child)
        else:
            raise TypeError('Child must be a ConfigValue or ConfigSection object')

    def iterchildren(self):
        """ Iterate over all children of this section.

        ..note::

            This is used for the include feature of parser.
        """

        return chain(self._values.itervalues(), self._subsections.itervalues())

    def iteritems(self):
        """ Like :meth:``iterchildren`` but return a couple (key, child).
        """

        return chain(self._values.iteritems(), self._subsections.iteritems())

    #
    # Public API -- User methods
    #   These methods are intended for configuration tree traversal by user.
    #

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @property
    def args(self):
        return self._args

    @property
    def position(self):
        return self._position

    def subsections(self, name):
        """ Iterate over sub-sections with the specified name.
        """
        return iter(self._subsections[name])

    def get(self, name, default=None, raw=True):
        """ Get the value with the specified name or return default.

        :param default: the default value to return if the name is not found
        :param raw: get the ConfigValue object instead of raw value

        .. note::
           If the default value is returned, the raw option is implicitly
           enabled.
        """
        value = self._values.get(name, default)
        if value is not default and raw:
            value = value.value
        return value

    def to_dict(self):
        """ Represent the section (and subsections) as a dict.
        """
        output = {}
        for name, subsections in self._subsections.iteritems():
            output[name] = []
            for subsection in subsections:
                output[name].append(subsection.to_dict())
        for name, value in self._values.iteritems():
            output[name] = value.value
        return output
