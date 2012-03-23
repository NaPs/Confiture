""" Dotconf lexer and parser.
"""


from glob import glob

import ply.lex as lex
import ply.yacc as yacc

from dotconf.tree import ConfigSection, ConfigValue, Position


class ParsingError(Exception):

    """ Error raised when a parsing error occurs.
    """

    def __init__(self, msg, position=None):
        super(ParsingError, self).__init__(msg)
        self.position = position


def default_external_opener(locator):
    """ The default locator used to open included external files.
    """
    parsed_externals = []
    for external in glob(locator):
        try:
            with open(external) as fexternal:
                external_data = fexternal.read()
        except IOError as err:
            raise ParsingError('Unable to open %s (%s)' % (external, err))
        parser = DotconfParser(external_data, debug=False, write_tables=False,
                               errorlog=yacc.NullLogger(), input_name=external,
                               external_opener=default_external_opener)
        parsed_externals.append(parser.parse())
    return parsed_externals


#
# Lexer
#

class DotconfLexer(object):

    """ Lexer for the DotConf format.

    :param \*\*kwargs: arguments to give to the ply lexer

    Usage example::

    >>> lexer = DotConfLexer()
    >>> lexer.input('test { key = yes }')
    >>> print lexer.next()
    """

    def __init__(self, **kwargs):
        self._lexer = lex.lex(module=self, **kwargs)

    #
    # Tokens definition
    #

    reserved = {'yes': 'YES', 'no': 'NO', 'include': 'INCLUDE'}
    tokens = ['LBRACE', 'RBRACE', 'NAME', 'TEXT', 'NUMBER',
              'ASSIGN', 'LIST_SEP'] + reserved.values()

    t_LBRACE = '{'
    t_RBRACE = '}'
    t_ASSIGN = '='
    t_LIST_SEP = ','
    t_ignore = ' \t'

    def t_NAME(self, token):
        r'[a-zA-Z_][a-zA-Z0-9_-]*'
        token.type = self.reserved.get(token.value, 'NAME')
        # Handle the boolean case:
        if token.type == 'YES':
            token.value = True
        elif token.type == 'NO':
            token.value = False
        return token

    def t_TEXT(self, token):
        r'(["]([\\]["]|[^"]|)*["]|[\']([\\][\']|[^\'])*[\'])'
        value = token.value[1:-1].replace('\\' + token.value[0], token.value[0])
        token.value = value
        # Count the lines in the string:
        token.lexer.lineno += value.count('\n')
        return token

    def t_NUMBER(self, token):
        r'[-+]?[0-9]+(\.[0-9]+)?'
        if token.value.isdigit():
            token.value = int(token.value)
        else:
            token.value = float(token.value)
        return token

    def t_EOL(self, token):
        r'[\n]+'
        token.lexer.lineno += len(token.value)

    def t_COMMENT(self, token):
        r'[#].*'

    def t_error(self, token):
        position = Position(self._input_name,
                            self._lexer.lineno,
                            self._lexer.lexpos)
        raise ParsingError('Illegal character %r' % token.value[0], position)


    #
    # Public methods
    #

    def column(self, lexpos):
        """ Find the column according to the lexpos.
        """
        # This code is taken from the python-ply documentation
        # see: http://www.dabeaz.com/ply/ply.html section 4.6
        last_cr = self._current_input.rfind('\n', 0, lexpos)
        if last_cr < 0:
            last_cr = 0
        column = (lexpos - last_cr)
        return column


    #
    # Bindings to the internal _lexer object
    #

    def input(self, input):
        self._current_input = input
        return self._lexer.input(input)

    def __getattr__(self, name):
        attr = getattr(self._lexer, name)
        if attr is None:
            raise AttributeError("'%s' object has no attribute '%s'" % (self, name))
        else:
            return attr

#
# Parser
#

class DotconfParser(object):

    """ Parser for the Dotconf format.
    """

    tokens = DotconfLexer.tokens

    def __init__(self, input, **kwargs):
        self._input = input
        self._input_name = kwargs.pop('input_name', '<unknown>')
        self._external_opener = kwargs.pop('external_opener',
                                           default_external_opener)
        self._lexer = kwargs.pop('lexer', DotconfLexer())
        self._parser = yacc.yacc(module=self, **kwargs)
        self._old_line = 0

    def _check_line(self, current, lineno, pos, token):
        if self._old_line == current:
            pos = Position(self._input_name, lineno, pos)
            raise ParsingError('Syntax error near of "%s", '
                               'newline missing?' % token, pos)
        else:
            self._old_line = current

    #
    # Rules
    #

    start = 'top'

    def p_top(self, p):
        """top : section_content"""
        section = ConfigSection('__top__')
        for child in p[1]:
            if isinstance(child, ConfigSection):
                child.parent = section
            section.register(child)
        p[0] = section

    def p_assignation(self, p):
        """assignment : NAME ASSIGN value
                      | NAME ASSIGN list"""
        position = Position(self._input_name,
                            p.lineno(3),
                            p.lexer.column(p.lexpos(3)))
        value = ConfigValue(p[1], p[3], position=position)
        p[0] = value

    def p_value(self, p):
        """value : TEXT
                 | YES
                 | NO
                 | NUMBER"""
        p[0] = p[1]

    #
    # List management rules:
    #

    def p_list(self, p):
        """list : value LIST_SEP list_next
                | value LIST_SEP"""
        if len(p) == 3:
            p[0] = [p[1]]
        elif len(p) == 4:
            p[3].insert(0, p[1])
            p[0] = p[3]

    def p_list_next(self, p):
        """list_next : value
                     | value LIST_SEP
                     | value LIST_SEP list_next"""
        if len(p) in (2, 3):
            p[0] = [p[1]]
        elif len(p) == 4:
            p[3].insert(0, p[1])
            p[0] = p[3]

    #
    # Sections:
    #

    def p_section_content_empty(self, p):
        """section_content : empty"""
        p[0] = []

    def p_section_content_assignation(self, p):
        """section_content : section_content assignment
                           | section_content section"""
        self._check_line(p.lexer.lineno, p.lineno(2),
                         self._lexer.column(p.lexpos(2)), p[2].name)
        p[1].append(p[2])
        p[0] = p[1]

    def p_section_content_include(self, p):
        """section_content : section_content INCLUDE TEXT"""
        for external in self._external_opener(p[3]):
            p[1] += list(external.iterchildren())
        p[0] = p[1]

    def p_section(self, p):
        """section : NAME LBRACE section_content RBRACE
                   | NAME section_args LBRACE section_content RBRACE"""
        name = p[1]
        if len(p) == 5:
            args = None
            section_content = p[3]
        else:
            args = p[2]
            section_content = p[4]
        column = p.lexer.column(p.lexpos(1))
        position = Position(self._input_name, p.lineno(1), column)
        section = ConfigSection(name, args=args, position=position)
        for child in section_content:
            if isinstance(child, ConfigSection):
                child.parent = section
            section.register(child)
        p[0] = section

    def p_section_args(self, p):
        """section_args : value LIST_SEP section_args
                        | value"""
        if len(p) == 2:
            position = Position(self._input_name,
                                p.lineno(1),
                                p.lexer.column(p.lexpos(1)))
            p[0] = ConfigValue('<args>', [p[1]], position=position)
        else:
            p[3].value.insert(0, p[1])
            p[0] = p[3]

    def p_empty(self, p):
        """empty :"""
        pass

    def p_error(self, token):
        column = self._lexer.column(token.lexpos)
        pos = Position(self._input_name, token.lineno, column)
        raise ParsingError('Syntax error near of "%s"' % token.value, pos)


    #
    # Bindings to the internel _parser object
    #

    def parse(self):
        return self._parser.parse(self._input, self._lexer, tracking=True)

    def __getattr__(self, name):
        attr = getattr(self._parser, name)
        if attr is None:
            raise AttributeError("'%s' object has no attribute '%s'" % (self, name))
        else:
            return attr

#
# Tests
#

from nose.tools import eq_


def test_lexer():
    #          Test string            Expected tok     Expected tok value
    tokens = (('name',                'NAME',          'name'),
              ('"test"',              'TEXT',          'test'),
              ("'test'",              'TEXT',          'test'),
              (r"'te\'st'",           'TEXT',          "te'st"),
              ('42',                  'NUMBER',        42),
              ('42.1',                'NUMBER',        42.1),
              ('+42',                 'NUMBER',        42),
              ('+42.1',               'NUMBER',        42.1),
              ('-42',                 'NUMBER',        -42),
              ('-42.1',               'NUMBER',        -42.1),
              ('{',                   'LBRACE',        '{'),
              ('}',                   'RBRACE',        '}'),
              ('=',                   'ASSIGN',        '='))
    for test, expected_type, expected_value in tokens:
        yield check_token, test, expected_type, expected_value


def check_token(test, expected_type, expected_value):
    lexer = DotconfLexer()
    lexer.input(test)
    token = lexer.next()
    eq_(token.type, expected_type)
    eq_(token.value, expected_value)

def test_parser_basic():
    test = '''
    daemon = yes  # This is a comment after an assignation
    # This is comment
    '''
    lexer = DotconfLexer()
    parser = DotconfParser(debug=True, write_tables=False, errorlog=yacc.NullLogger())
    output = parser.parse(test, lexer=lexer, tracking=True)
    eq_(output.get('daemon'), True)

def test_parser_list():
    test = '''
    list1 = 1, 2, 3
    list2 = 1, 2, 3,
    list3 = 1,
    list4 = 1,
            2,
            3
    list5 = 1,
            2,
            3,
    '''
    lexer = DotconfLexer()
    parser = DotconfParser(debug=True, write_tables=False, errorlog=yacc.NullLogger())
    output = parser.parse(test, lexer=lexer, tracking=True)
    eq_(output.get('list1'), [1, 2, 3])
    eq_(output.get('list2'), [1, 2, 3])
    eq_(output.get('list3'), [1])
    eq_(output.get('list4'), [1, 2, 3])
    eq_(output.get('list5'), [1, 2, 3])

def test_parser_section():
    test = '''
    section1 {
        key = 'test'
    }
    section2 'arg' {}
    section3 'arg1', 'arg2' {}
    '''
    lexer = DotconfLexer()
    parser = DotconfParser(debug=True, write_tables=False, errorlog=yacc.NullLogger())
    output = parser.parse(test, lexer=lexer, tracking=True)
    eq_(tuple(output.subsections('section1'))[0].get('key'), 'test')
    eq_(tuple(output.subsections('section2'))[0].args, ['arg'])
    eq_(tuple(output.subsections('section3'))[0].args, ['arg1', 'arg2'])

def test_parser_empty():
    test = ''''''
    lexer = DotconfLexer()
    parser = DotconfParser(debug=True, write_tables=False, errorlog=yacc.NullLogger())
    output = parser.parse(test, lexer=lexer, tracking=True)
