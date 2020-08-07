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

from gcloud.iam_auth import IAMMeta


def common_flow_params(instance, resource_type, ancestors=False):
    params = {"system": IAMMeta.SYSTEM_ID,
              "type": resource_type,
              "id": instance.id,
              "name": instance.name,
              "creator": instance.creator,
              }
    if ancestors:
        params.update({
            "ancestors": [{
                "system": IAMMeta.SYSTEM_ID,
                "type": IAMMeta.PROJECT_RESOURCE,
                "id": instance.project_id
            }]
        })
    return params


def batch_common_params(instance, resource_type, creator, ancestors=False):
    params = {
        "system": IAMMeta.SYSTEM_ID,
        "type": resource_type,
        "creator": creator,
    }
    if ancestors:
        params.update({
            "instances": [{"id": ins.id, "name": ins.name, "ancestors": [{
                "system": IAMMeta.SYSTEM_ID,
                "type": IAMMeta.PROJECT_RESOURCE,
                "id": ins.project_id
            }]} for ins in instance]})
    else:
        params.update({"instances": [{"id": ins.id, "name": ins.name} for ins in instance]})
    return params
