""" Confiture's parser tests.
"""

import pytest

from confiture.parser import ConfitureLexer, ConfitureParser, ParsingError


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
    lexer = ConfitureLexer()
    lexer.input(test)
    token = lexer.next()
    assert token.type == expected_type
    assert token.value == expected_value

def test_parser_basic():
    test = '''
    daemon = yes  # This is a comment after an assignation
    # This is comment
    '''
    parser = ConfitureParser(test)
    output = parser.parse()
    assert output.get('daemon') is True

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
    parser = ConfitureParser(test)
    output = parser.parse()
    assert output.get('list1') == [1, 2, 3]
    assert output.get('list2') == [1, 2, 3]
    assert output.get('list3') == [1]
    assert output.get('list4') == [1, 2, 3]
    assert output.get('list5') == [1, 2, 3]

def test_parser_section():
    test = '''
    section1 {
        key = 'test'
    }
    section2 'arg' {}
    section3 'arg1', 'arg2' {}
    '''
    parser = ConfitureParser(test)
    output = parser.parse()
    assert tuple(output.subsections('section1'))[0].get('key') == 'test'
    assert tuple(output.subsections('section2'))[0].args == ['arg']
    assert tuple(output.subsections('section3'))[0].args == ['arg1', 'arg2']

def test_parser_empty():
    test = ''''''
    parser = ConfitureParser(test)
    output = parser.parse()

def test_parser_end_of_file():
    test = '''
    section {
    '''
    parser = ConfitureParser(test)
    with pytest.raises(ParsingError):
        parser.parse()
