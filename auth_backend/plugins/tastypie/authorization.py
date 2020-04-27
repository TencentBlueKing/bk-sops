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

from tastypie.authorization import ReadOnlyAuthorization
from tastypie.exceptions import ImmediateHttpResponse

from auth_backend.plugins.http import HttpResponseAuthFailed
from auth_backend.plugins.utils import build_need_permission

logger = logging.getLogger('root')


class BkSaaSReadOnlyAuthorization(ReadOnlyAuthorization):
    """
    @summary: 严格接入权限中心的Tastypie ReadOnlyAuthorization
    """
    principal_type = 'user'

    def __init__(self,
                 auth_resource,
                 create_action_id='create',
                 read_action_id='read',
                 update_action_id='update',
                 delete_action_id='delete',
                 resource_f=None,
                 create_delegation=None,
                 inspect=None):
        self.auth_resource = auth_resource
        if resource_f is not None:
            self.resource_pk_field = '%s__pk' % resource_f
        else:
            self.resource_pk_field = 'pk'
        self.resource_pk_field_in = '%s__in' % self.resource_pk_field
        self.create_action_id = create_action_id
        self.read_action_id = read_action_id
        self.update_action_id = update_action_id
        self.delete_action_id = delete_action_id
        self.resource_f = resource_f
        self.create_delegation = create_delegation
        self.inspect = inspect

    def scope_id_for_bundle(self, bundle):
        if not self.inspect:
            return None

        return self.inspect.scope_id(bundle)

    def build_auth_failed_response(self, action_ids, instance, auth_resource=None, scope_id=None):
        if auth_resource is None:
            auth_resource = self.auth_resource
        if self.resource_f is not None:
            instance = getattr(instance, self.resource_f)
        if isinstance(action_ids, list):
            permission = [build_need_permission(
                auth_resource=auth_resource,
                action_id=action_id,
                instance=instance,
                scope_id=scope_id
            ) for action_id in action_ids]
        else:
            permission = [build_need_permission(
                auth_resource=auth_resource,
                action_id=action_ids,
                instance=instance,
                scope_id=scope_id
            )]
        return ImmediateHttpResponse(HttpResponseAuthFailed(permission))

    def authorized_list(self, username, action_id, scope_id=None):
        authorized_result = self.auth_resource.backend.search_authorized_resources(resource=self.auth_resource,
                                                                                   principal_type=self.principal_type,
                                                                                   principal_id=username,
                                                                                   action_ids=[action_id],
                                                                                   scope_id=scope_id)
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
        authorized_pks = self.authorized_list(username, self.read_action_id, self.scope_id_for_bundle(bundle))
        return object_list.filter(**{self.resource_pk_field_in: authorized_pks})

    def read_detail(self, object_list, bundle):
        if bundle.obj not in self.read_list(object_list, bundle):
            raise self.build_auth_failed_response(self.read_action_id, bundle.obj,
                                                  scope_id=self.scope_id_for_bundle(bundle))
        return True


class BkSaaSAuthorization(BkSaaSReadOnlyAuthorization):
    """
    @summary: 严格接入权限中心的Tastypie Authorization
    """
    def create_detail(self, object_list, bundle):

        auth_resource = self.auth_resource
        action_ids = [self.create_action_id]
        instance = None

        if self.create_delegation:
            auth_resource = self.create_delegation.delegate_resource
            action_ids = self.create_delegation.action_ids
            instance = self.create_delegation.delegate_instance(bundle.obj)

        username = bundle.request.user.username
        authorized_result = auth_resource.verify_perms(principal_type=self.principal_type,
                                                       principal_id=username,
                                                       action_ids=action_ids,
                                                       instance=instance)
        if not authorized_result['result'] or not authorized_result['data'][0]['is_pass']:
            if not authorized_result['result']:
                logger.error('Verify perms of Resource[{resource}] return error: {error}'.format(
                    resource=auth_resource.name,
                    error=authorized_result['message']
                ))
            raise self.build_auth_failed_response(action_ids, instance, auth_resource=auth_resource,
                                                  scope_id=self.scope_id_for_bundle(bundle))
        return True

    def update_list(self, object_list, bundle):
        username = bundle.request.user.username
        authorized_pks = self.authorized_list(username, self.update_action_id, self.scope_id_for_bundle(bundle))
        return object_list.filter(**{self.resource_pk_field_in: authorized_pks})

    def update_detail(self, object_list, bundle):
        if not self.update_list(object_list, bundle).filter(**{self.resource_pk_field: bundle.obj.pk}).exists():
            raise self.build_auth_failed_response(self.update_action_id, bundle.obj,
                                                  scope_id=self.scope_id_for_bundle(bundle))
        return True

    def delete_list(self, object_list, bundle):
        username = bundle.request.user.username
        authorized_pks = self.authorized_list(username, self.delete_action_id, self.scope_id_for_bundle(bundle))
        return object_list.filter(**{self.resource_pk_field_in: authorized_pks})

    def delete_detail(self, object_list, bundle):
        if not self.delete_list(object_list, bundle).filter(**{self.resource_pk_field: bundle.obj.pk}).exists():
            raise self.build_auth_failed_response(self.delete_action_id, bundle.obj,
                                                  scope_id=self.scope_id_for_bundle(bundle))
        return True


class BkSaaSLooseReadOnlyAuthorization(BkSaaSReadOnlyAuthorization):
    """
    @summary: 宽松接入（read_list不鉴权）权限中心的Tastypie ReadOnlyAuthorization
    """
    def read_list(self, object_list, bundle):
        return object_list

    def read_detail(self, object_list, bundle):
        if bundle.obj not in super(BkSaaSLooseReadOnlyAuthorization, self).read_list(object_list, bundle):
            raise self.build_auth_failed_response(self.read_action_id, bundle.obj,
                                                  scope_id=self.scope_id_for_bundle(bundle))
        return True


class BkSaaSLooseAuthorization(BkSaaSLooseReadOnlyAuthorization, BkSaaSAuthorization):
    """
    @summary: 宽松接入（read_list不鉴权）权限中心的Tastypie Authorization
    """
    pass
