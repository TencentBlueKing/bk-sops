# coding=utf-8
import os

from config.default import *  # noqa

# sentry support

SENTRY_DSN = os.environ.get("SENTRY_DSN")
if SENTRY_DSN:
    INSTALLED_APPS += (
        'raven.contrib.django.raven_compat',
    )
    RAVEN_CONFIG = {
        'dsn': SENTRY_DSN,
    }

# apm support
APM_ID = os.environ.get("APM_ID")
APM_TOKEN = os.environ.get("APM_TOKEN")
if APM_ID and APM_TOKEN:
    INSTALLED_APPS += (
        'ddtrace.contrib.django',
    )
    DATADOG_TRACE = {
        'TAGS': {
            'env': os.getenv('BKPAAS_ENVIRONMENT', 'dev'),
            'apm_id': APM_ID,
            'apm_token': APM_TOKEN,
        },
    }
    # requests for APIGateway/ESB
    # remove pymysql while Django Defaultdb has been traced already
    try:
        import requests # noqa
        from ddtrace import patch
        patch(requests=True, pymysql=False)
    except Exception as e:
        print("patch fail for requests and pymysql: %s" % e)
