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
import navi_mappings as nm
import logging
import config
import argparse

logger = logging.getLogger(__name__)

g_lines = {}
def all():
    import_collection(nm.Deptor(), db.deptors, config.deptor_file, True)
    import_collection(nm.Creditor(), db.creditors, config.creditor_file, True)
    import_collection(nm.Item(), db.items, config.item_file)

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Admin Server Help')
    parser.add_argument(
            '-c', '--config', type=str, nargs="*",
            help="List of configuration files to import (python modules)")
    parser.add_argument('method',
            help="all, invoices or the like")
    cmd_args = parser.parse_args()


    configure(cmd_args.config or [])
    conn = MongoClient(config.uri)
    db = conn.invoice
    parser = parsing.Parser()

    possibles = globals().copy()
    possibles.update(locals())
    method = possibles.get(cmd_args.method)
    if not method:
        raise Exception("Method %s not implemented" % method)
    method()


