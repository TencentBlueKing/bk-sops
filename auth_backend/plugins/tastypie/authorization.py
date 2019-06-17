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

import logging

from tastypie.authorization import ReadOnlyAuthorization
from tastypie.exceptions import ImmediateHttpResponse

from ..http import HttpResponseAuthFailed

logger = logging.getLogger('root')


class BkSaaSReadOnlyAuthorization(ReadOnlyAuthorization):
    principal_type = 'user'

    def __init__(self, auth_resource, create_action_id='create', read_action_id='read', update_action_id='update',
                 delete_action_id='delete', create_delegation=None):
        self.auth_resource = auth_resource
        self.create_action_id = create_action_id
        self.read_action_id = read_action_id
        self.update_action_id = update_action_id
        self.delete_action_id = delete_action_id
        self.create_delegation = create_delegation

    def build_auth_failed_response(self, resource_name, action_id):
        return ImmediateHttpResponse(HttpResponseAuthFailed(
            resource_type_name=self.auth_resource.name,
            resource_name=resource_name,
            action_name=self.auth_resource.actions_map[action_id].name
        ))

    def authorized_list(self, username, action_id):
        authorized_result = self.auth_resource.backend.search_authorized_resources(resource=self.auth_resource,
                                                                                   principal_type=self.principal_type,
                                                                                   principal_id=username,
                                                                                   action_ids=[action_id])
        if not authorized_result['result']:
            logger.error('Search authorized resources of Resource[{resource}] return error: {error}'.format(
                resource=self.auth_resource.name,
                error=authorized_result['message']
            ))
            return []
        authorized_resources = authorized_result['data']
        authorized_resource_pks = []
        for action_resource in authorized_resources:
            if action_resource['action_id'] == action_id:
                for absolute_resource in action_resource['resource_ids']:
                    for relative_resource in absolute_resource:
                        if relative_resource['resource_type'] == self.auth_resource.rtype:
                            authorized_resource_pks.append(relative_resource['resource_id'])
        return authorized_resource_pks

    def read_list(self, object_list, bundle):
        username = bundle.request.user.username
        authorized_pks = self.authorized_list(username, self.read_action_id)
        return object_list.filter(pk__in=authorized_pks)

    def read_detail(self, object_list, bundle):
        if bundle.obj not in self.read_list(object_list, bundle):
            raise self.build_auth_failed_response(bundle.obj.name, self.read_action_id)
        return True


class BkSaaSAuthorization(BkSaaSReadOnlyAuthorization):

    def create_detail(self, object_list, bundle):

        auth_resource = self.auth_resource
        action_ids = [self.create_action_id]
        instance = None

        if self.create_delegation:
            auth_resource = self.create_delegation.delegate_resource
            action_ids = self.create_delegation.action_ids
            if self.create_delegation.instance_field:
                instance = getattr(bundle.obj, self.create_delegation.instance_field)

        username = bundle.request.user.username
        authorized_result = auth_resource.verify_perms(principal_type=self.principal_type,
                                                       principal_id=username,
                                                       action_ids=action_ids,
                                                       instance=instance)
        if not authorized_result['result'] or not authorized_result['data'][0]['is_paas']:
            if not authorized_result['result']:
                logger.error('Verify perms of Resource[{resource}] return error: {error}'.format(
                    resource=auth_resource.name,
                    error=authorized_result['message']
                ))
            return False
        return True

    def update_list(self, object_list, bundle):
        username = bundle.request.user.username
        authorized_pks = self.authorized_list(username, self.update_action_id)
        return object_list.filter(pk__in=authorized_pks)

    def update_detail(self, object_list, bundle):
        if not self.update_list(object_list, bundle).filter(pk=bundle.obj.pk).exists():
            raise self.build_auth_failed_response(bundle.obj.name, self.update_action_id)
        return True

    def delete_list(self, object_list, bundle):
        username = bundle.request.user.username
        authorized_pks = self.authorized_list(username, self.delete_action_id)
        return object_list.filter(pk__in=authorized_pks)

    def delete_detail(self, object_list, bundle):
        if not self.delete_list(object_list, bundle).filter(pk=bundle.obj.pk).exists():
            raise self.build_auth_failed_response(bundle.obj.name, self.delete_action_id)
        return True


class BkSaaSLooseReadOnlyAuthorization(BkSaaSReadOnlyAuthorization):
    def read_list(self, object_list, bundle):
        return object_list

    def read_detail(self, object_list, bundle):
        if bundle.obj not in super(BkSaaSLooseReadOnlyAuthorization, self).read_list(object_list, bundle):
            raise self.build_auth_failed_response(bundle.obj.name, self.read_action_id)
        return True


class BkSaaSLooseAuthorization(BkSaaSLooseReadOnlyAuthorization, BkSaaSAuthorization):
    pass
