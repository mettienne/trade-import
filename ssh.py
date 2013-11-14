import daemon
import cli
import signal
import subprocess
import logging
import config

logger = logging.getLogger(__name__)


class SSH(daemon.Daemon):

    def run(self):

        def signal_handler(signal, frame):
            logger.info('ssh thread cought exit')
            process.terminate()


        logger.info('opening ssh connection')
        signal.signal(signal.SIGTERM, signal_handler)
        logger.info('connecting')
        process = subprocess.Popen(['ssh', '-o', 'ConnectTimeout={}'.format(config.ssh_timeout),
            '-N', '-L', '27018:localhost:22282', config.mongoSSH],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output,stderr = process.communicate()
        logger.info(output)
        logger.info(stderr)
        logger.info('ssh tunnel closed')




if __name__ == '__main__':
    cli.run('ssh', SSH)
