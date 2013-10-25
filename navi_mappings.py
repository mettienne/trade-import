import parsing
import sys
from datetime import datetime
module = sys.modules[__name__]

deptor_key = '_id'
creditor_key = '_id'
item_key = '_id'
salesinvoice_key = '_id'
sales_inv_cred_key = '_id'
inv_cred_line_key = 'number'

sales_inv_posting_num = 18
sales_cred_posting_num = 17
order_date_num = 17

city_zip = 'city_zip'
zip = 'zip'
city = 'city'
name = 'name'
name_1 = 'name_1'
address = 'address'
address_1 = 'address_1'
attention = 'attention'
phone = 'phone'
fax = 'fax'
search_name = 'search_name'
price_0 = 'price_0'
price_1 = 'price_1'
price_2 = 'price_2'
price_3 = 'price_3'
price_4 = 'price_4'
price = 'price'
cost_price = 'cost_price'
inner_box = 'inner_box'
outer_box = 'outer_box'
quantity = 'quantity'
group = 'group'
info = 'info'
total_without_tax = 'total_without_tax'
total_with_tax = 'total_with_tax'
ean = 'ean'
edi = 'edi'
order_date = 'order_date'
posting_date = 'posting_date'
customer_number = 'customer_number'
customer_order_number = 'customer_order_number'
lines = 'lines'

update_key = 'last_updated'
parser = parsing.Parser()

def string(string, key):
    return string

class NaviObject():

    def get_atts(self):
        return self.__dict__

    def format(self, line, city_zip=False):
        obj = {}
        for k, vals in self.get_atts().iteritems():
            v, trans = vals[0], vals[1]
            rest = vals[2] if len(vals) == 3 else {}

            if city_zip and k == 'city_zip':
                obj[zip], obj[city] = parser.get_city(line[self.city_zip[0]], line[self._id[0]], **rest)
                continue
            obj[k] = trans(line[v], line[self._id[0]], **rest)

        obj[update_key] = datetime.utcnow()
        #obj[.zip_code, self.city = parser.get_city(line[self.city_zip[0]], line[self._id[0]])
        return obj



class Deptor(NaviObject):

    def __init__(self):
        self._id = (0, string)
        self.name  = (1, string)
        self.search_name  = (2, string)
        self.address = (4, string)
        self.city_zip = (6, string)
        self.attention = (7, string)
        self.phone = (8, string)
        self.fax = (79, string)

class Creditor(NaviObject):

    def __init__(self):
        self._id = (0, string)
        self.name  = (1, string)
        self.address = (4, string)
        self.city_zip = (6, string)
        self.attention = (7, string)
        self.phone = (8, string)
        self.fax = (62, string)


class Item(NaviObject):

    def __init__(self):
        self._id = (0, string)
        self.name  = (2, string)
        self.cost_price = (20, parser.get_price)
        self.price = (16, parser.get_price)
        self.price_1 = (74, parser.get_price)
        self.price_2 = (75, parser.get_price)
        self.price_3 = (97, parser.get_price)
        self.price_4 = (98, parser.get_price)
        self.inner_box = (76, parser.get_qty)
        self.outer_box = (77, parser.get_qty)
        self.quantity = (77, parser.get_qty)
        self.group = (108, string)

class SalesInvCredLine(NaviObject):

    def __init__(self):
        self._id = (1, string)
        self.inv_cred_line_key = (4, string)
        self.info = (9, string)
        self.quantity = (12, string)
        self.price = (13, parser.get_price)
        self.total_without_tax = (20, parser.get_price)
        self.total_with_tax = (21, parser.get_price)
        self.ean = (42, string)

class SalesInvoice(NaviObject):

    def __init__(self):
        self.customer_number = (0, string)
        self._id = (1, string)
        self.name = (3, string)
        self.name_1 = (4, string)
        self.address = (5, string)
        self.address_1 = (6, string)
        self.city_zip = (7, string, { 'log': False })
        self.attention = (8, string)
        self.order_date = (17, parser.get_date, { 'log': False })
        self.posting_date = (18, parser.get_date)
        self.total_with_tax = (68, parser.get_price)
        self.edi = (72, string)
        self.customer_order_number = (76, string)

class SalesCreditNota(NaviObject):

    def __init__(self):
        self.customer_number = (0, string)
        self._id = (1, string)
        self.name = (3, string)
        self.name_1 = (4, string)
        self.address = (5, string)
        self.address_1 = (6, string)
        self.city_zip = (7, string, { 'log': False })
        self.attention = (8, string)
        self.posting_date = (17, parser.get_date)
        self.total_with_tax = (68, parser.get_price)
        self.edi = (72, string)
        self.customer_order_number = (76, string)
