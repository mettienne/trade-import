import logging_config
import config
import ftplib
import json
import cli
import uuid
from utils.amqp import BlockingAMQP
from utils.export import OIOXML
from utils import export
import logging
import socket
from utils import socks
logger = logging.getLogger(__name__)



class DS():

    def run(self):
        logger.info('Starting DS amqp handler')
        self.oio = export.OIOXML()
        self.edi = export.EDI()
        amqp = BlockingAMQP(
                config.amqp_queue,
                on_message=self.on_message,
                host=config.amqp_host,
                user=config.amqp_user,
                password=config.amqp_password)
        try:
            amqp.start()
        except (KeyboardInterrupt, SystemExit) as ex:
            logger.exception(ex)
        except Exception as ex:
            logger.exception(ex)
            raise



    def on_message(self, body):
        try:
            logger.info('recieved message')
            element = json.loads(body)
            group = element['deptor'].get('gln_group')
            if group == 'supergros':
                xml_file = self.edi.create_element(element['invoice'], element['deptor'], test=element.get('test', False))
                self.send_supergros(xml_file)
            elif group == 'dansksupermarked':
                xml_file = self.oio.create_element(element['invoice'], element['deptor'], test=element.get('test', False))
                self.send_ds(xml_file)
            else:
                message = 'GLN-gruppe {} er ukendt'.format(group)
                return json.dumps({ 'success': False, 'message': message })

            xml_file.close()
            return json.dumps({ 'success': True })
        except Exception as ex:
            logger.exception(ex)
            return json.dumps({ 'success': False, 'message': str(ex) })

    def send_ds(self, xml_file):
        logger.info('ftp-ing to dansk supermarked')
        ftp = ftplib.FTP(config.ds_server)
        ftp.login(config.ds_user, config.ds_password)
        ftp.cwd('invoice')
        self.do_ftp(ftp, xml_file)

    def send_supergros(self, xml_file):

        if config.use_proxy:
            logger.info('connecting to proxy')
            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5,"127.0.0.1", 9999)
            socket.socket = socks.socksocket

        logger.info('ftp-ing ro supergros')
        ftp = ftplib.FTP(config.supergros_server)
        ftp.login(config.supergros_user, config.supergros_password)
        ftp.cwd('PROD/EDISGR/D0901-FROM-EDISGR')
        self.do_ftp(ftp, xml_file)

    def do_ftp(self, ftp, xml_file):
        logger.info('Server message: {}'.format(ftp.getwelcome()))
        name = uuid.uuid1()
        ftp.storbinary('STOR {}.txt'.format(name), xml_file)
        logging.info('FTP uploaded file: {}'.format(name))
        ftp.close()


if __name__ == '__main__':
    cli.run('edi_ftp', DS)
