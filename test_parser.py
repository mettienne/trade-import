import parsing
import pytest

def test_get_price():
    parser = parsing.Parser()
    assert parser.get_price('') == 0
    assert parser.get_price('10,00') == 1000
    assert parser.get_price('100,43') == 10043
    assert parser.get_price('1000,43') == 100043
    assert parser.get_price('1.000,43') == 100043
    assert parser.get_price('10.000,43') == 1000043
    assert parser.get_price('10.000.000,43') == 1000000043

def test_get_lines(tmpdir):
    parser = parsing.Parser()
    foo_file = tmpdir.join('foo')
    p = foo_file.open('w')
    p.write(" line1:\nline2:\nline3:\nline4:\n::")
    p = foo_file.open('r')
    lines = list(parser.get_lines(p))
    assert lines == [[u'line1', 
            u'line2', u'line3', u'line4']]

def test_get_lines_error1(tmpdir):
    parser = parsing.Parser()
    foo_file = tmpdir.join('foo')
    p = foo_file.open('w')
    p.write(" line1:\nline2:\nline3:\nline4:\n")
    p = foo_file.open('r')
    with pytest.raises(Exception):
        lines = list(parser.get_lines(p))

def test_get_lines_error2(tmpdir):
    parser = parsing.Parser()
    foo_file = tmpdir.join('foo')
    p = foo_file.open('w')
    p.write(" line1:\nline2:\nline3:\nline4\n::")
    p = foo_file.open('r')
    with pytest.raises(Exception):
        lines = list(parser.get_lines(p))
