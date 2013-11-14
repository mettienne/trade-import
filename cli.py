import argparse
import logging
import config
import os

logger = logging.getLogger(__name__)

def run(app_name, worker):
    parser = argparse.ArgumentParser(description='Admin Server Help')
    parser.add_argument(
            '-c', '--config', type=str, nargs="*",
            help="List of configuration files to import (python modules)")
    parser.add_argument('-m', '--method', help="all, invoices or the like")
    parser.add_argument('action', choices=['start', 'stop','restart', 'run'])
    cmd_args = parser.parse_args()


    config.configure(cmd_args.config or [])

    import logging_config
    logging_config.configure(app_name)


    daemon = worker(os.path.join(config.pid_dir, '{}.pid'.format(app_name)))
    if cmd_args.action == 'start':
        daemon.start()
    elif cmd_args.action == 'stop':
        daemon.stop()
    elif cmd_args.action == 'restart':
        daemon.restart()
    elif cmd_args.action == 'run':
        if not cmd_args.method:
            logger.critical('method must be defined when running run')
        else:
            attr = getattr(daemon, cmd_args.method, None)
            if attr is None:
                logger.critical('method unknown')
            else:
                attr()
                daemon.close()



