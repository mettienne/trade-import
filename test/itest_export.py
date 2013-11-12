import os.path
import re
import pytest
from utils import export

oio = export.OIOXML()


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

        invoice = db.salesinvoices.find_one({ 'key': number })
        deptor = db.deptors.find_one({ 'key': invoice['customer_number'] });
        lines_with_ean = [];
        for line in invoice['lines']:
            if not line['item_number']:
                continue
            if not line['ean']:
                item = db.items.find_one({ 'key': line['item_number'] });
                line['ean'] = item['ean']

            lines_with_ean.append(line);

        invoice['lines'] = lines_with_ean
        resp = oio.create_element(invoice, deptor['search_name'])
        valid = open(os.path.join('test','data','oio_xml',f))
        res = fold(resp.read())
        valid = fold(valid.read())
        #print '#'*10
        #print valid
        #print '#'*10
        #print res
        #print '#'*10
        assert valid == res

