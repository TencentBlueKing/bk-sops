# -*- coding:utf-8 -*-

"""
version log app name, need to add in the INSTALLED_APPS
example:
    from version_log.quick_start_settings import version_log_app
    INSTALLED_APPS += (
        version_log_app,
    )

version log url setting, need to add in the root urls.py
example:
    from version_log.quick_start_settings import version_log_app
    import version_log.config as config
    urlpatterns += [
        url(r'^{}'.format(config.ENTRANCE_URL), include('{}.urls'.format(version_log_app))),
    ]
"""
version_log_app = 'version_log'
