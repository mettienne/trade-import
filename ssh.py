import cli
import signal
import subprocess
import logging
import config

logger = logging.getLogger(__name__)


class SSH():

    def run(self):

        def signal_handler(signal, frame):
            print 'exit'
            logger.info('ssh thread cought exit')
            process.terminate()


        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        logger.info('connecting')
        process = subprocess.Popen(['ssh', '-o', 'ConnectTimeout={}'.format(config.ssh_timeout),
            '-D', '9999', '-L', '4445:localhost:4445', config.superbest_proxy],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output,stderr = process.communicate()

        logger.error('Connection closed unexpectedly')




if __name__ == '__main__':
    cli.run('ssh', SSH)
