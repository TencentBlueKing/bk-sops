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
import time

from django.conf import settings
import requests
from requests import HTTPError

logger = logging.getLogger("root")


def requests_with_retry(method: str, url: str, with_sleep: bool = False, **kwargs):
    """带有重试的requests请求"""
    response = None
    for retry_num in range(1, settings.REQUEST_RETRY_NUMBER + 1):
        try:
            logger.info("[requests_with_retry] request url {} with method {} and kwargs {}".format(url, method, kwargs))
            response = getattr(requests, method)(url, **kwargs)
            response.raise_for_status()
            return True, response
        except HTTPError as e:
            message = (
                f"[requests_with_retry] request error, "
                f"retry_num:{retry_num}, {method} {url}, kwargs:{kwargs}, response:{response.content}, error:{str(e)}"
            )
            logger.exception(message)
            if with_sleep:
                time.sleep(1)

    return False, response
