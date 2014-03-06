import argparse
import logging
import config
import os
from types import ModuleType

logger = logging.getLogger(__name__)

def run(app_name, worker):
    parser = argparse.ArgumentParser(description='Admin Server Help')
    parser.add_argument(
            '-c', '--config', type=str, nargs="*",
            help="List of configuration files to import (python modules)")
    parser.add_argument('-m', '--method', help="all, invoices or the like")
    cmd_args = parser.parse_args()


    config.configure(cmd_args.config or [])

    def module_keys(mod):
        return [key for key in mod.__dict__
                if not key.startswith('__')
                and not isinstance(getattr(config, key), ModuleType)]


    # create a list of config for printing
    c_desc = '\n'
    c_desc += ('* ' * 50) + '\n'
    c_desc += 'Configuration for {}:\n'.format(app_name)
    c_desc += ('* ' * 50) + '\n'
    for key in sorted(module_keys(config)):
        c_desc += '{:40} : {!r:<}\n'.format(key, getattr(config, key))
    c_desc += ('* ' * 50) + '\n'

    print c_desc

    import logging_config
    logging_config.configure(app_name)

    instance = worker()

    if cmd_args.method:
        logger.critical('Running {}'.format(cmd_args.method))
        attr = getattr(worker, cmd_args.method, None)
        if attr is None:
            logger.critical('method unknown')
        else:
            attr(instance)


    else:
        instance.run()
