import parser
import sys
module = sys.modules[__name__]

deptor_key = 'number'
creditor_key = 'number'

city_zip = 'city_zip'
zip = 'zip'
city = 'city'
name = 'name'
address = 'address'
attention = 'attention'
phone = 'phone'
fax = 'fax'
search_name = 'search_name'

deptor = {
        deptor_key: 0,
        name : 1,
        search_name : 2,
        address: 4,
        city_zip: 6,
        attention: 7,
        phone: 8,
        fax: 79
        }

creditor = {
        creditor_key: 0,
        name : 1,
        address: 4,
        city_zip: 6,
        attention: 7,
        phone: 8,
        fax: 62
        }
