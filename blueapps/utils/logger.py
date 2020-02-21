import logging

__all__ = ['logger', 'logger_celery']

logger = logging.getLogger('app')
logger_celery = logging.getLogger('celery')
