====================
Argparse integration
====================

Confiture provide an optionnal integration with the standard ``argparse``
module. This compatibility brings you a way to override some configuration
values using a command line argument.


Define the schema
-----------------

Each compatible :class:`Container` can take five optionnals arguments:

- ``argparse_names``: the list of argument names or flags, the usage of this
  argument enable feature for the container.
- ``argparse_metavar``: the metavar value of the argument (read the argparse
  documentation for more informations).
- ``argparse_help``: the help to display.
- ``argparse_names_invert``: only for a flag value, create an argument to
  invert the boolean value (eg: for a ``--daemon`` argument, you can create a
  ``--foreground`` value which will force to disable the daemonization).
- ``argparse_help_invert``: help message for the invert argument.

Example::

    debug = Value(Boolean, argparse_names=['-d', '--debug'],
                  argparse_help='enable the debug mode')


Populate the argument parser and use it
---------------------------------------

Once your schema is defined, you must call the :meth:`populate_argparse` method
providing the argument parser to populate::

    parser = argparse.ArgumentParser()
    schema = MySchema()
    schema.populate_argparse(parser)
    args = parser.parse_args()
    config = Confiture(conf, schema=schema)
    my_config = config.parse()


Full featured example
---------------------

::

    from pprint import pprint
    import argparse

    from confiture import Confiture
    from confiture.schema import ValidationError
    from confiture.parser import ParsingError
    from confiture.schema.containers import Section, Value, List
    from confiture.schema.types import Boolean, String


    config_test = '''
    debug = no
    paths = '/bin', '/usr/bin'
    '''

    class MySchema(Section):

        debug = Value(Boolean(), argparse_names=['-d', '--debug'],
                      argparse_help='enable the debug mode',
                      argparse_names_invert=['-q', '--quiet'],
                      argparse_help_invert='disable the debug mode')
        paths = List(String(), argparse_names=['--paths'],
                     argparse_help='list of paths to inspect')


    if __name__ == '__main__':
        # 1. Create the argument parser:
        argument_parser = argparse.ArgumentParser()

        # 2. Create the schema:
        schema = MySchema()

        # 3. Populate the argument parser using schema:
        schema.populate_argparse(argument_parser)

        # 4. Parse command line arguments
        args = argument_parser.parse_args()

        # 5. Create the configuration parser:
        config = Confiture(config_test, schema=schema)

        # 6. Parse the configuration and show it:
        try:
            pconfig = config.parse()
        except (ValidationError, ParsingError) as err:
            if err.position is not None:
                print str(err.position)
            print err
        else:
            pprint(pconfig.to_dict())

And an execution example::

    $ ./argparse_example.py --help
    usage: ./argparse_example.py [-h] [-d] [--paths [PATHS [PATHS ...]]]

    optional arguments:
      -h, --help            show this help message and exit
      -d, --debug           enable the debug mode
      -q, --quiet           disable the debug mode
      --paths [PATHS [PATHS ...]]
                            list of paths to inspect
    $ ./argparse_example.py 
    {'debug': False, 'paths': ['/bin', '/usr/bin']}
    $ ./argparse_example.py -d
    {'debug': True, 'paths': ['/bin', '/usr/bin']}
    $ ./argparse_example.py --paths
    {'debug': False, 'paths': []}
    $ ./argparse_example.py --paths /sbin /usr/sbin
    {'debug': False, 'paths': ['/sbin', '/usr/sbin']}

