""" Builtin containers of confiture.schema
"""

import sys
try:
    import argparse
except ImportError:
    argparse = None

if sys.version_info[0] < 3:
    from itertools import izip as zip

from confiture.tree import ConfigSection, ConfigValue
from confiture.schema import Container, ArgparseContainer, ValidationError


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
            if isinstance(value.value, list):
                if len(value.value) == 1:
                    value.value = value.value[0]
                else:
                    raise ValidationError('%r is a list' % value.value,
                                          position=value.position)
            try:
                validated_value = self._type.validate(value.value)
            except ValidationError as err:
                raise ValidationError(str(err), position=value.position)
            return ConfigValue(value.name, validated_value, position=value.position)


class Choice(ArgparseContainer):

    """ A choice container used to store a choice of acceptable values.

    This container take a choices dict where each key is one of the acceptable
    values, and the according value, the value returned when the key is
    chosen.

    :param choices: the choices dict
    :param default: the default value of the container
    """

    def __init__(self, choices, default=required, **kwargs):
        super(Choice, self).__init__(**kwargs)
        self._choices = choices
        self._default = default

    def populate_argparse(self, parser, name):
        choice = self

        class Action(argparse.Action):

            def __init__(self, **kwargs):
                super(Action, self).__init__(**kwargs)
                self._const = kwargs.get('const', None)

            def __call__(self, parser, namespace, values, option_string=None):
                if self._const is not None:
                    choice._argparse_value = ConfigValue(name, self._const)
                else:
                    choice._argparse_value = ConfigValue(name, values)

        if self._argparse_names:
            parser.add_argument(*self._argparse_names, action=Action,
                                choices=list(self._choices.keys()),
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
            if isinstance(value.value, list):
                if len(value.value) == 1:
                    value.value = value.value[0]
                else:
                    raise ValidationError('%r is a list' % value.value,
                                          position=value.position)
            if value.value in self._choices:
                return ConfigValue(value.name, self._choices[value.value],
                                   position=value.position)
            else:
                choices = ', '.join(repr(x) for x in self._choices)
                raise ValidationError('bad choice (must be one of %s)' % choices)


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


class Array(List):

    """ An array container used to store a fixed size list of scalar values of
        the specified type.

    :param size: size of the array
    :param \*\*kwargs: same arguments as List
    """

    def __init__(self, size, *args, **kwargs):
        super(Array, self).__init__(*args, **kwargs)
        self._size = size

    def populate_argparse(self, parser, name):
        value = self

        class Action(argparse.Action):

            def __call__(self, parser, namespace, values, option_string=None):
                value._argparse_value = ConfigValue(name, values)

        if self._argparse_names:
            parser.add_argument(*self._argparse_names, action=Action,
                                type=self._type.cast, nargs=self._size,
                                metavar=self._argparse_metavar,
                                help=self._argparse_help)

    def validate(self, value):
        value = super(Array, self).validate(value)
        if len(value.value) != self._size:
            raise ValidationError('bad array size (should be %d, found %d items)'
                                  % (self._size, len(value.value)))
        return value


class TypedArray(ArgparseContainer):

    """ An array container used to store a fixed size list of scalar values
        with specified type for each of them.

    :param values_types: types of each item in a list
    :param default: the default value of the container
    """

    def __init__(self, values_types, default=required, **kwargs):
        super(TypedArray, self).__init__(**kwargs)
        self._types = values_types
        self._default = default

    def populate_argparse(self, parser, name):
        value = self

        class Action(argparse.Action):

            def __call__(self, parser, namespace, values, option_string=None):
                value._argparse_value = ConfigValue(name, values)

        if self._argparse_names:
            nargs = '*'
            parser.add_argument(*self._argparse_names, action=Action,
                                type=str, nargs=nargs,
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
            if len(values) != len(self._types):
                raise ValidationError('bad array size (should be %d, found %d '
                                      'items)' % (len(self._types), len(values)))

            for i, (item, item_type) in enumerate(zip(values, self._types)):
                try:
                    item = item_type.validate(item)
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
            for key, value in cls.__dict__.items():
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

        for name, container in self.keys.items():
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
                                  position=section.position)
        elif self.meta['args'] is not None:
            try:
                validated_args = self.meta['args'].validate(section.args_raw)
            except ValidationError as err:
                msg = 'section %s, arguments, %s' % (section.name, err)
                raise ValidationError(msg, position=err.position)
            else:
                validated_section.args = validated_args
        # Validate the section's children:
        for name, container in self.keys.items():
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
                        args_value = None if subsection.args is None else tuple(subsection.args)
                        if args_value in args:
                            msg = 'section %s, section must be unique' % name
                            raise ValidationError(msg, position=subsection.position)
                        else:
                            args.add(args_value)
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
        for name, child in section.iteritems(expand_sections=True):
            if name not in self.keys:
                if self.meta['allow_unknown']:
                    validated_section.register(child, name=name)
                else:
                    msg = 'section %s, unknown key %s' % (section.name, name)
                    raise ValidationError(msg, position=child.position)
        return validated_section
