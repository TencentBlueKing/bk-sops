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

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from packages.blueking.component.shortcuts import (
    get_client_by_request,
    get_client_by_user
)

RUN_VER_NAME = _(u"蓝鲸智云社区版")

ESB_GET_CLIENT_BY_REQUEST = get_client_by_request
ESB_GET_CLIENT_BY_USER = get_client_by_user

ESB_GET_OLD_CLIENT_BY_REQUEST = get_client_by_request
ESB_GET_OLD_CLIENT_BY_USER = get_client_by_user

APP_HOST = '%s%s' % (settings.BK_PAAS_HOST, settings.SITE_URL)
APP_MAKER_UPLOAD_LOGO_USER_UIN = 'bk_token'
APP_MAKER_UPLOAD_LOGO_USER_KEY = 'bk_token_null'

IMPORT_V1_TEMPLATE_FLAG = False
USE_BK_OAUTH = False
WHETHER_PREPARE_BIZ_IN_API_CALL = True

TEMPLATE_DATA_SALT = 'e5483c1ccde63392bd439775bba6a7ae'
