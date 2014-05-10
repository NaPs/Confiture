Containers
==========

Section container
-----------------

.. autoclass:: confiture.schema.containers.Section

Typically, this class has to be derived to specify accepted key for
the section::

    class MySection(Section):

        a_key = Value(Integer())

A section can also be defined imperatively::

    >>> section = MySection()
    >>> section.add('another_key', Value(Integer()))


Metadata
********

A section can hold some metadata, for example to define arguments
schema or how many time the section can appear. This metadata can be
defined in several different ways:

- In the ``_meta`` dict of a section definition (metadata are inherited
  from parent classes)::

    class MySection(Section):
        _meta = {'unique': True}
- In the ``meta`` dict of a section object::

    >>> section = MySection()
    >>> section.meta['unique'] = True
- In keyword parameters on instance initialization::

    >>> section = MySection(unique=True)


Accepted metadata
+++++++++++++++++

args
^^^^

The ``args`` metadata (default ``None``) store the container used to validate
the section argument (value between the section name and the opening brace).
You can use any type of container but a :class:`Section`.

If the metadata is set to ``None`` (the default), argument for the section
is forbidden.

Example::

    class MySection(Section):
        _meta = {'args': Value(String())}

.. note::
   This meta can't be defined for the ``__top__`` section.


unique
^^^^^^

The ``unique`` metadata (default ``False``) can be used to prevent multiple
section to have the same arguments.

For example if you have a section with this kind of schema::

    class MySubSection(Section):
        _meta = {'args': Value(String()), 'unique': True}

    class MySection(Section):
        sub = MySubSection()

And a configuration file with this content::

    sub "foo" {...}
    sub "bar" {...}
    sub "foo" {...}

The last "foo" section will throw a validation error because an another "sub"
section already exists with this argument.

.. note::
   This meta can't be defined for the ``__top__`` section.


repeat
^^^^^^

The ``repeat`` metadata (default to ``(1, 1)``) allow to define how many time
the section can appear. The first value is the minimum number of times, and
the second the maximum number of time.

Values must be non-negative integers, and the first must be smaller or equal
to the second. The second value can be set to None to express the infinite
value.

Examples:

- ``(1, 1)``: the section must appear once
- ``(1, 2)``: the section must appear one or two times
- ``(0, 1)``: the section is optionnal and can appear once
- ``(0, None)``: the section is optionnal and can appear an infinite number of
  times
- ``(1, None)``: the section mut appear at least once


Some shortcut are available in the :mod:`confiture.schema.containers` module:

- ``once`` -> ``(1, 1)``
- ``many`` -> ``(0, None)``

.. note::
   This meta can't be defined for the ``__top__`` section.


allow_unknown
^^^^^^^^^^^^^

The ``allow_unknow`` metadata (default to ``False``) allow the user to set
value which are not defined in the section schema. Unknown data are then
available in the validated section.


Value container
---------------

.. autoclass:: confiture.schema.containers.Value


Choice container
----------------

.. autoclass:: confiture.schema.containers.Choice


List containers
---------------

.. autoclass:: confiture.schema.containers.List


Array containers
----------------

.. autoclass:: confiture.schema.containers.Array
.. autoclass:: confiture.schema.containers.TypedArray
