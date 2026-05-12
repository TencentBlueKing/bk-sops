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

from functools import wraps

from django.http import HttpResponseForbidden
from iam import Action, Subject
from iam.shortcuts import allow_or_raise_auth_failed

from gcloud.contrib.appmaker.models import AppMaker
from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory

iam = get_iam_client()


def check_db_object_exists(model, iam_action=None):
    """
    @summary 请求的DB数据是否存在
    @return:
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            project_id = kwargs.get("project_id")
            if model == "AppMaker":
                app_id = kwargs.get("app_id")
                app_maker = AppMaker.objects.filter(pk=app_id, project_id=project_id, is_deleted=False).first()
                if not app_maker:
                    # return HttpResponseNotFound() 返回404不能显示404.html
                    return HttpResponseForbidden()
                if iam_action:
                    allow_or_raise_auth_failed(
                        iam=iam,
                        system=IAMMeta.SYSTEM_ID,
                        subject=Subject("user", request.user.username),
                        action=Action(iam_action),
                        resources=res_factory.resources_for_mini_app_obj(app_maker),
                    )
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
