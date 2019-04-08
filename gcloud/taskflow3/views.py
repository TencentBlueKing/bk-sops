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

@summary: 任务流程实例views
"""

from django.shortcuts import render


def home(request, biz_cc_id):
    """
    @summary: 任务记录首页
    @param request:
    @param biz_cc_id:
    @return:
    """
    ctx = {
        "view_mode": "app",
        "app_id": "",
        "template_id": request.GET.get('template_id', ''),
    }
    return render(request, 'core/base_vue.html', ctx)
