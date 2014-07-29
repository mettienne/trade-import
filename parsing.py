import logging
from datetime import datetime
import os
import config
logger = logging.getLogger(__name__)

class MalformedException(Exception):
    pass


class Parser():

    def get_email(self, string, key=''):
        email = string.replace('$', '@')
        if email and not '@' in email:
            logger.warning('invalid email, {}'.format(key))
        return email

    def get_price(self, string, key=''):
        if not string:
            return 0
        multiplier = 1
        if ',' in string:
            _, decs = string.split(',')
            if len(decs) == 1:
                multiplier = 10

        if ',' in string:
            price = int(string.replace('.', '').replace(',', '')) * multiplier
        else:
            price = int(string.replace('.', '')) * 100

        return price

    def get_city(self, string, key, log=True):
        res = [x for x in string.split() if x]
        if not res:
            if log:
                logger.warning('city_zip: empty, {}'.format(key))
            return '', ''
        if res[0].isdigit():
            return (res[0], ' '.join(res[1:]))
        else:
            if log:
                logger.warning('city_zip: invalid format, {}, {}'.format(key, string.encode('utf8')))
            return '', string

    def parse_file(self, filename):
        f = open(os.path.join(config.path, filename), 'r')
        return unicode(f.read(), 'CP850').split('\r\n')[:-1]

    def get_lines(self, f):
        l = []
        last_line = ''
        for i, line in enumerate(f):
            line = line.strip()
            last_line = line
            if line.strip() == '::':
                yield l
                l = []
            else:
                if line[-1] != ':':
                    raise Exception('Line not properly ended {}'.format(line))
                l.append(line[:-1])

        if last_line != '::':
            raise Exception('File not properly ended line {}, {}'.format(i, last_line))

    def get_qty(self, string, key):
        qty = 0
        try:
            qty = int(string.replace('.', ''))
        except Exception as e:
            logger.warning('quantity: invalid format, {}, {}'.format(key, string.encode('utf8')))

        #if qty < 0:
            #logger.warning('negative quantity: {}, {}'.format(key, string.encode('utf8')))

        return qty

    def get_date(self, string, key, log=True):
        try:
            return datetime.strptime(string, '%d-%m-%y')
        except:
            if log:
                logger.warning('date invalid: {}, {}'.format(key, string.encode('utf8')))
            return ''

