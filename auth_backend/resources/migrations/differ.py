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

    def diff_operations(self):
        if self.last_snapshot is None:
            return self.init_diff_operations()

        operations = []

        for scope, last_resources in self.last_snapshot.items():

            # scope not exist anymore
            if scope not in self.snapshot:
                operations.extend([{
                    'operation': 'delete_resource_type',
                    'data': {
                        'scope_type': scope,
                        'resource_type': resource['resource_type']
                    }
                }] for resource in last_resources)

                continue

            upsert_resources = []

            current_resources = {resource['resource_type']: resource for resource in self.snapshot[scope]}

            # check resource state 1 by 1
            for old_resource in last_resources:
                resource_type = old_resource['resource_type']

                # resource had been deleted
                if resource_type not in current_resources:
                    operations.append({
                        'operation': 'delete_resource_type',
                        'data': {
                            'scope_type': scope,
                            'resource_type': resource_type
                        }
                    })
                    continue

                current_state = current_resources[resource_type]
                # resource snapshot had changed
                if current_state != old_resource:
                    upsert_resources.append(current_state)

            operations.append({
                'operation': 'batch_upsert_resource_types',
                'data': {
                    'scope_type': scope,
                    'resource_types': upsert_resources
                }
            })

    def init_diff_operations(self):
        operations = [{
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
            operations.append({
                'operation': 'batch_upsert_resource_types',
                'data': {
                    'scope_type': scope,
                    'resource_types': resources
                }
            })

        return operations

    def has_change(self):
        return self.last_snapshot != self.snapshot
