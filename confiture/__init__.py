""" Confiture is an advanced configuration parser for Python.
"""


from confiture.parser import ConfitureParser, yacc


class Confiture(object):

    def __init__(self, config, schema=None, input_name='<unknown>'):
        self._config = config
        self._schema = schema
        self._input_name = input_name

    @classmethod
    def from_filename(cls, filename, **kwargs):
        fconf = open(filename, 'Ur')
        kwargs['input_name'] = filename
        return cls(fconf.read(), **kwargs)

    def _parse(self):
        parser = ConfitureParser(self._config, debug=False, write_tables=False,
                               errorlog=yacc.NullLogger(), input_name=self._input_name)

        return parser.parse()

    def parse(self):
        config = self._parse()
        if self._schema is not None:
            config = self._schema.validate(config)
        return config
