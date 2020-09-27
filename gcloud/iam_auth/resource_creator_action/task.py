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
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from gcloud.iam_auth import IAMMeta
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.iam_auth.resource_creator_action.utils import register_grant_resource_creator_action_attributes


@receiver(post_save, sender=TaskFlowInstance)
def task_resource_creator_action_handler(sender, instance, created, **kwargs):
    register_grant_resource_creator_action_attributes(
        IAMMeta.TASK_RESOURCE, instance.creator, attributes=[{"id": "iam_resource_owner", "name": _("资源创建者")}]
    )
