""" Dotconf is an advanced configuration parser for Python.
"""


from dotconf.parser import DotconfParser, yacc


class Dotconf(object):

    def __init__(self, config, schema=None):
        self._config = config
        self._schema = schema

    def _parse(self):
        parser = DotconfParser(self._config, debug=False, write_tables=False,
                               errorlog=yacc.NullLogger())

        return parser.parse()

    def parse(self):
        config = self._parse()
        if self._schema is not None:
            config = self._schema.validate(config)
        return config
