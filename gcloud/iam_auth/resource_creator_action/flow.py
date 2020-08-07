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
from django.dispatch import receiver
from django.db.models.signals import post_save

from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.iam_auth import IAMMeta, get_iam_client
from gcloud.iam_auth.resource_creator_action.base import common_flow_params, batch_common_params

logger = logging.getLogger("root")
iam = get_iam_client()


@receiver(post_save, sender=TaskTemplate)
def task_template_creat_related_actions_handler(sender, instance, created, **kwargs):
    if isinstance(instance, list):
        #  batch register
        application = batch_common_params(instance, IAMMeta.FLOW_RESOURCE, kwargs["creator"], ancestors=True)

        ok, message = iam.grant_batch_resource_creator_actions(application, bk_username=kwargs["creator"])
        if not ok:
            logging.error("Failed to batch register resources for 'FLOW',resources info:%s." % application)
    else:
        application = common_flow_params(instance, IAMMeta.FLOW_RESOURCE, ancestors=True)

        ok, message = iam.grant_resource_creator_actions(application, bk_username=instance.creator)
        if not ok:
            logging.error("Failed to register resource for 'FLOW',resources info:%s." % application)
