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

from django.conf import settings


class SnapshotDiffer(object):
    def __init__(self, last_snapshot, snapshot):
        self.last_snapshot = last_snapshot
        self.snapshot = snapshot

    def diff(self):
        if self.last_snapshot is None:
            return self.init_diff()

    def init_diff(self):
        diff = [{
            'operation': 'register_system',
            'data': {
                'system_id': settings.BK_IAM_SYSTEM_ID,
                'system_name': settings.BK_IAM_SYSTEM_NAME,
                'desc': settings.BK_IAM_SYSTEM_DESC,
                'query_interface': settings.BK_IAM_QUERY_INTERFACE,
                'related_scope_types': settings.BK_IAM_RELATED_SCOPE_TYPES,
                'managers': settings.BK_IAM_SYSTEM_MANAGERS,
                'creator': settings.BK_IAM_SYSTEM_CREATOR
            }
        }]

        for scope, resources in self.snapshot.items():
            diff.append({
                'operation': 'batch_upsert_resource_types',
                'data': {
                    'scope_type': scope,
                    'resource_types': resources
                }
            })

        return diff
