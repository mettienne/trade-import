import logging
logger = logging.getLogger(__name__)

class MalformedException(Exception):
    pass


class Parser():

    def get_price(self, string):
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


    def get_city(self, string, key):
        res = [x for x in string.split() if x]
        if not res:
            logger.warning('city_zip: empty')
            return '', '' 
        if res[0].isdigit():
            return (res[0], ' '.join(res[1:]))
        else:
            logger.warning('city_zip: {}, {}'.format(key, string.encode('utf8')))
            return '', string


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
                    raise Exception('Line not properly ended')
                l.append(unicode(line[:-1].strip(), 'CP850'))

        if last_line != '::':
            raise Exception('File not properly ended')

