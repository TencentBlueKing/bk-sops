# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import itertools
import logging

from django.db import transaction
from django.http import HttpResponseForbidden
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from guardian.shortcuts import (assign_perm,
                                remove_perm,
                                get_users_with_perms,
                                get_groups_with_perms,
                                get_group_perms,
                                get_user_perms
                                )

from gcloud.core.roles import CC_PERSON_GROUP, CC_ROLES
from gcloud.core.utils import get_business_obj

logger = logging.getLogger("root")


@transaction.atomic
def assign_tmpl_perms(request, perms, groups, tmpl_inst):
    user = request.user
    biz = tmpl_inst.business

    if user.has_perm('manage_business', biz):
        # 先删除所有有当前要授权权限的分组的权限
        perm_groups = get_groups_with_perms(tmpl_inst, attach_perms=True)
        for group, perm_list in perm_groups.items():
            for perm in perm_list:
                if perm in perms:
                    remove_perm(perm, group, tmpl_inst)
        # 给当前有权限的分组授权
        for perm, group in itertools.product(perms, groups):
            assign_perm(perm, group, tmpl_inst)
    else:
        return HttpResponseForbidden()


@transaction.atomic
def assign_tmpl_perms_user(request, perms, users, tmpl_inst):
    user = request.user
    biz = tmpl_inst.business

    if user.has_perm('manage_business', biz):
        # 删除有当前要授权权限的所有拥有用户的授权信息
        perm_users = get_users_with_perms(tmpl_inst, attach_perms=True)
        for user, perm_list in perm_users.items():
            for perm in perm_list:
                if perm in perms:
                    remove_perm(perm, user, tmpl_inst)
        # then assign perms
        for perm, user in itertools.product(perms, users):
            assign_perm(perm, user, tmpl_inst)
    else:
        return HttpResponseForbidden()


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

    biz_info, __, role_info = get_business_obj(request, biz_cc_id,
                                               use_maintainer=True)
    notify_receivers = [username]
    if not isinstance(receiver_group, list):
        receiver_group = receiver_group.split(',')
    if not isinstance(more_receiver, list):
        if more_receiver.strip():
            more_receiver = more_receiver.strip().split(',')
            notify_receivers += more_receiver
    for group in receiver_group:
        if group in CC_ROLES:
            role_members = role_info.get(group, '')
            if role_members:
                # ESB组件接口返回的人员信息，多个人是用;分隔的
                notify_receivers += role_members.split(';')
    notify_receivers = list(set(notify_receivers))
    return notify_receivers


def get_template_context(obj):
    try:
        from gcloud.tasktmpl3.models import TaskTemplate
        template = TaskTemplate.objects.get(pipeline_template=obj)
    except TaskTemplate.DoesNotExist as e:
        logger.warning('TaskTemplate Does not exit: pipeline_template.id=%s' % obj.pk)
        return {}
    context = {
        'biz_cc_id': template.business.cc_id,
        'biz_cc_name': template.business.cc_name
    }
    return context
