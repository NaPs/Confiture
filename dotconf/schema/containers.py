""" Builtin containers of dotconf.schema
"""

from dotconf.tree import ConfigSection, ConfigValue
from dotconf.schema import Container, ValidationError


required = object()
many = (1, None)
once = (1, 1)


class Value(Container):

    """ A value container used to store a scalar value of specified type.

    :param value_type: the type of the value stored by container
    :param default: the default value of the container
    """

    def __init__(self, value_type, default=required):
        self._type = value_type
        self._default = default

    def validate(self, value):
        if value is None:
            if self._default is required:
                raise ValidationError('This value is required')
            else:
                return ConfigValue(None, self._default)
        else:
            try:
                validated_value = self._type.validate(value.value)
            except ValidationError as err:
                raise ValidationError(str(err), position=value.position)
            return ConfigValue(value.name, validated_value, position=value.position)


class List(Container):

    """ A list container used to store a list of scalar value of specified type.

    :param values_type: type of values
    :param default: the default value of the container
    """

    def __init__(self, values_type, default=required):
        self._type = values_type
        self._default = default

    def validate(self, value):
        if value is None:
            if self._default is required:
                raise ValidationError('This value is required')
            else:
                return ConfigValue(None, self._default)
        else:
            values = value.value
            if not isinstance(values, list):
                values = [values]
            validated_list = []
            for i, item in enumerate(values):
                try:
                    item = self._type.validate(item)
                except ValidationError as err:
                    raise ValidationError('item #%d, %s' % (i, err),
                                          position=value.position)
                else:
                    validated_list.append(item)
            return ConfigValue(value.name, validated_list, position=value.position)


class Section(Container):

    """ A section container used to store a mapping between name and other
        containers.

        :param \*\*kwargs: parameters used to override meta
    """

    # Defaults meta:
    _meta = {'args': None,
             'unique': False,
             'repeat': once,
             'allow_unknown': False}

    def __init__(self, **kwargs):
        self.meta = {}
        self.keys = {}
        for cls in reversed(self.__class__.mro()):
            # Update meta from class:
            if hasattr(cls, '_meta'):
                self.meta.update(cls._meta)
            # Update fields from class:
            for key, value in cls.__dict__.iteritems():
                if isinstance(value, Container):
                    self.keys[key] = value

    def add(self, name, container):
        """ Add a new key imperatively.

        :param name: the key name to add
        :param container: the container to add
        """

        if name not in self.keys:
            self.keys[name] = container
        else:
            raise KeyError('key already exists')

    def validate(self, section):
        if not isinstance(section, ConfigSection):
            raise ValidationError('Not a section')

        # Rebuild the section using schema:
        validated_section = ConfigSection(section.name, section.parent,
                                          position=section.position)
        #TODO: validate the argument
        for name, container in self.keys.iteritems():
            if isinstance(container, Section):
                # Validate subsections of this section:
                subsections = list(section.subsections(name))
                # Check for repeat option:
                rmin, rmax = container.meta['repeat']
                if rmax is not None and rmin > rmax:
                    raise ValidationError('section %s, rmin > rmax' % name)
                if len(subsections) < rmin:
                    raise ValidationError('section %s, section must be defined'
                                          ' at least %d times' % (name, rmin))
                if rmax is not None and len(subsections) > rmax:
                    raise ValidationError('section %s, section must be defined'
                                          ' at max %d times' % (name, rmax))
                # Do the children validation:
                args = set()  # Store the already seen args
                for subsection in subsections:
                    # Check for unique option:
                    if container.meta['unique']:
                        if tuple(subsection.args) in args:
                            msg = 'section %s, section must be unique' % name
                            raise ValidationError(msg, position=subsection.position)
                        else:
                            args.add(tuple(subsection.args))
                    # Container validation:
                    validated_subsection = container.validate(subsection)
                    validated_section.register(validated_subsection, name=name)
            elif isinstance(container, Container):
                # Validate all other types of containers:
                try:
                    validated_value = container.validate(section.get(name, raw=False))
                except ValidationError as err:
                    raise ValidationError('section %s, %s' % (section.name, err),
                                          position=err.position)
                else:
                    validated_section.register(validated_value, name=name)
        #TODO: Handle the allow_unknown meta option
        return validated_section
