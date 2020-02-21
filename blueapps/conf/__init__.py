"""
blueapps.conf
=============
"""


class BlueSettings(object):

    def __init__(self):
        from django.conf import settings as django_settings
        from blueapps.conf import default_settings

        self._django_settings = django_settings
        self._default_settings = default_settings

    def __getattr__(self, key):
        if key == key.upper():
            if hasattr(self._django_settings, key):
                return getattr(self._django_settings, key)
            elif hasattr(self._default_settings, key):
                return getattr(self._default_settings, key)

        raise AttributeError("%r object has no attribute %r"
                             % (self.__class__.__name__, key))


settings = BlueSettings()
