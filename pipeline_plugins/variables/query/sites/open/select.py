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

import logging
import requests

from django.conf.urls import url
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger('root')


def variable_select_source_data_proxy(request):
    """
    @summary: 获取下拉框源数据的通用接口
    @param request:
    @return:
    """
    url = request.GET.get('url')
    try:
        response = requests.get(
            url=url,
            verify=False
        )
    except Exception as e:
        logger.exception('variable select get data from url[url={url}] raise error: {error}'.format(url=url, error=e))
        text = _('请求数据异常: {error}').format(error=e)
        data = [{'text': text, 'value': ''}]
        return JsonResponse(data, safe=False)

    try:
        data = response.json()
    except Exception:
        try:
            content = response.content.decode(response.encoding)
            logger.exception('variable select get data from url[url={url}] is not a valid JSON: {data}'.format(
                url=url, data=content[:500])
            )
        except Exception:
            logger.exception('variable select get data from url[url={url}] data is not a valid JSON'.format(url=url))
        text = _('返回数据格式错误，不是合法 JSON 格式')
        data = [{'text': text, 'value': ''}]

    return JsonResponse(data, safe=False)


select_urlpatterns = [
    url(r"^variable_select_source_data_proxy/$", variable_select_source_data_proxy),
]
