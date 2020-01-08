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

from django.test import RequestFactory
from django.contrib.auth import get_user_model

from gcloud.core.roles import CC_PERSON_GROUP, CC_ROLES, CC_V2_ROLE_MAP
from gcloud.core.utils import get_business_obj

logger = logging.getLogger("root")


def get_notify_group_by_biz_core(biz_cc_id):
    """
    @summary: 获取默认通知分组加业务自定义通知分组
    @param biz_cc_id:
    @return:
    """
    # 出错通知人员分组
    notify_group_list = list(CC_PERSON_GROUP)
    return notify_group_list


def get_notify_receivers(username, biz_cc_id, receiver_group, more_receiver):
    """
    @summary: 根据通知分组和附加通知人获取最终通知人
    @param username: 请求人
    @param biz_cc_id: 业务CC ID
    @param receiver_group: 通知分组
    @param more_receiver: 附加通知人
    @return:
    """
    # produce a request on backend
    request = RequestFactory().get('/')
    User = get_user_model()
    user = User.objects.get(username=username)
    setattr(request, 'user', user)

    biz_info, __, role_info = get_business_obj(request, biz_cc_id, use_maintainer=True)
    notify_receivers = [username]
    if not isinstance(receiver_group, list):
        receiver_group = receiver_group.split(',')
    if not isinstance(more_receiver, list):
        if more_receiver.strip():
            more_receiver = more_receiver.strip().split(',')
            notify_receivers += more_receiver
    for group in receiver_group:
        if group in CC_ROLES:
            role_members = role_info.get(CC_V2_ROLE_MAP[group], '')
            if role_members:
                # ESB组件接口返回的人员信息，多个人是用;分隔的
                notify_receivers += role_members.split(';')
    notify_receivers = list(set(notify_receivers))
    return notify_receivers


def get_template_context(obj, data_type):
    try:
        from gcloud.tasktmpl3.models import TaskTemplate
        template = TaskTemplate.objects.get(pipeline_template=obj)
    except TaskTemplate.DoesNotExist:
        logger.warning('TaskTemplate Does not exist: pipeline_template.id=%s' % obj.pk)
        return {}
    context = {
        'biz_cc_id': template.business.cc_id,
        'biz_cc_name': template.business.cc_name
    }
    return context
