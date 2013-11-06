import config
import json
from utils.amqp import BlockingAMQP
from utils.export import OIOXML
from  pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)


class DS():

    def __init__(self):
        self.oio = OIOXML()
        amqp = BlockingAMQP(on_message=self.on_message, host=config.amqp_host)
        try:
            amqp.start()
        except (KeyboardInterrupt, SystemExit):
            self.amqp.stop()
            raise



    def on_message(self, body):
        try:
            element = json.loads(body)
            res = self.oio.create_element(element['invoice'], element['deptor'])
            res.seek(0)
            print res.read()
            res.close()
            return json.dumps({ 'success': True })
        except Exception as ex:
            print ex
            logger.exception(ex)
            return json.dumps({ 'success': False, 'message': str(ex) })

    #channel.basic_ack(method.delivery_tag)


if __name__ == '__main__':
    config.configure([])
    DS()



