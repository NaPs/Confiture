=========
Confiture
=========

.. image:: https://raw.githubusercontent.com/NaPs/Confiture/master/docs/_static/images/confiture_logo.png

Confiture (formerly Dotconf) is an advanced configuration parser which allow
nested sections to any level, typed values in syntax, file include and so more.
Confiture is also shipped with a powerful schema validation system.

The full documentation can be found here: http://confiture.readthedocs.org

.. image:: https://www.ohloh.net/p/python-confiture/widgets/project_thin_badge.gif
   :target: https://www.ohloh.net/p/python-confiture?ref=sample

.. image:: https://travis-ci.org/NaPs/Confiture.svg?branch=master
   :target: https://travis-ci.org/NaPs/Confiture


Features
--------

- Configuration format kept as simple as possible
- Developer friendly APIs
- Python 2 and 3 compatibility
- Types are expressed in the syntax, so the parser can guess it without
  validation
- Four primitive types: string, number, boolean, or list
- More complex composite types can be created using the schema validation
  system
- Nested section of any deep. Sections can take a special "argument" value
  (look at the example)
- Schema validation system, all schema can be defined using declarative or
  imperative way
- External file include with globbing
- Integration with argparse
- Tests (only parser is covered yet)
- Released under MIT license


Example
-------

This is an example of configuration file for an imaginary web server::


    daemon = yes
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

    >>> from confiture import Confiture
    >>> parsed_conf = Confiture.from_filename('mywebserver.conf').parse()
    >>> print parsed_conf.get('daemon', False)
    True


Even more exciting, you can create a validation schema to avoid you the
painful chore of manual configuration file validation::

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

Then you can use the API exactly as if it was not validated::

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
    daemon: True
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

Setup
-----

The fastest and more common way to install Confiture is using pip::

    pip install confiture

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
    # aptitude install python-confiture

Archlinux
~~~~~~~~~

If you use Archlinux, a Confiture package is available in Aur::

    yaourt -S python2-confiture


TODO
----

- More test.


Changelog
---------

v2.1 - Strawberry mark II, released on 12/10/16
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This release only fix a small bug related to encoding and setuptools building
process and adds the Path schema type contributed by Anaël Beutot.

Changes:

- Added the Path schema type
- Fixed encoding bug when building Python package on Python3/non-utf8 system

v2.0 - Strawberry, released on 11/05/14
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

I finally decided to rename Dotconf as Confiture to avoid name conflict with
another (and similar) project which is already packaged in several distro.
Confiture means jam in French and is also at one letter from Configure.

Obviously, this change has broken the API, so I incremented sur API compat
version number. Migrating from Dotconf to Confiture will be simple as
substituting "dotconf" by "confiture" and "Dotconf" by "Confiture".

Changes:

- Renamed Dotconf as Confiture
- Added a beautiful logo :-)
- Fixed documentation build
- Fixed Travis-CI execution
- Fixed parser which now detects unexpected end of files
- Now use universal newline flag when opening file in from_filename (ref #13)

New contributors:

- Grégoire Rocher (provided a fix for the parser)

v1.8 released on 08/09/13
~~~~~~~~~~~~~~~~~~~~~~~~~

This new release bring a lot of bugfixes all reported by Stefan Tschiggerl.
Thanks to him for its time and its help to enhance Confiture.

Changes:

- Fixed a bug where from_filename is not passing extra
- Fixed examples in readme and docs
- Fixed bad API usage in containers' argument validation
- Handle the uniqueness validation of empty args
- Added single subsection access method (eg: section.subsection('foo'))
- Fixed optional section without occurrence not working
- Fixed a bug when subsection method is used twice with the same name
- Fixed traceback when a section is not in schema

New contributors:

- Stefan Tschiggerl (bug report and fixes)

v1.7 released on 31/07/13
~~~~~~~~~~~~~~~~~~~~~~~~~

The major (and almost the only) change of this release is the compatibility with
Python 3. This work has been done with the help of 2to3 with some thing fixed
manually. Enjoy!

- Added compatibility with Python 3
- Now use py.test instead of nosetests

v1.6 released on 09/12/12
~~~~~~~~~~~~~~~~~~~~~~~~~

This second stable release bring some bug fixes and features, the API has not
been broken. I also registered the project on travis-ci and I will try to
improve the test coverage for the next release.

Changes:

- Added Choice container
- Added a from_filename constructor the the Confiture class
- Added encoding management (by default, files are parsed in UTF-8)
- Added continuous integration with travis
- Fixed bug with Float type validation
- Fixed an error when a section is included by an external file (thanks to
  DuanmuChun for its bug report and help to fix it)
- Fixed other minor bugs

New contributors:

- DuanmuChun (bug report and help to fix it)

v1.5 released on 14/04/2012
~~~~~~~~~~~~~~~~~~~~~~~~~~~

First stable release of Confiture has been released, development will now take
care of API compatibility. The project status has been changed to "Beta" on the
PYPI, and should be "Stable" on the next release if no major bug is found.
Packages will be updated for Debian and Archlinux, feel free to contact me if
you want to package it for your distro.

Changes:

- Added Eval, NamedRegex and RegexPattern types
- Added TypedArray container
- Fixed bug with scalar values from a singleton list in Value container
- Fixed argument validation in Section container
- Updated documentation (new tips and tricks section)

New contributors:

- Anaël Beutot (thanks for RegexPattern type and argument validation fix)

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


A note on versioning
--------------------

Confiture use a two numbers X.Y versioning. The Y part is incremented by one on
each release. The X part is used as API compatibility indicator and will be
incremented each time the API is broken.


Contribute
----------

You can contribute to Confiture through these ways:

- Github: https://github.com/NaPs/Confiture

Feel free to contact me for any question/suggestion: <antoine@inaps.org>.
