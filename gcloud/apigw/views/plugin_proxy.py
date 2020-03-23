# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from urllib.parse import urlsplit

import ujson as json
from django.http import JsonResponse
from django.test import RequestFactory
from django.urls import resolve, Resolver404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.apigw.views.utils import logger

try:
    from bkoauth.decorators import apigw_required
except ImportError:
    from packages.bkoauth.decorators import apigw_required


@login_exempt
@csrf_exempt
@require_POST
@apigw_required
@mark_request_whether_is_trust
def dispatch_plugin_query(request):
    """
        转发插件表单渲染资源请求，暂时仅考虑GET/POST请求
        body = {
            "url": 被转发资源请求url, 比如：/pipeline/job_get_script_list/4/?type=public
            "method": 'GET|POST',
            "data": data, POST请求的数据
        }
    """

    try:
        params = json.loads(request.body)
    except Exception:
        return JsonResponse({
            'result': False,
            'message': 'invalid json format',
            'code': err_code.REQUEST_PARAM_INVALID.code,
        })

    # proxy: url/method/data
    url = params.get('url')
    method = params.get('method', 'GET')
    data = params.get('data', {})

    try:
        parsed = urlsplit(url)

        if method.lower() == "get":
            fake_request = RequestFactory().get(url, content_type="application/json")
        elif method.lower() == "post":
            fake_request = RequestFactory().post(
                url, data=data, content_type="application/json"
            )
        else:
            return JsonResponse({
                'result': False,
                'code': err_code.INVALID_OPERATION.code,
                'message': 'dispatch_plugin_query: only support get and post method.'
            })

        # transfer request.user
        setattr(fake_request, "user", request.user)

        # resolve view_func
        match = resolve(parsed.path, urlconf=None)
        view_func, kwargs = match.func, match.kwargs

        # call view_func
        return view_func(fake_request, **kwargs)

    except Resolver404:
        logger.warning('dispatch_plugin_query: resolve view func 404 for: {}'.format(url))
        return JsonResponse({
            'result': False,
            'code': err_code.REQUEST_PARAM_INVALID.code,
            'message': 'dispatch_plugin_query: resolve view func 404 for: {}'.format(url)
        })

    except Exception as e:
        logger.error('dispatch_plugin_query: exception for {}'.format(e))
        return JsonResponse({
            'result': False,
            'message': 'dispatch_plugin_query: exception for {}'.format(e),
            'code': err_code.UNKNOW_ERROR.code
        })

