# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import time

from django.http import JsonResponse
from django.shortcuts import render

from blueapps.account.decorators import login_exempt


@login_exempt
def login_success(request):
    """
    弹框登录成功返回页面
    """
    return render(request, "account/login_success.html")


@login_exempt
def login_page(request):
    """
    跳转至固定页面，然后弹框登录
    """
    refer_url = request.GET.get("refer_url")

    context = {"refer_url": refer_url}
    return render(request, "account/login_page.html", context)


def send_code_view(request):
    ret = request.user.send_code()
    return JsonResponse(ret)


def get_user_info(request):

    return JsonResponse(
        {
            "code": 0,
            "data": {
                "id": request.user.id,
                "username": request.user.username,
                "timestamp": time.time(),
            },
            "message": "ok",
        }
    )
