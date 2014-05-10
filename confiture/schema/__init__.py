""" Confiture schema validator.
"""


class ValidationError(Exception):

    """ Exception raised for a schema validation error.
    """

    def __init__(self, msg, position=None):
        super(ValidationError, self).__init__(msg)
        self.position = position


class Container(object):

    """ Base class for all containers.
    """

    def populate_argparse(self, parser, name=None):
        pass

    def validate(self, value):
        raise NotImplementedError()


class ArgparseContainer(Container):

    """ A container which support argparse override.
    """

    def __init__(self, argparse_names=None, argparse_metavar=None,
                 argparse_help=None, argparse_names_invert=None,
                 argparse_help_invert=None):
        self._argparse_names = argparse_names
        self._argparse_value = None  # Where to store the overriding value
        self._argparse_metavar = argparse_metavar
        self._argparse_help = argparse_help
        self._argparse_names_invert = argparse_names_invert
        self._argparse_help_invert = argparse_help_invert


class Type(object):

    """ Base class for all types.
    """

    is_argparse_flag = False  # If True, this type will be defined as a
                              # boolean "flag" by argument parser.

    def validate(self, value):
        raise NotImplementedError()

    def cast(self, value):
        return value
