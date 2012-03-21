""" Dotconf schema validator.
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

    def validate(self, value):
        raise NotImplementedError()


class Type(object):

    """ Base class for all types.
    """

    def validate(self, value):
        raise NotImplementedError()
