from  pymongo import MongoClient
from bson.objectid import ObjectId
import cPickle as pickle
import os.path
import parsing
import navi_mappings as nm
import logging
import config
import argparse
import subprocess
import time
import signal
from multiprocessing import Process, Pipe
from datetime import datetime, timedelta
logging.basicConfig(level=config.log_level)
logger = logging.getLogger(__name__)

connected = False

def all():
    import_collection(nm.Deptor(), db.deptors, config.deptor_file, True)
    import_collection(nm.Creditor(), db.creditors, config.creditor_file, True)
    import_collection(nm.Item(), db.items, config.item_file)
    invoices()

def import_collection(element, collection, filename, city_zip=False):
    split = parser.parse_file(filename)
    for i, line in enumerate(parser.get_lines(split)):
        if i % 100 == 0:
            logger.info('progress file {}: {}'.format(filename, i))

        obj = element.format(line, city_zip)
        collection.update({ '_id': obj.pop('_id') },
                { '$set': obj }, upsert=True)


def invoices():
    import_inv_cred(config.sales_invoice_line, config.sales_invoice_head, nm.SalesInvoice(), db.salesinvoices)

def import_inv_cred(lines_name, heads_filename, element, collection):
    parsed_lines = parser.parse_file(lines_name)
    result = {}

    line_element = nm.SalesInvCredLine()
    lines = parser.get_lines(parsed_lines)
    for i, l in enumerate(lines):
        if i % 10000 == 0:
            logger.info('processed lines: {}'.format(i))

        obj = line_element.format(l, False)
        result.setdefault(obj.pop('_id'), []).append(obj)

    parsed_heads = parser.parse_file(heads_filename)
    insert_creditnotas(parsed_heads, result, element, collection)


def insert_creditnotas(parsed_heads, d_lines, element, collection):
    for i, line in enumerate(parser.get_lines(parsed_heads)):
        if i % 100 == 0:
            logger.info('progress file {}: {}'.format('inv/cred', i))

        obj = element.format(line, True)
        _id = obj.pop('_id')
        obj[nm.lines] = d_lines.get(_id, [])
        collection.update({ '_id': _id },
                { '$set': obj }, upsert=True)

def configure(config_files):

    def load_config_file(config_file):
        print "Loading", config_file
        cfg = {}
        execfile(config_file, {}, cfg)
        for key, value in cfg.items():
            if not hasattr(config, key):
                raise Exception("Unknown config variable in {}:"
                                " {}".format(config_file, key))
            setattr(config, key, value)

    if os.path.exists(config.home_config):
        load_config_file(config.home_config)

    for config_file in config_files:
        load_config_file(config_file)

def connect():

    def signal_handler(signal, frame):
        process.terminate()

    signal.signal(signal.SIGTERM, signal_handler)
    logger.info('connecting')
    process = subprocess.Popen(['ssh', '-o', 'ConnectTimeout={}'.format(config.ssh_timeout),
        '-N', '-L', '27018:localhost:22282', config.mongoSSH],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output,stderr = process.communicate()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Admin Server Help')
    parser.add_argument(
            '-c', '--config', type=str, nargs="*",
            help="List of configuration files to import (python modules)")
    parser.add_argument('-m', '--method',
            help="all, invoices or the like")
    cmd_args = parser.parse_args()


    configure(cmd_args.config or [])

    process = Process(target=connect)
    process.start()

    logger.info('checking if ssh thread timed out')
    time.sleep(config.ssh_timeout + 1)

    if not process.is_alive():
        logger.error('SSH connection failed')

    conn = None
    try:
        conn = MongoClient(config.uri)
        db = conn.invoice
        parser = parsing.Parser()

        if cmd_args.method:
            possibles = globals().copy()
            possibles.update(locals())
            method = possibles.get(cmd_args.method)
            method()
        else:
            last_run = None
            while True:
                now = datetime.now()
                #run once every hour and only in specified minute interval
                if now.minute > 30 and now.minute < 45 and (not last_run or now - last_run > timedelta(minutes=30)):
                    last_run = now
                    logger.info('Starting sync')
                    all()

                time.sleep(10)
                logger.info('Sleeping: {}'.format(now))



    except Exception as ex:
        process.terminate()
        if conn:
            conn.close()

    process.terminate()


