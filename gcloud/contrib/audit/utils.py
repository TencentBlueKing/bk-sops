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
import logging

import six
from bk_audit.contrib.bk_audit.client import bk_audit_client
from bk_audit.log.models import AuditContext
from django.conf import settings
from iam.auth.models import BaseObject

from gcloud.contrib.audit.instances import build_instance
from iam import Action

logger = logging.getLogger("root")


class ResourceType(BaseObject):
    __slots__ = ("id",)

    def __init__(self, id):
        self.id = id

    def validate(self):
        # Type Check
        if not isinstance(self.id, six.string_types):
            raise TypeError("ResourceType.id should be a string")

        # Value Check
        if not self.id:
            raise ValueError("ResourceType.id should not be empty")

    def to_dict(self):
        return {"id": self.id}


def bk_audit_add_event(username, action_id, resource_id=None, instance=None, origin_data=None, *args, **kwargs):
    if not settings.ENABLE_BK_AUDIT:
        return
    try:
        logger.info(
            "bk_audit add_event: username: %s, action_id: %s, resource_id: %s, instance: %s",
            username,
            action_id,
            resource_id,
            instance,
        )
        instance = build_instance(resource_id, instance, origin_data)
        context = AuditContext(username=username)
        bk_audit_client.add_event(
            action=Action(action_id),
            resource_type=ResourceType(resource_id) if resource_id else None,
            audit_context=context,
            instance=instance,
        )
        logger.info("bk_audit add_event: success")
    except Exception as e:
        logger.exception(f"bk_audit error: {e}")
