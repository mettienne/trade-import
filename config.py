import logging
import os.path
import sys
import logging_config
module = sys.modules[__name__]

### IMPORTING
path = 'text_values'
deptor_file = 'debitor.txt'
creditor_file = 'kreditor.txt'
item_file = 'vare.txt'
sales_invoice_line = 'salgsfakturalinie.txt'
sales_invoice_head = 'salgsfakturahovede.txt'
cust_order_numbers = 'kundeordrenumre.txt'

### DATABASE
uri = "mongodb://localhost:27017/invoice"

mongoSSH = "ettienne@ettienne.webfactional.com"
ssh_timeout = 5

### AMQP
amqp_host = 'localhost'
amqp_user = 'guest'
amqp_password = 'guest'

### GLOBAL SETTINGS

log_dir = '/apps/log'
pid_dir = '/apps/pid'
monit_dir = '/apps/monit'
apps_dir = '/apps'
config_dir = '/apps/config'

extra_config = os.path.join(config_dir, "trade_tools.py")

### TRADEHOUSE SETTINGS


trade_cvr = '26704561'
trade_ean = '90000' + trade_cvr

cur_dir = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.join(cur_dir, 'data')

env = 'test' # or prod

### DS FTP
#server = '217.10.25.76'
#user = 'TradeHouseDenmark'
#password = 'xX!mc6Z1'
ftp_server = 'ettienne.webfactional.com'
ftp_user = 'navigator'
ftp_password = ''


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

    if os.path.exists(extra_config):
        load_config_file(extra_config)

    for config_file in config_files:
        load_config_file(config_file)
