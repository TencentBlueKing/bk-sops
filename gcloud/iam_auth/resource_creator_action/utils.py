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
import logging

from gcloud.core.utils.sites.open.tenant_tools import get_current_tenant_id
from gcloud.iam_auth import IAMMeta, get_iam_client

logger = logging.getLogger("root")


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
    tenant_id = get_current_tenant_id()
    iam = get_iam_client(tenant_id)
    try:
        application = resource_creator_action_params(instance, resource_type, with_ancestors)

        ok, message = iam.grant_resource_creator_actions(application)
        if not ok:
            logging.error(
                "[{resource_type}({resource_id}) created grant] {api} failed".format(
                    resource_type=resource_type, resource_id=instance.id, api="grant_resource_creator_actions"
                )
            )
    except Exception:
        logging.exception(
            "[{resource_type}({resource_id}) created grant] {api} failed".format(
                resource_type=resource_type, resource_id=instance.id, api="grant_resource_creator_actions"
            )
        )


def register_batch_grant_resource_creator_actions(instance: list, response_type, creator, with_ancestors=False):
    tenant_id = get_current_tenant_id()
    iam = get_iam_client(tenant_id)
    try:
        application = batch_resource_creator_action_params(instance, response_type, creator, with_ancestors)

        ok, message = iam.grant_batch_resource_creator_actions(application)
        if not ok:
            logging.error(
                "[{resource_type}({resource_id}) batch created grant] {api} failed".format(
                    resource_type=response_type,
                    resource_id=[ins.id for ins in instance],
                    api="grant_batch_resource_creator_actions",
                )
            )
    except Exception:
        logging.exception(
            "[{resource_type}({resource_id}) batch created grant] {api} failed".format(
                resource_type=response_type,
                resource_id=[ins.id for ins in instance],
                api="grant_batch_resource_creator_actions",
            )
        )


def register_grant_resource_creator_action_attributes(resource_type, creator, attributes):
    tenant_id = get_current_tenant_id()
    iam = get_iam_client(tenant_id)
    try:
        application = resource_creator_action_attribute_params(resource_type, creator, attributes)

        ok, message = iam.grant_resource_creator_action_attributes(application)
        if not ok:
            logging.error(
                "[{resource_type} resource attributes of {creator} created grant] {api} failed".format(
                    resource_type=resource_type, creator=creator, api="grant_resource_creator_action_attributes"
                )
            )
    except Exception:
        logging.error(
            "[{resource_type} resource attributes of {creator} created grant] {api} failed".format(
                resource_type=resource_type, creator=creator, api="grant_resource_creator_action_attributes"
            )
        )
