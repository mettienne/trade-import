import parsing
import pytest
import logging
import config
from datetime import datetime

parser = parsing.Parser()

def test_get_price():
    assert parser.get_price('') == 0
    assert parser.get_price('10,00') == 1000
    assert parser.get_price('100,43') == 10043
    assert parser.get_price('1000,43') == 100043
    assert parser.get_price('1.000,43') == 100043
    assert parser.get_price('10.000,43') == 1000043
    assert parser.get_price('10.000.000,43') == 1000000043
    assert parser.get_price('10.000.000,4') == 1000000040
    assert parser.get_price('10.000.000') == 1000000000

def test_parse_file(tmpdir):
    filename = 'foo'
    foo_file = tmpdir.join(filename)
    p = foo_file.open('w')
    p.write("line1:\r\nline2:\r\nline3:\r\nline4:\r\n::")
    p.close()
    config.path = foo_file.dirname
    lines = parser.parse_file(filename)
    assert lines == [u'line1:', 
            u'line2:', u'line3:', u'line4:']

def test_get_lines(tmpdir):
    lines = ['line1:', 'line2:', 'line3:', 'line4:', '::']
    res = list(parser.get_lines(lines))
    assert res == [[u'line1', 
            u'line2', u'line3', u'line4']]

def test_get_lines_error1(tmpdir):
    lines = ['line1:', 'line2:', 'line3:', 'line4:']
    with pytest.raises(Exception) as ex:
        lines = list(parser.get_lines(lines))
    assert ex.value.message == 'File not properly ended'
        

def test_get_lines_error2(tmpdir):
    lines = ['line1', 'line2', 'line3:', 'line4::']
    with pytest.raises(Exception) as ex:
        lines = list(parser.get_lines(lines))
    assert ex.value.message == 'Line not properly ended'

def test_get_city(caplog):
    city = 'Roskilde'
    zip = '4000'
    r_zip, r_city = parser.get_city('{}  {}'.format(zip, city), '')
    assert r_city == city
    assert r_zip == zip 
    print caplog


def test_get_city_warn1(caplog):
    r_zip, r_city = parser.get_city(' ', 'id1')
    assert r_city == ''
    assert r_zip == '' 
    assert 'empty' in caplog.text()
    assert 'id1' in caplog.text()


def test_get_city_warn2(caplog):
    parser.get_city('123a ros', 'id1')
    assert 'invalid' in caplog.text()
    assert 'id1' in caplog.text()

def test_get_qty(caplog):
    qty = parser.get_qty('123.000', 'id1')
    assert qty == 123000
    qty = parser.get_qty('-129', 'id1')
    assert qty == -129 
    assert 'negative quantity' in caplog.text()
    qty = parser.get_qty('ert', 'id1')
    assert 'invalid format' in caplog.text()
    assert qty == 0 

def test_get_date(caplog):
    date = parser.get_date('10-12-03', 'id1')
    assert date == datetime(2003, 12, 10, 0, 0, 0)
    date = parser.get_date('', 'id1')
    assert 'date invalid' in caplog.text()
    assert date == ''
