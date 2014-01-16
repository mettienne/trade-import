import logging
from  pymongo import MongoClient
import os.path
import parsing
import navi_mappings as nm
import config
import cli

logger = logging.getLogger(__name__)
connected = False

class Importer(object):

    def __init__(self, app_name):

        self.conn = MongoClient(config.uri)
        self.db = self.conn.invoice
        self.parser = parsing.Parser()

    def all(self):
        logger.info('starting all')
        self.contacts()
        self.salescreditnotas()
        self.salesinvoices()
        self.purchaseinvoices()
        self.purchasecreditnotas()
        self.entries()
        logger.info('done with all')

    def items(self):
        self.import_collection(nm.Item(), self.db.items, config.item_file)

    def bootstrap(self):
        def get_boot(name):
            name, ext = name.split('.')
            return os.path.join(config.bootstrap_path, '{}bootstrap.{}'.format(name, ext))
        self.speed_import_collection(nm.ItemEntry(), self.db.itementries, get_boot(config.item_entries))
        self.speed_import_collection(nm.DeptorEntry(), self.db.deptorentries, get_boot(config.deptor_entries))
        self.speed_import_collection(nm.CreditorEntry(), self.db.creditorentries, get_boot(config.creditor_entries))

    def entries(self):
        logger.info('starting entry import')
        self.import_collection(nm.ItemEntry(), self.db.itementries, config.item_entries)
        self.import_collection(nm.CreditorEntry(), self.db.creditorentries, config.creditor_entries)
        self.import_collection(nm.DeptorEntry(), self.db.deptorentries, config.deptor_entries)
        logger.info('done with entry import')

    def salesinvoices(self):
        logger.info('starting sales invoice import')
        self.import_inv_cred(config.sales_invoice_line, config.sales_invoice_head,
                nm.SalesInvoice(), self.db.salesinvoices, nm.SalesInvCredLine())
        logger.info('done with sales invoice import')

    def purchaseinvoices(self):
        logger.info('starting purchase invoice import')
        self.import_inv_cred(config.purchase_invoice_line, config.purchase_invoice_head,
                nm.PurchaseInvoice(), self.db.purchaseinvoices, nm.PurchaseInvCredLine())
        logger.info('done with purchase invoice import')

    def salescreditnotas(self):
        logger.info('starting sales creditnota import')
        self.import_inv_cred(config.sales_creditnota_line, config.sales_creditnota_head,
                nm.SalesCreditnota(), self.db.salescreditnotas, nm.SalesInvCredLine())
        logger.info('done with sales creditnota import')

    def purchasecreditnotas(self):
        logger.info('starting purchase creditnota import')
        self.import_inv_cred(config.purchase_creditnota_line, config.purchase_creditnota_head,
                nm.PurchaseCreditnota(), self.db.purchasecreditnotas, nm.PurchaseInvCredLine())
        logger.info('done with purchase creditnota import')

    def contacts(self):
        logger.info('starting contacts import')
        self.import_collection(nm.Deptor(), self.db.deptors, config.deptor_file, True)
        self.import_collection(nm.Creditor(), self.db.creditors, config.creditor_file, True)
        logger.info('done with contacts import')

    def order_numbers(self):
        logger.info('starting order numbers import')
        for line in open(os.path.join(config.path, config.cust_order_numbers), 'r'):
            invoice_number, order_number = line.strip().split(',')[:2]
            self.db.salesinvoices.update({ 'key': invoice_number }, { '$set': { 'customer_order_number': order_number }})
        logger.info('done with order numbers import')


    def speed_import_collection(self, element, collection, filename, city_zip=False):
        """imports data in chunks,
        expects that the collection is initially empty"""

        split = self.parser.parse_file(filename)
        lines = []
        for i, line in enumerate(self.parser.get_lines(split)):
            if i % 100 == 0:
                logger.info('progress file {}: {}'.format(filename, i))

            obj = element.format(line, city_zip)
            lines.append(obj)
            if len(lines) >= 10:
                collection.insert(lines)
                lines = []

        if lines:
            collection.insert(lines)

    def import_collection(self, element, collection, filename, city_zip=False):
        split = self.parser.parse_file(filename)
        for i, line in enumerate(self.parser.get_lines(split)):
            if i % 100 == 0:
                logger.info('progress file {}: {}'.format(filename, i))

            obj = element.format(line, city_zip)
            collection.update({ 'key': obj.pop('key') },
                    { '$set': obj }, upsert=True)

    def import_inv_cred(self, lines_name, heads_filename, element, collection, line_element):
        parsed_lines = self.parser.parse_file(lines_name)
        result = {}

        lines = self.parser.get_lines(parsed_lines)
        for i, l in enumerate(lines):
            if i % 10000 == 0:
                logger.info('processed lines: {}'.format(i))

            obj = line_element.format(l, False)
            result.setdefault(obj.pop('key'), []).append(obj)

        parsed_heads = self.parser.parse_file(heads_filename)
        self.insert_creditnotas(parsed_heads, result, element, collection)

    def insert_creditnotas(self, parsed_heads, d_lines, element, collection):
        for i, line in enumerate(self.parser.get_lines(parsed_heads)):
            if i % 100 == 0:
                logger.info('progress file {}: {}'.format('inv/cred', i))

            obj = element.format(line, True)
            key = obj.pop('key')
            lines = d_lines.get(key, [])
            comments = []
            final_lines = []
            for line in lines:
                if line['quantity'] == 0:
                    if line['info']:
                        comments.append(line['info'])
                else:
                    final_lines.append(line)

            obj[nm.lines] = final_lines
            obj[nm.comments] = comments
            collection.update({ 'key': key },
                    { '$set': obj }, upsert=True)


if __name__ == '__main__':
    cli.run('import', Importer)


