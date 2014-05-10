Welcome to Confiture's documentation!
===================================

Confiture (formerly Dotconf) is an advanced configuration parsing library which
can be used by developers who are limited with standard ConfigParser library.
Confiture is also shipped with a schema validator which can be used to check the
content of your application's configuration file before to start.


Features
--------

- Simple configuration format with sections

- Typing:

  - Typing in the syntax ("42" is a string, 42 a number)

  - Four types availables: string, boolean, number or list

- Validation of configuration using a schema
- Configuration includes


Example
-------

This is an example of what you can do with Confiture::

    from confiture.schema.containers import many, once
    from confiture.schema.containers import Section, Value
    from confiture.schema.types import Boolean, Integer, Float, String

    # Schema definition:

    class UserSection(Section):
        password = Value(String())
        _meta = {'repeat': many, 'unique': True}

    class PathSection(Section):
        rate_limit = Value(Float(), default=0)
        enable_auth = Value(Boolean(), default=False)
        user = UserSection()

    class VirtualHostSection(Section):
        enable_ssl = Value(Boolean(), default=False)
        path = PathSection()
        _meta = {'repeat': many, 'unique': True}

    class MyWebserverConfiguration(Section):
        daemon = Value(Boolean(), default=False)
        pidfile = Value(String(), default=None)
        interface = Value(String(), default='127.0.0.1:80')
        interface_ssl = Value(String(), default='127.0.0.1:443')
        host = VirtualHostSection()

Then, to use the parser::

    >>> conf = '''
    ... daemon = yes
    ... pidfile = '/var/run/myapp.pid'
    ... interface = '0.0.0.0:80'
    ... interface_ssl = '0.0.0.0:443'
    ...
    ... host 'example.org' {
    ...     path '/' {
    ...         rate_limit = 30
    ...     }
    ... }
    ...
    ... host 'protected.example.org' {
    ...     enable_ssl = yes
    ...
    ...     path '/files' {
    ...         enable_auth = yes
    ...         user 'foo' {
    ...             password = 'bar'
    ...         }
    ...     }
    ... }
    ... '''
    >>> from confiture import Confiture
    >>> from myconfschema import MyWebserverConfiguration
    >>> parsed_conf = Confiture(conf, schema=MyWebserverConfiguration()).parse()
    >>> print 'daemon:', parsed_conf.get('daemon')
    True
    >>> for vhost in parsed_conf.subsections('host'):
    >>>     print vhost.args
    >>>     if vhost.get('enable_ssl'):
    >>>         print '  SSL enabled'
    >>>     for path in vhost.subsections('path'):
    >>>         print '  ' + path.args
    >>>         if path.get('enable_auth'):
    >>>             print '    Following users can access to this directory:'
    >>>             for user in path.subsections('user'):
    >>>                 print '     - ' + user.args
    >>>
    example.org
      /
    protected.example.org
      SSL enabled
      /files
        Following users can access to this directory:
          - foo


Contents
--------

.. toctree::
   :maxdepth: 2

   schema/index
   tipsandtricks/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

