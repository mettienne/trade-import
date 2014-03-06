import os.path
import re
import pytest
from utils import export
from datetime import datetime
import parsing

oio = export.OIOXML()
edi = export.EDI()

def fold(string):
    string = re.sub(r'\s+', '', string)

    for g in ['\n', '\t', '\r']:
        string = string.replace(g, '')
    return string

@pytest.mark.parametrize('f', os.listdir(os.path.join('test','data','oio_xml')))
def test_ok_output(f, db):
    print f
    number, ext = f.split('.')
    if ext != 'xml':
        return

    invoice = db.salesinvoices.find_one({ 'key': int(number) })
    deptor = db.deptors.find_one({ 'key': invoice['customer_number'] })
    lines_with_ean = []
    for line in invoice['lines']:
        if not line['item_number']:
            continue
        if not line['ean']:
            item = db.items.find_one({ 'key': line['item_number'] })
            line['ean'] = item['ean']

        lines_with_ean.append(line)

    invoice['lines'] = lines_with_ean
    resp = oio.create_element(invoice, deptor['search_name'])
    valid = open(os.path.join('test', 'data', 'oio_xml', f))
    res = fold(resp.read())
    valid = fold(valid.read())
    #print '#'*10
    #print valid
    #print '#'*10
    #print res
    #print '#'*10
    assert valid == res

def test_edi(db):
    #invoice = db.salesinvoices.find_one({ 'key': 88917 })
    invoice = db.salesinvoices.find_one({ 'key': 72941 })
    deptor = db.deptors.find_one({ 'key': invoice['customer_number'] })
    print invoice, deptor
    lines_with_ean = []
    for line in invoice['lines']:
        if not line['item_number']:
            continue
        if not line['ean']:
            item = db.items.find_one({ 'key': line['item_number'] })
            if item:
                line['ean'] = item['ean']

        lines_with_ean.append(line)

    invoice['lines'] = lines_with_ean
    resp = edi.create_element(invoice, deptor['key'])
    print resp
    #print '#'*10
    #print valid
    #print '#'*10
    #print res
    #print '#'*10
    #assert valid == res

def test_supergros(db):
    parser = parsing.Parser()
    data = open(os.path.join('test', 'data', 'supergros_test.csv'))
    items = []
    for line in data:
        _, ean, number, price = line.strip().split(';')
        item = db.items.find_one({ 'key': number })
        if not item:
            print 'Vare eksisterer ikke: {}'.format(number)
            continue
        assert ean == item['ean'], 'Ean forkert {} {}'.format(ean, item['ean'])
        if '.' in price:
            price = price.replace('.', '') + '0'
        else:
            price = price + '00'
        if int(price) != item['price']:
            print 'Pris forkert', number, item['price'], price
            continue
        items.append(item)
        item['total_without_tax'] = item['price']
        item['total_with_tax'] = item['price'] * 1.25
        item['item_number'] = item['key']
        item['info'] = item['name']
        print item['key']

    print len(items)

    invoice = {
            'lines': items,
            'customer_order_number': 'test',
            'key': 111,
            'delivery_date': datetime.now(),
            'posting_date': datetime.now() }
    deptor = db.deptors.find_one({ 'key': '87934210' })
    edi_fact = export.EDI()

    elem = edi_fact.create_element(invoice, deptor['gln'])
    print elem



