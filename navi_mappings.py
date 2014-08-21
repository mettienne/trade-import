import parsing
import sys
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

update_key = 'last_updated'
city = 'city'
zip = 'zip'
lines = 'lines'
comments = 'comments'

parser = parsing.Parser()

def string(string, key):
    return string

def to_int(string, key):
    try:
        return int(string)
    except:
        logger.warning('could not get int {}, key {}'.format(repr(string), key))

    return 0

class NaviObject():

    def get_atts(self):
        return self.__dict__

    def format(self, line, city_zip=False):
        obj = {}
        for k, vals in self.get_atts().iteritems():
            v, trans = vals[0], vals[1]
            rest = vals[2] if len(vals) == 3 else {}

            if city_zip and k == 'city_zip':
                obj[zip], obj[city] = parser.get_city(line[self.city_zip[0]], line[self.key[0]], **rest)
                continue
            obj[k] = trans(line[v], line[self.key[0]], **rest)

        obj[update_key] = datetime.utcnow()
        #obj[.zip_code, self.city = parser.get_city(line[self.city_zip[0]], line[self.key[0]])
        return obj



class Deptor(NaviObject):

    def __init__(self):
        self.key = (0, string)
        self.name  = (1, string)
        self.search_name  = (2, string)
        self.address = (4, string)
        self.city_zip = (6, string)
        self.attention = (7, string)
        self.phone = (8, string)
        self.fax = (79, string)
        self.email = (89, parser.get_email)

class Creditor(NaviObject):

    def __init__(self):
        self.key = (0, string)
        self.name  = (1, string)
        self.address = (4, string)
        self.city_zip = (6, string)
        self.attention = (7, string)
        self.phone = (8, string)
        self.fax = (62, string)


class Item(NaviObject):

    def __init__(self):
        self.key = (0, string)
        self.name  = (2, string)
        self.cost_price = (20, parser.get_price)
        self.price = (16, parser.get_price)
        self.price_1 = (74, parser.get_price)
        self.price_2 = (75, parser.get_price)
        self.price_3 = (97, parser.get_price)
        self.price_4 = (98, parser.get_price)
        self.outer_box = (76, parser.get_qty)
        self.inner_box = (77, parser.get_qty)
        self.quantity = (78, parser.get_qty)
        self.ean = (81, string)
        self.group = (108, string)
        self.in_stock = (58, string)
        # we do not want to use navi as authoritative here
        #self.gln_number = (135, string)

class SalesInvCredLine(NaviObject):

    def __init__(self):
        self.key = (1, to_int)
        self.item_number = (4, string)
        self.info = (9, string)
        self.quantity = (12, parser.get_qty)
        self.price = (13, parser.get_price)
        self.total_without_tax = (20, parser.get_price)
        self.total_with_tax = (21, parser.get_price)
        self.ean = (42, string)

class PurchaseInvCredLine(NaviObject):

    def __init__(self):
        self.key = (1, to_int)
        self.item_number = (4, string)
        self.info = (8, string)
        self.quantity = (11, parser.get_qty)
        self.price = (12, parser.get_price)
        self.total_without_tax = (19, parser.get_price)
        self.total_with_tax = (20, parser.get_price)

class SalesInvoice(NaviObject):

    def __init__(self):
        self.customer_number = (0, string)
        self.key = (1, to_int)
        self.name = (3, string)
        self.name_1 = (4, string)
        self.address = (5, string)
        self.address_1 = (6, string)
        self.city_zip = (7, string, { 'log': False })
        self.attention = (8, string)
        self.order_date = (17, parser.get_date, {'log': False })
        self.posting_date = (18, parser.get_date, {'log': False})
        self.delivery_date = (19, parser.get_date, {'log': False})
        self.account = (29, parser.get_posting_group)
        self.total_with_tax = (68, parser.get_price)
        self.edi = (72, string)
        self.customer_order_number = (76, string)

class PurchaseInvoice(NaviObject):

    def __init__(self):
        self.supplier_number = (0, string)
        self.key = (1, to_int)
        self.name = (3, string)
        self.name_1 = (4, string)
        self.address = (5, string)
        self.address_1 = (6, string)
        self.city_zip = (7, string, { 'log': False })
        self.attention = (8, string)
        self.order_date = (17, parser.get_date, { 'log': False })
        self.posting_date = (18, parser.get_date)
        self.creditor_invoice_number = (43, to_int)

class SalesCreditnota(NaviObject):

    def __init__(self):
        self.customer_number = (0, string)
        self.key = (1, to_int)
        self.name = (3, string)
        self.name_1 = (4, string)
        self.address = (5, string)
        self.address_1 = (6, string)
        self.city_zip = (7, string, { 'log': False })
        self.attention = (8, string)
        self.posting_date = (17, parser.get_date)
        self.account = (23, parser.get_posting_group)

class PurchaseCreditnota(NaviObject):

    def __init__(self):
        self.supplier_number = (0, string)
        self.key = (1, to_int)
        self.name = (3, string)
        self.name_1 = (4, string)
        self.address = (5, string)
        self.address_1 = (6, string)
        self.city_zip = (7, string, { 'log': False })
        self.attention = (8, string)
        self.posting_date = (17, parser.get_date)
        self.creditor_creditnota_number = (35, to_int)

class ItemEntry(NaviObject):

    def __init__(self):
        self.key = (0, parser.get_qty)
        self.item_number = (1, string)
        self.date = (2, parser.get_date)
        self.type = (3, string)
        self.record_number = (5, to_int)
        #self.contact_number = (5, to_int)
        self.quantity = (10, parser.get_qty)
        self.item_price = (13, parser.get_price)
        self.total_price = (15, parser.get_price)
        self.item_group = (37, string)

class DeptorEntry(NaviObject):

    def __init__(self):
        self.key = (0, parser.get_qty)
        self.deptor_number = (1, string)
        #self.date = (2, parser.get_date)
        #self.type = (3, string)
        self.record_number = (4, to_int)
        self.amount = (7, parser.get_price)
        self.customer_number = (15, string)
        self.posting_group = (16, string)

class CreditorEntry(NaviObject):

    def __init__(self):
        self.key = (0, parser.get_qty)
        self.creditor_number = (1, string)
        self.date = (2, parser.get_date)
        self.type = (3, string)
        self.record_number = (4, to_int)
        self.amount = (7, parser.get_price)
        self.posting_group = (15, string)


class FinanceEntry(NaviObject):

    def __init__(self):
        self.key = (0, parser.get_qty)
        self.account_number = (1, string)
        self.date = (2, parser.get_date)
        self.type = (3, string)
        self.record_number = (4, to_int)
        self.text = (5, string)
        self.tax_code = (6, string)
        self.offsetting_account = (7, string)
        self.amount = (8, parser.get_price)

class Account(NaviObject):

    def __init__(self):
        self.key = (0, string)
        self.name = (1, string)
        self.type = (3, string)
        self.tax_code = (6, string)
        self.art = (7, string)

