# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import re
import os

from django.conf import settings
from django.utils.translation import ugettext_lazy as _


__all__ = ('MD_FILES_DIR', 'PARSED_HTML_FILES_DIR', 'NAME_PATTERN',
           'LATEST_VERSION_INFORM', 'ENTRANCE_URL')

# 默认设置
VERSION_LOG = {
    'MD_FILES_DIR': 'version_logs_md',
    # 形如 'V1.0.0_2020-01-01.md'
    'NAME_PATTERN': '[vV]\d+(\.\d+){1,3}_\d{4}(-\d{2}){2}\.md',  # noqa
    'LATEST_VERSION_INFORM': False,
    'LATEST_VERSION_INFORM_TYPE': 'redirect',
    'ENTRANCE_URL': 'version_log/',
    'PAGE_HEAD_TITLE': _(u'版本日志'),
    'PAGE_STYLE': 'dialog',
    'USE_HASH_URL': True
}

# 用户配置
USER_SETTING = getattr(settings, 'VERSION_LOG', {})

# 合并后配置，以用户配置为主，兼容py2和py3
version_log = VERSION_LOG.copy()
version_log.update(USER_SETTING)

# 版本日志模式
NAME_PATTERN = re.compile(version_log['NAME_PATTERN'])

# 版本日志md文件夹
if 'MD_FILES_DIR' in USER_SETTING:
    MD_FILES_DIR = os.path.join(settings.BASE_DIR, USER_SETTING['MD_FILES_DIR'])
    # 自定义路径文件夹不存在，需更正配置地址
    if not os.path.isdir(MD_FILES_DIR):
        raise IOError('VERSION_LOGS_DIR not found, please use a valid address')
else:
    MD_FILES_DIR = os.path.join(settings.BASE_DIR, VERSION_LOG['MD_FILES_DIR'])
    # 默认配置下，在项目根目录新建文件夹
    if not os.path.isdir(MD_FILES_DIR):
        os.mkdir(MD_FILES_DIR)

# 版本日志html文件夹
PARSED_HTML_FILES_DIR = os.path.join(os.path.dirname(MD_FILES_DIR), 'version_logs_html')
if not os.path.isdir(PARSED_HTML_FILES_DIR):
    os.mkdir(PARSED_HTML_FILES_DIR)

# 最新版本
LATEST_VERSION = None

# 最新版本通知开关
LATEST_VERSION_INFORM = version_log['LATEST_VERSION_INFORM']

# 用户缓存
USER_CACHE = set()

# 入口URL
ENTRANCE_URL = version_log['ENTRANCE_URL']

# 版本日志页面标题
PAGE_HEAD_TITLE = version_log['PAGE_HEAD_TITLE']

# 版本日志页面选择 dialog/gitbook
PAGE_STYLE = version_log['PAGE_STYLE']

# 无版本号记录常量
NO_VERSION_CONSTANT = 'None'

# 自动弹出方式 popup/redirect
LATEST_VERSION_INFORM_TYPE = version_log["LATEST_VERSION_INFORM_TYPE"]

# url 类型: 带 # 的 hash 方式: index/#/home, 或者是普通路径: index/home
# 默认为 hash 方式, 如果不是, 获取不到就会默认返回主页
USE_HASH_URL = version_log['USE_HASH_URL']
