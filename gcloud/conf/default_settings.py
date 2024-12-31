# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.conf import settings
from django.utils.translation import gettext_lazy as _

import env
from packages.blueking.component.shortcuts import get_client_by_request, get_client_by_user

RUN_VER_NAME = _("蓝鲸智云")

ESB_GET_CLIENT_BY_REQUEST = get_client_by_request
ESB_GET_CLIENT_BY_USER = get_client_by_user

ESB_GET_OLD_CLIENT_BY_REQUEST = get_client_by_request
ESB_GET_OLD_CLIENT_BY_USER = get_client_by_user

APP_HOST = env.BK_SOPS_HOST
ESB_GET_ALL_USER = "{}/api/c/compapi/v2/usermanage/fe_list_users/".format(settings.BK_PAAS_ESB_HOST)
BK_DOC_URL = f"{env.BK_DOC_CENTER_HOST}/markdown/{{}}/SOPS/3.33/UserGuide/Overview/README.md"
FEEDBACK_URL = "https://bk.tencent.com/s-mart/community"
APP_MAKER_UPLOAD_LOGO_USER_UIN = "bk_token"
APP_MAKER_UPLOAD_LOGO_USER_KEY = "bk_token_null"

IMPORT_V1_TEMPLATE_FLAG = False
WHETHER_PREPARE_BIZ_IN_API_CALL = True
