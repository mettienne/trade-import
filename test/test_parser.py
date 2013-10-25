import parsing
import pytest
import logging

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

def test_get_city(caplog):
    parser = parsing.Parser()
    city = 'Roskilde'
    zip = '4000'
    r_zip, r_city = parser.get_city('{}  {}'.format(zip, city), '')
    assert r_city == city
    assert r_zip == zip 
    print caplog


def test_get_city_warn1(caplog):
    parser = parsing.Parser()
    r_zip, r_city = parser.get_city(' ', 'id1')
    assert r_city == ''
    assert r_zip == '' 
    assert 'empty' in caplog.text()
    assert 'id1' in caplog.text()


def test_get_city_warn2(caplog):
    parser = parsing.Parser()
    parser.get_city('123a ros', 'id1')
    assert 'invalid' in caplog.text()
    assert 'id1' in caplog.text()
