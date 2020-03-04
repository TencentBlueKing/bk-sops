# -*- coding: utf-8 -*-
import os
import string
import random

from blueapps.conf.default_settings import BASE_DIR, APP_CODE

APP_CODE = os.environ.get('APP_ID', APP_CODE)


def get_logging_config_dict(settings_module):
    log_class = 'logging.handlers.RotatingFileHandler'
    log_level = settings_module.get('LOG_LEVEL', 'INFO')

    if settings_module.get('IS_LOCAL', False):
        log_dir = os.path.join(os.path.dirname(BASE_DIR), 'logs', APP_CODE)
        log_name_prefix = os.getenv('BKPAAS_LOG_NAME_PREFIX', APP_CODE)
        logging_format = {
            'format': ('%(levelname)s [%(asctime)s] %(pathname)s '
                       '%(lineno)d %(funcName)s %(process)d %(thread)d '
                       '\n \t %(message)s \n'),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    else:
        log_dir = '/app/v3logs/'
        rand_str = ''.join(
            random.sample(string.ascii_letters + string.digits, 4))
        log_name_prefix = '%s-%s' % (os.getenv('BKPAAS_PROCESS_TYPE'), rand_str)

        logging_format = {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'fmt': ('%(levelname)s %(asctime)s %(pathname)s %(lineno)d '
                    '%(funcName)s %(process)d %(thread)d %(message)s')
        }
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': logging_format,
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'handlers': {
            'null': {
                'level': 'DEBUG',
                'class': 'logging.NullHandler',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'root': {
                'class': log_class,
                'formatter': 'verbose',
                'filename': os.path.join(
                    log_dir, '%s-django.log' % log_name_prefix),
                'maxBytes': 1024 * 1024 * 10,
                'backupCount': 5
            },
            'component': {
                'class': log_class,
                'formatter': 'verbose',
                'filename': os.path.join(
                    log_dir, '%s-component.log' % log_name_prefix),
                'maxBytes': 1024 * 1024 * 10,
                'backupCount': 5
            },
            'mysql': {
                'class': log_class,
                'formatter': 'verbose',
                'filename': os.path.join(
                    log_dir, '%s-mysql.log' % log_name_prefix),
                'maxBytes': 1024 * 1024 * 10,
                'backupCount': 5
            },
            'celery': {
                'class': log_class,
                'formatter': 'verbose',
                'filename': os.path.join(
                    log_dir, '%s-celery.log' % log_name_prefix),
                'maxBytes': 1024 * 1024 * 10,
                'backupCount': 5
            },
            'blueapps': {
                'class': log_class,
                'formatter': 'verbose',
                'filename': os.path.join(
                    log_dir, '%s-django.log' % log_name_prefix),
                # TODO blueapps log 等待平台提供单独的路径
                # log_dir, '%s-blueapps.log' % log_name_prefix),
                'maxBytes': 1024 * 1024 * 10,
                'backupCount': 5
            },
        },
        'loggers': {
            'django': {
                'handlers': ['null'],
                'level': 'INFO',
                'propagate': True,
            },
            'django.server': {
                'handlers': ['console'],
                'level': log_level,
                'propagate': True,
            },
            'django.request': {
                'handlers': ['root'],
                'level': 'ERROR',
                'propagate': True,
            },
            'django.db.backends': {
                'handlers': ['mysql'],
                'level': log_level,
                'propagate': True,
            },
            # the root logger ,用于整个project的logger
            'root': {
                'handlers': ['root'],
                'level': log_level,
                'propagate': True,
            },
            # 组件调用日志
            'component': {
                'handlers': ['component'],
                'level': log_level,
                'propagate': True,
            },
            'celery': {
                'handlers': ['celery'],
                'level': log_level,
                'propagate': True,
            },
            # other loggers...
            # blueapps
            'blueapps': {
                'handlers': ['blueapps'],
                'level': log_level,
                'propagate': True,
            },
            # 普通app日志
            'app': {
                'handlers': ['root'],
                'level': log_level,
                'propagate': True,
            }
        }
    }
