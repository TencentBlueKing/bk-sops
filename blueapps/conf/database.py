# -*- coding: utf-8 -*-
import os


def get_default_database_config_dict(settings_module):
    if os.getenv('GCS_MYSQL_NAME') and os.getenv('MYSQL_NAME'):
        db_prefix = settings_module.get('DB_PREFIX', '')
        if not db_prefix:
            raise EnvironmentError('no DB_PREFIX config while multiple '
                                   'databases found in environment')
    elif os.getenv('GCS_MYSQL_NAME'):
        db_prefix = 'GCS_MYSQL'
    elif os.getenv('MYSQL_NAME'):
        db_prefix = 'MYSQL'
    else:
        if settings_module.get('IS_LOCAL', False):
            return {}
        else:
            raise EnvironmentError('no database[GCS_MYSQL or MYSQL] config')
    return {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ['%s_NAME' % db_prefix],
        'USER': os.environ['%s_USER' % db_prefix],
        'PASSWORD': os.environ['%s_PASSWORD' % db_prefix],
        'HOST': os.environ['%s_HOST' % db_prefix],
        'PORT': os.environ['%s_PORT' % db_prefix],
    }
