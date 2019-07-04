# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from django.utils.translation import ugettext as _

from settings import BK_PAAS_HOST, APP_CODE
from blueking.component.shortcuts import (get_client_by_request,
                                          ComponentClient,
                                          get_client_by_user)

ESB_GET_CLIENT_BY_REQUEST = get_client_by_request
ESB_GET_CLIENT_BY_USER = get_client_by_user
ESB_COMPONENT_CLIENT = ComponentClient

ESB_AUTH_COMPONENT_SYSTEM = 'bk_login'
ESB_AUTH_GET_USER_INFO = 'get_user'

# 针对CC接口数据相关的缓存时间(单位s)
DEFAULT_CACHE_TIME_FOR_CC = 5

# 针对本地用户信息更新标志缓存的时间
DEFAULT_CACHE_TIME_FOR_USER_UPDATE = 5

# 针对平台用户接口缓存的时间
DEFAULT_CACHE_TIME_FOR_AUTH = 5

REMOTE_ANALYSIS_URL = ''
REMOTE_API_URL = ''

RUN_VER_NAME = _(u"蓝鲸智云社区版")

APP_HOST = '%s/o/%s/' % (BK_PAAS_HOST, APP_CODE)
TEST_APP_HOST = '%s/t/%s/' % (BK_PAAS_HOST, APP_CODE)

APP_MAKER_LINK_PREFIX = '%sappmaker/' % APP_HOST
TEST_APP_MAKER_LINK_PREFIX = '%sappmaker/' % TEST_APP_HOST
APP_MAKER_UPLOAD_LOGO_URL = '%s/paas/api/app_maker/app_logo/modify/' % BK_PAAS_HOST
APP_MAKER_UPLOAD_LOGO_USER_UIN = 'bk_token'
APP_MAKER_UPLOAD_LOGO_USER_KEY = 'bk_token_null'

IMPORT_V1_TEMPLATE_FLAG = False

TEST_API_URL = '%s/o/bk_sops/apigw' % BK_PAAS_HOST
TEST_BK_BIZ_ID = 3
TEST_TEMPLATE_ID = 8
TEST_TOKEN = {
    "BK_TOKEN": 'NGpWESNXOYOgIAegc6cQOffLEtWYGF'
}
