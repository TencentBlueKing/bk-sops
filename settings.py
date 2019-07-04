import os
from conf.default import *
"""
You can load different configurations depending on yourcurrent environment.

 This can be the following values:

      development
      testing
      production
"""

ENVIRONMENT = os.environ.get("BK_ENV", "development")
# Inherit from environment specifics
conf_module = "conf.settings_%s" % ENVIRONMENT

try:
    module = __import__(conf_module, globals(), locals(), ['*'])
except ImportError, e:
    raise ImportError("Could not import conf '%s' (Is it on sys.path?): %s" % (conf_module, e))

for setting in dir(module):
    if setting == setting.upper():
        locals()[setting] = getattr(module, setting)


# check saas app  settings
# try:
# #     saas_conf_module = "conf.settings_saas"
# #     saas_module = __import__(saas_conf_module, globals(), locals(), ['*'])
# #     for saas_setting in dir(saas_module):
# #         if saas_setting == saas_setting.upper():
# #             locals()[saas_setting] = getattr(saas_module, saas_setting)
# # except:
# #     pass
