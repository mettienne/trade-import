from . import config
from pymongo import MongoClient

conn = MongoClient(config.uri)
db = conn.invoice
print db.sale.update({}, {'$unset': {'item_entries': ''}}, multi=True)


print db.sale.remove({'type': {'$exists': False}}, multi=True)
