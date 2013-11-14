import logging
from  pymongo import MongoClient
from bson.objectid import ObjectId
import cPickle as pickle
import os.path
import parsing
import navi_mappings as nm
import config
import daemon
import subprocess
import time
import signal
import setproctitle
from multiprocessing import Process, Pipe
from datetime import datetime, timedelta
import sys
import cli

logger = logging.getLogger(__name__)
connected = False

class Importer(daemon.Daemon):

    def __init__(self, app_name, *args, **kwargs):

        def signal_handler(signal, frame):
            self.close()
            logger.info('main thread cought exit')
            sys.exit('exiting')

        signal.signal(signal.SIGTERM, signal_handler)

        daemon.Daemon.__init__(self, app_name, *args, **kwargs)

        self.process = None
        if '27018' in config.uri:
            self.ssh()

        self.conn = MongoClient(config.uri)
        self.db = self.conn.invoice
        self.parser = parsing.Parser()

    def all(self):
        logger.info('starting all')
        self.import_collection(nm.Item(), self.db.items, config.item_file)
        self.contacts()
        self.invoices()
        logger.info('done with all')

    def invoices(self):
        logger.info('starting invoice import')
        self.import_inv_cred(config.sales_invoice_line, config.sales_invoice_head, nm.SalesInvoice(), self.db.salesinvoices)
        logger.info('done with invoice import')

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


    def import_collection(self, element, collection, filename, city_zip=False):
        split = self.parser.parse_file(filename)
        for i, line in enumerate(self.parser.get_lines(split)):
            if i % 100 == 0:
                logger.info('progress file {}: {}'.format(filename, i))

            obj = element.format(line, city_zip)
            collection.update({ 'key': obj.pop('key') },
                    { '$set': obj }, upsert=True)



    def import_inv_cred(self, lines_name, heads_filename, element, collection):
        parsed_lines = self.parser.parse_file(lines_name)
        result = {}

        line_element = nm.SalesInvCredLine()
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
            obj[nm.lines] = d_lines.get(key, [])
            collection.update({ 'key': key },
                    { '$set': obj }, upsert=True)


    def connect(self):

        def signal_handler(signal, frame):
            logger.info('ssh thread cought exit')
            process.terminate()


        signal.signal(signal.SIGTERM, signal_handler)
        setproctitle.setproctitle('ssh thread')
        logger.info('connecting')
        process = subprocess.Popen(['ssh', '-o', 'ConnectTimeout={}'.format(config.ssh_timeout),
            '-N', '-L', '27018:localhost:22282', config.mongoSSH],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output,stderr = process.communicate()

    def close(self):
        self.process.terminate()
        if conn:
            conn.close()

    def ssh(self):
        self.process = Process(target=self.connect)
        self.process.start()

        logger.info('checking if ssh thread timed out')
        time.sleep(config.ssh_timeout + 1)

        if not self.process.is_alive():
            logger.error('SSH connection failed')
        else:
            logger.info('ssh looks good, starting main loop')



    def run(self):
        try:
            last_run = None
            while True:
                if self.user_ssh and not self.process.is_alive():
                    raise Exception('SSH connection lost, exiting')

                now = datetime.now()
                #run once every hour and only in specified minute interval
                if now.minute > 30 and now.minute < 45 and (not last_run or now - last_run > timedelta(minutes=30)):
                    last_run = now
                    logger.info('Starting sync')
                    self.all()

                time.sleep(10)
                logger.info('Sleeping: {}'.format(now))

        except Exception as ex:
            self.close()
            logger.exception(ex)

if __name__ == '__main__':
    cli.run('import', Importer)


