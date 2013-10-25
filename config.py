import logging
import os.path
logging.basicConfig(level=logging.WARNING, filename='import.log', filemode='w')
#logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.WARNING)


path = 'text_values'
deptor_file = 'debitor.txt'
creditor_file = 'kreditor.txt'
item_file = 'vare.txt'
sales_invoice_line = 'salgsfakturalinie.txt'
sales_invoice_head = 'salgsfakturahovede.txt'
uri = "mongodb://localhost/invoice"

home_dir = os.path.expanduser("~")
home_config = os.path.join(home_dir, ".trade_tools.config.py")
