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

import json
import logging

import requests
from requests.exceptions import HTTPError

from . import conf

logger = logging.getLogger('component')


class BKIAMClient(object):

    def __init__(self, app_code=None, app_secret=None, bk_iam_host=None, version=None,
                 system_id=None, system_name=None):
        self.app_code = app_code or conf.APP_CODE
        self.app_secret = app_secret or conf.SECRET_KEY
        self.bk_iam_host = (bk_iam_host or conf.BK_IAM_HOST).rstrip('/')
        self.version = version or conf.BK_IAM_API_VERSION
        self.system_id = system_id or conf.SYSTEM_ID
        self.system_name = system_name or conf.SYSTEM_NAME

        self._bk_iam_api_base = '{host}/{prefix}'.format(host=self.bk_iam_host,
                                                         prefix='bkiam/api')

    def _request_url(self, path):
        return '{base}/{version}/{path}'.format(base=self._bk_iam_api_base, version=self.version, path=path.lstrip('/'))

    def _perm_api_url(self, path):
        return self._request_url(path='perm/systems/{system_id}/{path}'.format(system_id=self.system_id,
                                                                               path=path.lstrip('/')))

    def _resource_api_url(self, path):
        return self._request_url(path='perm/systems/{system_id}/resources/{path}'.format(system_id=self.system_id,
                                                                                         path=path.lstrip('/')))

    def _perm_model_api_url(self, path):
        return self._request_url(path='perm-model/systems/{system_id}/{path}'.format(system_id=self.system_id,
                                                                                     path=path.lstrip('/')))

    def _request(self, method, url, params=None, data=None, headers=None):
        method_func = getattr(requests, method)

        _headers = {
            "X-BK-APP-CODE": self.app_code,
            "X-BK-APP-SECRET": self.app_secret,
            "Content-Type": "application/json"
        }

        if headers:
            _headers.update(headers)

        logger.debug(
            u'bk_iam client request({method}) {url} with headers: {headers}, data: {data}, params: {params}'.format(
                method=method, url=url, headers=_headers, data=data, params=params
            ))

        response = method_func(url, data=json.dumps(data or {}), headers=_headers, params=params or {})

        try:
            response.raise_for_status()
        except HTTPError as e:
            message = u'bk_iam request({url}) error: {e}, response: {response}'.format(
                url=response.request.url, e=e, response=response.text)
            logger.error(message)

            return {
                'result': False,
                'message': message
            }

        try:
            resp_data = response.json()
            logger.debug(u'bk_iam request({url}) return: {data}'.format(url=response.request.url, data=resp_data))
            if not resp_data['result']:
                logger.error(u'bk_iam return error, message {message}, request_id={request_id}, '
                             u'url={url}, headers={headers}, params={params}, data={data}, '
                             u'response={response}'.format(message=resp_data['message'],
                                                           request_id=resp_data.get('request_id'),
                                                           url=url,
                                                           headers=_headers,
                                                           params=params,
                                                           data=data,
                                                           response=response.text))
            return resp_data
        except Exception as e:
            message = u'bk_iam request({url}) error, response json convert failed: {e}, response: {response}'.format(
                url=response.request.url, e=e, response=response.content)
            logger.error(message)

            return {
                'result': False,
                'message': message
            }

    def batch_verify_resources_perms(self, principal_type, principal_id, scope_type, scope_id, resources_actions):
        """批量校验权限

        Arguments:
            principal_type {str} -- 主体类型
            principal_id {str} -- 主体 ID
            scope_type {str} -- 作用域类型
            scope_id {str} -- 作用域 ID
            resources_actions {list} -- 操作列表 [
                {
                    'action_id': '操作 ID',
                    'resource_type': '资源类型',
                    'resource_id': '资源 ID',
                }, ...
            ]

        """
        return self._request(method='post',
                             url=self._perm_api_url(path='resources-perms/batch-verify'),
                             data={'principal_type': principal_type,
                                   'principal_id': principal_id,
                                   'scope_type': scope_type,
                                   'scope_id': scope_id,
                                   'resources_actions': resources_actions
                                   })

    def batch_verify_any_resources_perms(self, principal_type, principal_id, scope_type, scope_id, resources_actions):
        """批量查询用户是否有任意一个资源实例的操作权限

        Arguments:
            principal_type {str} -- 主体类型
            principal_id {str} -- 主体 ID
            scope_type {str} -- 作用域类型
            scope_id {str} -- 作用域 ID
            resources_actions {list} -- 操作列表 [
                {
                    'action_id': '操作 ID',
                    'resource_type': '资源类型',
                }, ...
            ]
        """
        return self._request(method='post',
                             url=self._perm_api_url(path='any-resources-perms/batch-verify'),
                             data={'principal_type': principal_type,
                                   'principal_id': principal_id,
                                   'scope_type': scope_type,
                                   'scope_id': scope_id,
                                   'resources_actions': resources_actions})

    def batch_verify_combine_resources_perms(self, principal_type, principal_id, scope_type, scope_id,
                                             resources_actions):
        """批量查询用户是否有某个资源 & 依赖资源的某个的权限

        Arguments:
            principal_type {str} -- 主体类型
            principal_id {str} -- 主体 ID
            scope_type {str} -- 作用域类型
            scope_id {str} -- 作用域 ID
            resources_actions {list} -- 操作列表 [
                {
                    'action_id': '操作 ID',
                    'combine_resource_type': [] # 依赖资源类型列表,
                    'combine_resource': [
                        [
                            {
                                'resource_type': '资源类型',
                                'resource_id': '资源实例 ID'
                            }, ...
                        ], ...
                    ]
                }, ...
            ]
        """
        return self._request(method='post',
                             url=self._perm_api_url(path='combine-resources-perms/batch-verify'),
                             data={'principal_type': principal_type,
                                   'principal_id': principal_id,
                                   'scope_type': scope_type,
                                   'scope_id': scope_id,
                                   'resources_actions': resources_actions})

    def search_authorized_resources(self, principal_type, principal_id, scope_type, scope_id,
                                    resource_types_actions, resource_data_type, is_exact_resource):
        """批量查询用户有某个权限的资源

        Arguments:
            principal_type {str} -- 主体类型
            principal_id {str} -- 主体 ID
            scope_type {str} -- 作用域类型
            scope_id {str} -- 作用域 ID
            resource_types_actions {list} -- 资源操作列表 [
                {
                    'action_id': '操作类型',
                    'resource_type': '资源类型'
                }, ...
            ]
            resource_data_type {str} -- [description]
            is_exact_resource {bool} -- [description]

        """
        return self._request(method='post',
                             url=self._perm_api_url(path='authorized-resources/search'),
                             data={'principal_type': principal_type,
                                   'principal_id': principal_id,
                                   'scope_type': scope_type,
                                   'scope_id': scope_id,
                                   'resource_types_actions': resource_types_actions,
                                   "resource_data_type": resource_data_type,
                                   "is_exact_resource": is_exact_resource})

    def search_authorized_scopes(self, scope_type_id, principal_type, principal_id):
        """批量查询有任意一点权限的资源所属实例列表

        Arguments:
            scope_type_id {str} -- 资源作用域 ID
            principal_type {str} -- 主体类型
            principal_id {str} -- 主体 ID

        """
        return self._request(method='post',
                             url=self._request_url(path='perm/scope_type/{scope_type_id}/authorized-scopes'.format(
                                 scope_type_id=scope_type_id)),
                             data={'principal_type': principal_type,
                                   'principal_id': principal_id})

    def search_resources_perms_principals(self, scope_type, scope_id, resources_actions):
        """批量查询有权限的用户

        Arguments:
            scope_type {str} -- 作用域类型
            scope_id {str} -- 作用域 ID
            resources_actions {list} -- 资源操作列表 [
                {
                    'action_id': '操作',
                    'resource_type': '资源类型',
                    'resource_id': [{
                            'resource_type': '资源类型',
                            'resource_id': '资源实例 ID'
                    }], ...
                }, ...
            ]

        """
        return self._request(method='post',
                             url=self._perm_api_url(path='/resources-perms-principals/search'),
                             data={'scope_type': scope_type,
                                   'scope_id': scope_id,
                                   'resources_actions': resources_actions})

    def register_resource(self, creator_type, creator_id, scope_type, scope_id, resource_type, resource_id,
                          resource_name):
        """注册资源实例

        Arguments:
            creator_type {str} -- 创建者类型
            creator_id {str} -- 创建者 ID
            scope_type {str} -- 作用域类型
            scope_id {str} -- 作用域 ID
            resource_type {str} -- 资源类型
            resource_id {str} -- 资源实例 ID  [
                        {
                            'resource_type': '资源类型',
                            'resource_id': '资源实例 ID'
                        }, ...
                    ],
            resource_name {str} -- 资源实例名
        """
        return self.batch_register_resource(creator_type=creator_type,
                                            creator_id=creator_id,
                                            resources=[
                                                {
                                                    'scope_type': scope_type,
                                                    'scope_id': scope_id,
                                                    'resource_type': resource_type,
                                                    'resource_id': resource_id,
                                                    'resource_name': resource_name
                                                }
                                            ])

    def batch_register_resource(self, creator_type, creator_id, resources):
        """批量注册资源实例

        Arguments:
            creator_type {str} -- 创建者类型
            creator_id {str} -- 创建者 ID
            resources {list} -- 注册资源列表 [
                {
                    'scope_type': '作用域类型',
                    'scope_id': '作用域 ID',
                    'resource_type': '资源类型',
                    'resource_id': [
                        {
                            'resource_type': '资源类型',
                            'resource_id': '资源实例 ID'
                        }, ...
                    ],
                    'resource_name': '资源实例名'
                }, ...
            ]
        """
        return self._request(method='post',
                             url=self._resource_api_url(path='batch-register'),
                             data={'creator_type': creator_type,
                                   'creator_id': creator_id,
                                   'resources': resources})

    def delete_resource(self, scope_type, scope_id, resource_type, resource_id):
        """删除资源实例

        Arguments:
            scope_type {str} -- 作用域类型
            scope_id {str} -- 作用域 ID
            resource_type {str} -- 资源类型
            resource_id {str} -- 资源实例 ID
        """
        return self.batch_delete_resource(resources=[
            {
                'scope_type': scope_type,
                'scope_id': scope_id,
                'resource_type': resource_type,
                'resource_id': resource_id
            }
        ])

    def batch_delete_resource(self, resources):
        """批量删除资源实例

        Arguments:
            resources {list} -- 注册资源列表 [
                {
                    'scope_type': '作用域类型',
                    'scope_id': '作用域 ID',
                    'resource_type': '资源类型',
                    'resource_id': [
                        {
                            'resource_type': '资源类型',
                            'resource_id': '资源实例 ID'
                        }, ...
                    ]
                }, ...
            ]
        """
        return self._request(method='delete',
                             url=self._resource_api_url(path='batch-delete'),
                             data={'resources': resources})

    def update_resource(self, scope_type, scope_id, resource_type, resource_id, resource_name):
        """更新资源实例

        Arguments:
            scope_type {str} -- 作用域类型
            scope_id {str} -- 作用域 ID
            resource_type {str} -- 资源类型
            resource_id {str} -- 资源实例 ID
            resource_name {str} -- 资源实例名
        """
        return self._request(method='put',
                             url=self._resource_api_url(path=''),
                             data={'scope_type': scope_type,
                                   'scope_id': scope_id,
                                   'resource_type': resource_type,
                                   'resource_id': resource_id,
                                   'resource_name': resource_name})

    def register_system(self, system_name, desc, query_interface, related_scope_types, managers, creator,
                        system_id=None):
        """注册系统

        Arguments:
            system_name {str} -- 系统名
            desc {str} -- 系统名
            query_interface {str} -- 资源获取 api
            related_scope_types {str} -- 关联的资源所属，有业务、全局、项目等
            managers {str} -- 管理者
            creator {str} -- 创建人
        """
        return self._request(method='post',
                             url=self._request_url(path='perm-model/systems'),
                             data={'system_id': system_id or self.system_id,
                                   'system_name': system_name,
                                   'desc': desc,
                                   'query_interface': query_interface,
                                   'releated_scope_types': related_scope_types,
                                   'managers': managers,
                                   'creator': creator})

    def modify_system_info(self, system_name, desc, query_interface, related_scope_types, managers, updater):
        """修改系统基本信息

        Arguments:
            system_name {str} -- 系统名
            desc {str} -- 系统名
            query_interface {str} -- 资源获取 api
            related_scope_types {str} -- 关联的资源所属，有业务、全局、项目等
            managers {str} -- 管理者
            updater {str} -- 更新人
        """
        return self._request(method='put',
                             url=self._perm_model_api_url(''),
                             data={'system_name': system_name,
                                   'desc': desc,
                                   'query_interface': query_interface,
                                   'releated_scope_types': related_scope_types,
                                   'managers': managers,
                                   'updater': updater})

    def batch_upsert_resource_types(self, scope_type, resource_types):
        """添加或更新系统资源类型

        Arguments:
            scope_type {str} -- 作用域类型
            resource_types {list} -- 资源类型列表 [
                {
                    'resource_type': '资源类型',
                    'resource_name': '资源名称',
                    'parent_resource_type': '父资源类型',
                    'actions': [
                        {
                            'action_id': '操作id',
                            'action_name': '操作名',
                            'is_related_resource': False # 是否关联资源
                        }, ...
                    ]
                }, ...
            ]
        """
        return self._request(method='post',
                             url=self._perm_model_api_url(
                                 path='scope-types/{scope_type}/resource-types/batch-upsert'.format(
                                     scope_type=scope_type)),
                             data={'resource_types': resource_types})

    def delete_resource_type(self, scope_type, resource_type):
        """删除资源类型

        Arguments:
            scope_type {str} -- [作用域类型]
            resource_type {str} -- [资源类型]

        """
        return self._request(method='delete',
                             url=self._perm_model_api_url(
                                 path='scope-types/{scope_type}/resource-types/{resource_type}').format(
                                 scope_type=scope_type,
                                 resource_type=resource_type))

    def get_system_info(self, is_detail=True):
        """获取系统详细信息

        """
        return self._request(method='get', url=self._perm_model_api_url(''), params={'is_detail': int(is_detail)})

    def upsert_perm_template(self, perm_template_name, template_id, desc, resource_types_actions):
        """添加或更新权限模板

        Arguments:
            perm_template_name {str} -- [权限模板名]
            template_id {str} -- [模板 ID]
            desc {str} --- [模板描述]
            resource_types_actions {list} - 权限模板操作 [
                {
                    'scope_type_id: '作用域 ID',
                    'resource_type_id': '资源类型 ID',
                    'action_id': '动作 ID'
                }, ...
            ]

        """
        return self._request(method='post',
                             url=self._perm_model_api_url(path='perm-templates'),
                             data={'perm_template_name': perm_template_name,
                                   'template_id': template_id,
                                   'desc': desc,
                                   'resource_types_actions': resource_types_actions})
