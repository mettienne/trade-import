'''

@author: Team Processing
@copyright: Issuu Aps Jun 17, 2013
'''
import config
import logging.config
import os


def configure(app_id=''):
    file_err = os.path.join(config.log_dir, "{}_err.log".format(app_id))
    file_debug = os.path.join(config.log_dir, "{}_debug.log".format(app_id))

    logging.raiseExceptions = False

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': True,
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
            'debug_log_file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': file_debug,
                'formatter': 'verbose'
            }
        },
        'loggers': {
            '': {
                'handlers': ['error_log_file', 'debug_log_file'],
                'propagate': False,
                'level': 'DEBUG',
            },
            'pika': {
                'level': 'ERROR'
            },
        }
    })