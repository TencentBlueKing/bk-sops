# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
# NOTE: 不要在这个文件添加代码，打包时会被替换
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
except ImportError as e:
    raise ImportError("Could not import conf '%s' (Is it on sys.path?): %s" % (conf_module, e))

for setting in dir(module):
    if setting == setting.upper():
        locals()[setting] = getattr(module, setting)
