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

from abc import ABCMeta, abstractmethod

import ujson as json

from api.utils.request import logger
from django.utils.translation import ugettext_lazy as _


class RequestValidator(object, metaclass=ABCMeta):
    @abstractmethod
    def validate(self, request, *args, **kwargs):
        """
        return is_valid(bool), err(str)
        """
        raise NotImplementedError()


class ObjectJsonBodyValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):

        try:
            data = json.loads(request.body)
        except Exception:
            logger.error("非法请求: 数据错误, 请求不是合法的Json格式, 加载异常| validate")
            return False, _("非法请求: 数据错误, 请求不是合法的Json格式, 加载异常 | validate")

        if not isinstance(data, dict):
            logger.error("非法请求: 数据错误, 请求不是合法的Json格式 | validate")
            return False, _("非法请求: 数据错误, 请求不是合法的Json格式 | validate")

        self.data = data

        return True, ""
