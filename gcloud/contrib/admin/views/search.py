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
from gcloud.core.models import Project
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.taskflow3.models import TaskFlowInstance


class AdminSearchMatcher:

    def __init__(self, keyword):
        self.keyword = keyword
        self.id_keyword = None
        try:
            self.id_keyword = int(keyword)
        except Exception:
            pass

    def match(self):
        matched = []

        if self.id_keyword:
            matched.extend(self._match_id())

        else:
            matched.extend(self._match_str())

        return {
            'matched': matched
        }

    def _match_id(self):
        matched = []

        if TaskTemplate.objects.filter(id=self.id_keyword).exists():
            matched.append({
                'type': 'flow',
                'filter': {
                    'id': self.id_keyword
                }
            })

        if TaskFlowInstance.objects.filter(id=self.id_keyword).exists():
            matched.append({
                'type': 'task',
                'filter': {
                    'id': self.id_keyword
                }
            })

        return matched

    def _match_str(self):
        matched = []

        qs = Project.objects.filter(name=self.keyword)
        if qs.exists():
            first_match_project = qs[0]
            matched.extend([
                {
                    'type': 'flow',
                    'filter': {
                        'project__id': first_match_project.id
                    }
                },
                {
                    'type': 'task',
                    'filter': {
                        'project__id': first_match_project.id
                    }
                }
            ])

        return matched


@require_POST
def search(request):

    verify_or_raise_auth_failed(principal_type='user',
                                principal_id=request.user.username,
                                resource=admin_operate_resource,
                                action_ids=[admin_operate_resource.actions.view.id],
                                instance=None)

    data = json.loads(request.body)
    keyword = data.get('keyword', '')

    match_result = AdminSearchMatcher(keyword=keyword).match()

    return JsonResponse({
        'result': True,
        'data': match_result
    })
