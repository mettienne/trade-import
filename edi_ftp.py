import logging_config
logging_config.configure('edi_ftp')
import config
import ftplib
import json
from utils.amqp import BlockingAMQP
from utils.export import OIOXML
from  pymongo import MongoClient
import logging
logger = logging.getLogger(__name__)



class DS():

    def __init__(self):
        logger.info('Starting DS amqp handler')
        self.oio = OIOXML()
        amqp = BlockingAMQP(on_message=self.on_message,
                host=config.amqp_host,
                user=config.amqp_user,
                password=config.amqp_password)
        try:
            amqp.start()
        except (KeyboardInterrupt, SystemExit):
            self.amqp.stop()
            raise



    def on_message(self, body):
        try:
            element = json.loads(body)
            xml_file = self.oio.create_element(element['invoice'], element['deptor'])
            self.do_ftp(xml_file, element['invoice']['key'])
            xml_file.close()
            return json.dumps({ 'success': True })
        except Exception as ex:
            print ex
            logger.exception(ex)
            return json.dumps({ 'success': False, 'message': str(ex) })

    #channel.basic_ack(method.delivery_tag)

    def do_ftp(self, xml_file, number):
        print config.ftp_server
        ftp = ftplib.FTP(config.ftp_server)
        ftp.login(config.ftp_user, config.ftp_password)

        ftp.cwd('invoice')
        ftp.storbinary('STOR {}.xml'.format(number), xml_file)
        logging.info('FTP uploaded file: {}'.format(number))
        ftp.close()

if __name__ == '__main__':
    config.configure([])
    DS()



