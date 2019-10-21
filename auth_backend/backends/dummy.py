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

from __future__ import absolute_import, unicode_literals

from UserDict import UserDict

from django.contrib.auth import get_user_model

from auth_backend.backends import utils
from auth_backend.backends.base import AuthBackend
from auth_backend.resources.django import DjangoModelResource


class AuthOperationResult(UserDict):
    pass


class FreeAuthBackend(AuthBackend):

    def register_instance(self, resource, instance, scope_id=None):
        return AuthOperationResult(result=True,
                                   code=0,
                                   message='success',
                                   data={})

    def batch_register_instance(self, resource, instances, scope_id=None):
        return AuthOperationResult(result=True,
                                   code=0,
                                   message='success',
                                   data={})

    def update_instance(self, resource, instance, scope_id=None):
        return AuthOperationResult(result=True,
                                   code=0,
                                   message='success',
                                   data={})

    def delete_instance(self, resource, instance, scope_id=None):
        return AuthOperationResult(result=True,
                                   code=0,
                                   message='success',
                                   data={})

    def batch_delete_instance(self, resource, instances, scope_id=None):
        return AuthOperationResult(result=True,
                                   code=0,
                                   message='success',
                                   data={})

    def verify_perms(self, principal_type, principal_id, resource, action_ids, instance=None, scope_id=None):
        instances = [instance] if instance else []
        actions = utils.resource_actions_for(resource=resource,
                                             action_ids=action_ids,
                                             instances=instances,
                                             ignore_relate_instance_act=False)
        for action in actions:
            action['is_pass'] = True

        return AuthOperationResult(result=True,
                                   code=0,
                                   message='success',
                                   data=actions)

    def batch_verify_perms(self, principal_type, principal_id, resource, action_ids, instances=None, scope_id=None):
        if not instances:
            instances = []
        actions = utils.resource_actions_for(resource=resource,
                                             action_ids=action_ids,
                                             instances=instances,
                                             ignore_relate_instance_act=False)
        for action in actions:
            action['is_pass'] = True

        return AuthOperationResult(result=True,
                                   code=0,
                                   message='success',
                                   data=actions)

    def verify_multiple_resource_perms(self, principal_type, principal_id, perms_tuples, scope_id=None):
        actions = []
        for perms_tuple in perms_tuples:
            resource = perms_tuple[0]
            action_ids = perms_tuple[1]
            instance = perms_tuple[2]

            actions.extend(utils.resource_actions_for(resource=resource,
                                                      action_ids=action_ids,
                                                      instances=[instance] if instance else None,
                                                      ignore_relate_instance_act=False))

        for action in actions:
            action['is_pass'] = True

        return AuthOperationResult(result=True,
                                   code=0,
                                   message='success',
                                   data=actions)

    def search_authorized_resources(self, resource, principal_type, principal_id, action_ids, scope_id=None):
        if not isinstance(resource, DjangoModelResource):
            raise NotImplementedError('only allow search authorized resources for DjangoModelResource')

        actions = utils.resource_actions_for(resource=resource,
                                             action_ids=action_ids,
                                             instances=[],
                                             ignore_relate_instance_act=False)
        ids = resource.resource_cls.objects.all().values_list(resource.id_field, flat=True)

        resource_ids = [[{'resource_type': resource.rtype, 'resource_id': rid}] for rid in ids]

        for action in actions:
            action['resource_ids'] = resource_ids

        return AuthOperationResult(result=True,
                                   code=0,
                                   message='success',
                                   data=actions)

    def search_resources_perms_principals(self, resource, resources_actions, scope_id=None):
        UserModel = get_user_model()
        user_ids = UserModel.objects.all().values_list('username', falt=True)
        principals = [{'principal_type': 'user', 'principal_id': uid} for uid in user_ids]

        actions = []
        for resource_action in resources_actions:
            action = {
                'action_id': resource_action['action_id'],
                'resource_type': resource.rtype,
                'principals': principals
            }
            instance = resource_action.get('instance')
            if instance:
                action['resource_id'] = utils.resource_id_for(resource, instance)

            actions.append(action)

        return AuthOperationResult(result=True,
                                   code=0,
                                   message='success',
                                   data=actions)
