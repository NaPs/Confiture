""" Builtin containers of dotconf.schema
"""

try:
    import argparse
except ImportError:
    argparse = None

from dotconf.tree import ConfigSection, ConfigValue
from dotconf.schema import Container, ArgparseContainer, ValidationError


required = object()
many = (1, None)
once = (1, 1)


class Value(ArgparseContainer):

    """ A value container used to store a scalar value of specified type.

    :param value_type: the type of the value stored by container
    :param default: the default value of the container
    """

    def __init__(self, value_type, default=required, **kwargs):
        super(Value, self).__init__(**kwargs)
        self._type = value_type
        self._default = default

    def populate_argparse(self, parser, name):
        value = self
        class Action(argparse.Action):
            def __init__(self, **kwargs):
                super(Action, self).__init__(**kwargs)
                self._const = kwargs.get('const', None)
            def __call__(self, parser, namespace, values, option_string=None):
                if self._const is not None:
                    value._argparse_value = ConfigValue(name, self._const)
                else:
                    value._argparse_value = ConfigValue(name, values[0])

        if self._argparse_names:
            if self._type.is_argparse_flag:
                nargs = 0
                const = True
            else:
                nargs = 1
                const = None
            nargs = 0 if self._type.is_argparse_flag else 1
            parser.add_argument(*self._argparse_names, action=Action,
                                type=self._type.cast, nargs=nargs,
                                metavar=self._argparse_metavar,
                                help=self._argparse_help, const=const)
            if self._type.is_argparse_flag and self._argparse_names_invert:
                parser.add_argument(*self._argparse_names_invert,
                                    action=Action, type=self._type.cast,
                                    nargs=0, help=self._argparse_help_invert,
                                    const=False)

    def validate(self, value):
        if self._argparse_value is not None:
            value = self._argparse_value
        if value is None:
            if self._default is required:
                raise ValidationError('this value is required')
            else:
                return ConfigValue(None, self._default)
        else:
            try:
                validated_value = self._type.validate(value.value)
            except ValidationError as err:
                raise ValidationError(str(err), position=value.position)
            return ConfigValue(value.name, validated_value, position=value.position)


class List(ArgparseContainer):

    """ A list container used to store a list of scalar value of specified type.

    :param values_type: type of values
    :param default: the default value of the container
    """

    def __init__(self, values_type, default=required, **kwargs):
        super(List, self).__init__(**kwargs)
        self._type = values_type
        self._default = default

    def populate_argparse(self, parser, name):
        value = self
        class Action(argparse.Action):
            def __call__(self, parser, namespace, values, option_string=None):
                value._argparse_value = ConfigValue(name, values)
        if self._argparse_names:
            nargs = '*'
            parser.add_argument(*self._argparse_names, action=Action,
                                type=self._type.cast, nargs=nargs,
                                metavar=self._argparse_metavar,
                                help=self._argparse_help)

    def validate(self, value):
        if self._argparse_value is not None:
            value = self._argparse_value
        if value is None:
            if self._default is required:
                raise ValidationError('this value is required')
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

    def populate_argparse(self, parser, name=None):
        """ Populate an argparse parser.
        """

        for name, container in self.keys.iteritems():
            container.populate_argparse(parser, name=name)

    def validate(self, section):
        if not isinstance(section, ConfigSection):
            raise ValidationError('Not a section')

        # Rebuild the section using schema:
        validated_section = ConfigSection(section.name, section.parent,
                                          position=section.position)
        # Validate the section's argument:
        if self.meta['args'] is None and section.args is not None:
            raise ValidationError('section %s, this section does not take '
                                  'any argument' % section.name,
                                  position=section.args.position)
        elif self.meta['args'] is not None:
            try:
                self.meta['args'].validate(section.args)
            except ValidationError as err:
                msg = 'section %s, arguments, %s' % (section.name, err)
                raise ValidationError(msg, position=err.position)
        # Validate the section's children:
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
                        if tuple(subsection.args.value) in args:
                            msg = 'section %s, section must be unique' % name
                            raise ValidationError(msg, position=subsection.position)
                        else:
                            args.add(tuple(subsection.args.value))
                    # Container validation:
                    validated_subsection = container.validate(subsection)
                    validated_section.register(validated_subsection, name=name)
            elif isinstance(container, Container):
                # Validate all other types of containers:
                try:
                    validated_value = container.validate(section.get(name, raw=False))
                except ValidationError as err:
                    raise ValidationError('section %s, key %s, %s' % (section.name, name, err),
                                          position=err.position)
                else:
                    validated_section.register(validated_value, name=name)
        # Handle the allow_unknown meta option:
        for name, child in section.iteritems():
            if name not in validated_section:
                if self.meta['allow_unknown']:
                    validated_section.register(child, name=name)
                else:
                    msg = 'section %s, unknown key %s' % (section.name, name)
                    raise ValidationError(msg, position=child.position)
        return validated_section
