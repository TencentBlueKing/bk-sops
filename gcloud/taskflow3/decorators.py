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

from functools import wraps

from django.utils.decorators import available_attrs
from django.http import HttpResponseForbidden

from gcloud.taskflow3.models import TaskFlowInstance


def check_user_perm_of_task(perm=None):
    """
    @summary 请求的任务是否存在
    @param perm: 鉴权的任务阶段
    @return:
    """
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            biz_cc_id = kwargs.get('biz_cc_id')
            instance_id = kwargs.get('instance_id') or request.POST.get('instance_id')
            taskflow = TaskFlowInstance.objects.filter(pk=instance_id, business__cc_id=biz_cc_id)
            if not taskflow.count():
                # return HttpResponseNotFound() 返回404不能显示404.html
                return HttpResponseForbidden()
            # 判断权限
            if perm and not taskflow[0].user_has_perm(
                    request.user, perm):
                return HttpResponseForbidden()
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
