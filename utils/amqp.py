import pika
import logging

logger = logging.getLogger(__name__)

class BlockingAMQP():

    def __init__(self, on_message=None, host='localhost', 
            user='guest', password='guest'):
        credentials = pika.PlainCredentials(user, password)
        params = pika.connection.ConnectionParameters(
                host=host,
                credentials=credentials)
        self.connection = pika.BlockingConnection(
                parameters=params)

        self.channel = self.connection.channel()
        self.channel.queue_declare(queue="test", durable=False, exclusive=False, auto_delete=True)

        self.on_message = on_message

        self.channel.basic_consume(self._on_message, queue="test")

    def start(self):
        self.channel.start_consuming()

    def stop(self):
        self.channel.stop_consuming()

    def _on_message(self, channel, method, props, body):

        # Acknowledge message receipt
        response = ''
        if self.on_message:
            response = self.on_message(body)
        if props.reply_to:
            logger.info('Replying to {}'.format(props.reply_to))

            channel.basic_publish(
                    exchange='',
                    routing_key=props.reply_to,
                    properties=pika.BasicProperties(
                        correlation_id=props.correlation_id,
                        content_type='application/json'),
                    body=response)
        channel.basic_ack(method.delivery_tag)

if __name__ == '__main__':
    blocking = BlockingAMQP()
    blocking.start()
