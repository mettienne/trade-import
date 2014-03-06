import logging
import os.path
import sys
import logging_config
module = sys.modules[__name__]

### IMPORTING
path = '/export'
item_file = 'vare.txt'
sales_invoice_line = 'salgsfakturalinie.txt'
sales_invoice_head = 'salgsfakturahovede.txt'
purchase_invoice_line = 'kobsfakturalinie.txt'
purchase_invoice_head = 'kobsfakturahovede.txt'
sales_creditnota_line = 'salgskreditnotalinie.txt'
sales_creditnota_head = 'salgskreditnotahovede.txt'
purchase_creditnota_line = 'kobskreditnotalinie.txt'
purchase_creditnota_head = 'kobskreditnotahoved.txt'
cust_order_numbers = 'kundeordrenumre.txt'
item_entries = 'varepost.txt'
deptor_entries = 'debitorpost.txt'
deptor_file = 'debitor.txt'
creditor_file = 'kreditor.txt'
creditor_entries = 'kreditorpost.txt'
finance_entries = 'finanspost.txt'
bootstrap_path = 'bootstrap'
accounts = 'finanskonti.txt'

### DATABASE
uri = "mongodb://localhost:27017/invoice"

### rsync

rsync_user = 'nelly'
rsync_host = '90.185.144.43'
rsync_dir = '/'

superbest_proxy = 'nelly@90.185.144.43'

mongoSSH = "ettienne@ettienne.webfactional.com"
ssh_timeout = 5

### AMQP
amqp_host = 'localhost'
amqp_user = 'guest'
amqp_password = 'guest'

amqp_queue = 'test'

### GLOBAL SETTINGS

log_dir = '/apps/log'
supervisor_dir = '/etc/supervisor.d'
apps_dir = '/apps'

### TRADEHOUSE SETTINGS


trade_cvr = '26704561'
trade_ean = '90000' + trade_cvr

cur_dir = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.join(cur_dir, 'data')

### DS FTP
ds_server = 'ettienne.webfactional.com'
ds_user = 'navigator'
ds_password = ''

### supergros FTP
supergros_server = 'ettienne.webfactional.com'
supergros_user = 'navigator'
supergros_password = ''


test_edi = True
use_proxy = False

def configure(config_files):

    def load_config_file(config_file):
        print "Loading", config_file
        cfg = {}
        execfile(config_file, {}, cfg)
        for key, value in cfg.items():
            if not hasattr(module, key):
                raise Exception("Unknown config variable in {}:"
                                " {}".format(config_file, key))
            setattr(module, key, value)

    for config_file in config_files:
        load_config_file(config_file)
