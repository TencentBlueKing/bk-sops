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

import ujson as json

from django.views.decorators.http import require_POST
from django.http.response import JsonResponse

from auth_backend.plugins.shortcuts import verify_or_raise_auth_failed

from gcloud.core.permissions import admin_operate_resource
from gcloud.tasktmpl3.models import TaskTemplate


@require_POST
def restore_template(request):

    verify_or_raise_auth_failed(principal_type='user',
                                principal_id=request.user.username,
                                resource=admin_operate_resource,
                                action_ids=[admin_operate_resource.actions.edit.id],
                                instance=None)

    data = json.loads(request.body)
    template_id = data['template_id']

    res = TaskTemplate.objects.filter(id=template_id, is_deleted=True).update(is_deleted=False)

    return JsonResponse({
        'result': True,
        'data': {
            'affect': res
        }
    })
