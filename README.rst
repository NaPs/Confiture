=======
Dotconf
=======

Dotconf is an advanced configuration parser which allow nested sections to any
level, typed values in syntax, file include and so more. Dotconf is also
shipped with a powerful schema validation system.

The full documentation can be found here: http://dotconf.readthedocs.org

Features
--------

- Configuration format kept as simple as possible.
- Developer friendly APIs.
- Types are expressed in the syntax, so the parser can guess it without
  validation.
- Four primitive types: string, number, boolean, or list.
- More complex composite types can be created using the schema validation
  system.
- Nested section of any deep. Sections can take a special "argument" value
  (look at the example).
- Schema validation system, all schema can be defined using declarative or
  imperative way.
- External file include with globbing.
- Integration with argparse.
- Tests (only parser is covered yet)
- Released under MIT license.


Example
-------

This is an example of configuration file for an imaginary web server::


    daemon = True
    pidfile = '/var/run/myapp.pid'
    interface = '0.0.0.0:80'
    interface_ssl = '0.0.0.0:443'

    host 'example.org' {
        path '/' {
            rate_limit = 30
        }
    }

    host 'protected.example.org' {
        enable_ssl = yes

        path '/files' {
            enable_auth = yes
            user 'foo' {
                password = 'bar'
            }
        }
    }

You can access to each values using the developer friendly API::

    >>> from dotconf import Dotconf
    >>> parsed_conf = Dotconf.from_file('mywebserver.conf')
    >>> print parsed_conf.get('daemon', False)
    True


Even more exciting, you can create a validation schema to avoid you the
painful chore of manual configuration file validation::

    from dotconf.schema import many, once
    from dotconf.schema.containers import Section, Value
    from dotconf.schema.types import Boolean, Integer, Float, String

    # Schema definition:

    class UserSection(Section):
        password = Value(String())
        _meta = {'repeat': many, 'unique': True}

    class PathSection(Section):
        rate_limit = Value(Float(), default=0)
        enable_auth = Value(Boolean(), default=False)
        user = UserSection()

    class VirtualHostSection(Section):
        base_path = Value(String())
        enable_ssl = Value(Boolean(), default=False)
        path = PathSection()
        _meta = {'repeat': many, 'unique': True}

    class MyWebserverConfiguration(Section):
        daemon = Value(Boolean()default=False)
        pidfile = Value(String(), default=None)
        interface = Value(String(), default='127.0.0.1:80')
        interface_ssl = Value(String(), default='127.0.0.1:443')
        host = VirtualHostSection()

Then you can use the API exactly as if it was not validated::

    >>> from dotconf import Dotconf
    >>> from myconfschema import MyWebserverConfiguration
    >>> parsed_conf = Dotconf(conf, schema=MyWebserverConfiguration)
    >>> print 'daemon:', parsed_conf.get('daemon')
    daemon: True
    >>> for vhost in parsed_conf.subsections('host'):
    >>>     print vhost.args[0]
    >>>     if vhost.get('enable_ssl'):
    >>>         print '  SSL enabled'
    >>>     for path in vhost.subsections('path'):
    >>>         print '  ' + path.args[0]
    >>>         if path.get('enable_auth'):
    >>>             print '    Following users can access to this directory:'
    >>>             for user in path.subsections('user'):
    >>>                 print '     - ' + user.args[0]
    >>>
    example.org
      /
    protected.example.org
      SSL enabled
      /files
        Following users can access to this directory:
          - foo

Setup
-----

The fastest and more common way to install Dotconf is using pip::

    pip install dotconf

Debian
~~~~~~

If you use Debian, you can also use the Tecknet repositories. Add this lines
in your ``/etc/apt/source.list`` file::

    deb http://debian.tecknet.org/debian squeeze tecknet
    deb-src http://debian.tecknet.org/debian squeeze tecknet

Add the Tecknet repositories key in your keyring:

    # wget http://debian.tecknet.org/debian/public.key -O - | apt-key add -

Then, update and install::

    # aptitude update
    # aptitude install python-dotconf

Archlinux
~~~~~~~~~

If you use Archlinux, a Dotconf package is available in Aur::

    yaourt -S python2-dotconf


TODO
----

- More test.


Changelog
---------

v0.4 released on 07/04/2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Added debian package
- Added IPSocketAddress type
- Added Array container
- Added release procedure
- Fixed bug on IPAddress and IPNetwork types when ipaddr is missing
- Fixed documentation build

v0.3 released on 04/04/2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Added IPAddress, IPNetwork, Regex and Url types
- Added min and max options on Integer type
- Added units on number parsing (42k == 42000)
- Fixed bug with validation of long numbers

v0.2 released on 03/04/2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Added argparse integration feature & documentation
- Cleanup

v0.1 released on 24/03/2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Initial version.


Contribute
----------

You can contribute to Dotconf through these ways:

- Main Git repository: https://idevelop.org/p/dotconf/source/tree/master/
- Bitbucket: https://bitbucket.org/NaPs/dotconf
- Github: https://github.com/NaPs/Dotconf

Feel free to contact me for any question/suggestion: <antoine@inaps.org>.
