import logging
from pymongo import MongoClient
import os.path
from . import config
from . import cli


logger = logging.getLogger(__name__)


def bootstrap(ean_file, columns, ean_index, ref_index, deptor_key, group):
    """Read a ean_file which contains some kind of mapping between ean/gln numbers
    and deptors.
    @Columns: expected number of columns on each line
    @ean_index: column index with ean number
    @ref_index: column index with deptor reference
    @deptor_key: what key does ref_index point to on a deptor
    @group: the edi group (handler) that the deptor belongs to"""

    conn = MongoClient(config.uri)
    db = conn.invoice

    with open(os.path.join(config.data_path, ean_file)) as f:
        updates = 0
        for l in f.readlines():
            res = l.split(';')
            if len(res) != columns:
                logger.exception(
                    Exception(
                        'More columns than expected in file {}'.format(ean_file)))
            deptor = db.deptors.find_one({deptor_key: res[ref_index]})
            if deptor:
                deptor['gln'] = res[ean_index].strip()
                deptor['gln_group'] = group
                db.deptors.save(deptor)

                logger.info('Updated deptor {}'.format(deptor['key']))
                updates += 1

        logger.info(
            'Total updates for {} from file {}: {}'.format(
                group,
                ean_file,
                updates))


def all():
    bootstrap('supergros.csv', 13, 11, 10, 'key', 'supergros')
    bootstrap('butik.csv', 10, 9, 0, 'search_name', 'dansksupermarked')

if __name__ == '__main__':
    class Mock():

        def run(self):
            all()
    cli.run('edi_ftp', Mock)
