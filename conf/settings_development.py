# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import os

from settings import APP_ID

# ===============================================================================
# 数据库设置, 测试环境数据库设置
# ===============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 默认用mysql
        'NAME': 'testdisk',  # 数据库名 (默认与APP_ID相同)
        'USER': 'root',  # 你的数据库user
        'PASSWORD': 'root',  # 你的数据库password
        'HOST': '192.168.1.73',  # 数据库HOST
        'PORT': '3306',  # 默认3306
    },
}

REDIS = {
    'host': '127.0.0.1',
    'port': 6379,
}

# Import from local settings
try:
    from local_settings import *
except ImportError:
    pass

LOG_PERSISTENT_DAYS = 1

