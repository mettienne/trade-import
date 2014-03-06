'''

@author: Team Processing
@copyright: Issuu Aps Jun 17, 2013
'''
import config
import logging.config
import os
import sys


def configure(app_id=''):
    file_err = os.path.join(config.log_dir, "{}_err.log".format(app_id))

    logging.raiseExceptions = False

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(asctime)s %(name)-22s %(levelname)-8s %(message)s'
            }
        },
        'handlers': {
            'error_log_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': file_err,
                'formatter': 'verbose'
            },
            'stdout': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
                'formatter': 'verbose'
            }
        },
        'loggers': {
            '': {
                'handlers': ['error_log_file', 'stdout'],
                'propagate': False,
                'level': 'DEBUG',
            },
            'pika': {
                'level': 'ERROR'
            },
        }
    })
