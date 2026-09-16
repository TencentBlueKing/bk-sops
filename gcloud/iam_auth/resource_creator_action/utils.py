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
from gcloud.iam_auth import IAMMeta


def resource_creator_action_params(instance, resource_type, with_ancestors=False):
    params = {
        "system": IAMMeta.SYSTEM_ID,
        "type": resource_type,
        "id": instance.id,
        "name": instance.name,
        "creator": instance.creator,
    }
    if with_ancestors:
        params.update(
            {"ancestors": [{"system": IAMMeta.SYSTEM_ID, "type": IAMMeta.PROJECT_RESOURCE, "id": instance.project_id}]}
        )
    return params


def batch_resource_creator_action_params(instance: list, resource_type, creator, with_ancestors=False):
    params = {
        "system": IAMMeta.SYSTEM_ID,
        "type": resource_type,
        "creator": creator,
    }
    if with_ancestors:
        params.update(
            {
                "instances": [
                    {
                        "id": ins.id,
                        "name": ins.name,
                        "ancestors": [
                            {"system": IAMMeta.SYSTEM_ID, "type": IAMMeta.PROJECT_RESOURCE, "id": ins.project_id}
                        ],
                    }
                    for ins in instance
                ]
            }
        )
    else:
        params.update({"instances": [{"id": ins.id, "name": ins.name} for ins in instance]})
    return params


def resource_creator_action_attribute_params(resource_type, creator, attributes):
    params = {
        "system": IAMMeta.SYSTEM_ID,
        "type": resource_type,
        "creator": creator,
        "attributes": [
            {"id": attribute["id"], "name": attribute["name"], "values": [{"id": creator, "name": creator}]}
            for attribute in attributes
        ],
    }
    return params


def register_grant_resource_creator_actions(instance, resource_type, with_ancestors=False):
    raise RuntimeError("creator auto-grant is disabled for IAM V4")


def register_batch_grant_resource_creator_actions(instance: list, response_type, creator, with_ancestors=False):
    raise RuntimeError("creator auto-grant is disabled for IAM V4")


def register_grant_resource_creator_action_attributes(resource_type, creator, tenant_id, attributes):
    raise RuntimeError("creator auto-grant is disabled for IAM V4")
