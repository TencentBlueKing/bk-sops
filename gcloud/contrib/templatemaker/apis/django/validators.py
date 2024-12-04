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

import logging
import ujson as json

from django.utils.translation import ugettext_lazy as _

from gcloud.utils.validate import RequestValidator

logger = logging.getLogger("root")


class JsonValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):
        try:
            json.loads(request.body)
        except Exception:
            message = _("非法请求: 数据错误, 请求不是合法的Json格式 | validate")
            logger.error(message)
            return False, message

        return True, ""
