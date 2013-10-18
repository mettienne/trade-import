#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
#import simplejson as json
from datetime import datetime
from  pymongo import MongoClient
from bson.objectid import ObjectId
import cPickle as pickle
import os.path
import parsing
import navi_mappings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

conn = MongoClient('localhost', 27017)
db = conn.invoice
path = 'text_values/'

lines = {}


def deptors():
    parser = parsing.Parser()
    db.deptors.remove()
    f = open(path+'debitor.txt', 'r')
    lines = get_lines(f)
    for l in lines:
        zip_code, city = parser.get_city(
                l[navi_mappings.deptor[navi_mappings.city_zip]],
                navi_mappings.deptor_key)
        obj = { k: l[v] for (k, v) in navi_mappings.deptor.iteritems() }
        obj[navi_mappings.zip] = zip_code
        obj[navi_mappings.city] = city
        db.deptors.insert(obj)

def creditors():
    parser = parsing.Parser()
    db.creditors.remove()
    f = open(path+'kreditor.txt', 'r')
    lines = get_lines(f)
    for l in lines:
        zip_code, city = parser.get_city(
                l[navi_mappings.creditor[navi_mappings.city_zip]],
                navi_mappings.creditor_key)
        obj = { k: l[v] for (k, v) in navi_mappings.creditor.iteritems() }
        obj[navi_mappings.zip] = zip_code
        obj[navi_mappings.city] = city
        db.creditors.insert(obj)


def get_lines(f):
    l = []
    for i, line in enumerate(f.xreadlines()):
        if line.strip() == '::':
            #yield [ x.strip() for x in ''.join(l).split(':')]
            yield l
            l = []
        else:
            l.append(unicode(line.strip()[:-1], 'CP850'))


def items():
    db.items.remove()

    f = open('text_values/vare.txt', 'r')
    lines = get_lines(f)
    for l in lines:
        db.items.insert({'_id': l[0],
                         'name' : l[2],
                         'cost_price': get_price(l[20]),
                         'price_0': get_price(l[16]),
                         'price_1': get_price(l[74]),
                         'price_2': get_price(l[75]),
                         'price_3': get_price(l[97]),
                         'price_4': get_price(l[98]),
                         'inner_box': int(l[76]),
                         'outer_box': int(l[77]),
                         'quantity': int(l[77]),
                         'group': l[108],
                        })

def invoices():
    db.salesinvoices.remove()
    #db.salescreditnotas.remove()
    create('salesinvoices')
    #create('creditnotas')

def create(type):
    p_file = 'pickle/{}.p'.format(type)

    if not os.path.isfile(p_file):
        if type == 'salesinvoices':
            f = open('text_values/salgsfakturalinie.txt', 'r')
        else:
            f = open('text_values/salgskreditnotalinie.txt', 'r')
        lines = get_lines(f)
        d_lines = create_creditnota_lines(lines)
        pickle.dump(d_lines, open( p_file, "wb" ))

    else:
        d_lines = pickle.load(open(p_file, "rb"))
    if type == 'salesinvoices':
        f2 = open('text_values/salgsfakturahovede.txt', 'r')
    else:
        f2 = open('text_values/salgskreditnotahovede.txt', 'r')

    lines2 = get_lines(f2)
    insert_creditnotas(lines2, d_lines, type)

def create_creditnota_lines(lines):
    #invoice = db.invoices.find_one({'fields.number': l[1]})
    #if not invoice:
        #return

    d_lines = {}
    for i, l in enumerate(lines):
        if i % 10000 == 0:
            print i
        #if i > 10000:
            #return d_lines
        if l[12]:
            try:
                qty = int(l[12].replace('.', ''))
            except Exception as e:
                qty = 0
                print e, l[4]
        else:
            qty = 0

        d_lines.setdefault(l[1], []).append(
            {'number': l[4],
             'info': l[9],
             'quantity': qty,
             'price': get_price(l[13]),
             'total_without_tax': get_price(l[20]),
             'total_with_tax': get_price(l[21]),
             'ean': l[42]
             })

    return d_lines

def insert_creditnotas(lines, d_lines, type):

    for i, l in enumerate(lines):
        if i % 100 == 0:
            print i

        zip_code, city = get_city(l[7])
        if type == 'salesinvoices':
            el = db.salesinvoices
            post_num = 18
        else:
            el = db.salescreditnotas
            post_num = 17

        try:
            order_date = datetime.strptime(l[17], '%d-%m-%y')
        except Exception as e:
            #print l[0], e
            #continue
            order_date = ''
        try:
            posting_date = datetime.strptime(l[post_num], '%d-%m-%y')
        except Exception as e:
            #print l[0], e
            #continue
            #raise e
            posting_date = ''


        el.insert({'customer_number': l[0],
                            'number': l[1],
                            'name': l[3],
                            'name2': l[4],
                            'address': l[5],
                            'address2': l[6],
                            'zip': zip_code,
                            'city': city,
                            'attention': l[8],
                            'customer_order_number': l[76],
                            'edi': l[72],
                            'order_date': order_date,
                            'posting_date': posting_date,
                            'total_with_tax': get_price(l[68]),
                            'lines': d_lines.get(l[1], []),
                            })
if __name__ == '__main__':
    #get_invoices(*)
    possibles = globals().copy()
    possibles.update(locals())
    method = possibles.get(sys.argv[1])
    if not method:
        raise Exception("Method %s not implemented" % method)
    method(*sys.argv[2:])
