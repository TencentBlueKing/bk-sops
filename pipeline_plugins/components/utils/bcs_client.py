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

from __future__ import unicode_literals

import os
import logging

import requests
import ujson as json
from requests import HTTPError
from django.conf import settings

from bkiam import bkiam_client

logger = logging.getLogger('component')


class Login(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({'referer': '{}'.format(settings.BK_PAAS_HOST)})
        self.session.verify = False
        self.bk_token = None
        self.error = None

    def refresh_csrftoken(self):
        url = '{}{}'.format(settings.BK_PAAS_HOST, '/login/')

        resp = self.session.get(url, verify=False)

        try:
            resp.raise_for_status()
        except HTTPError as e:
            self.error = 'user[{}] login csrftoken fetch failed'.format(self.username)
            logger.error('Login get_csrftoken failed with error: {}, content: {}'.format(
                e,
                resp.content
            ))
        else:
            self.csrftoken = resp.cookies['bklogin_csrftoken']

    def login(self):
        self.refresh_csrftoken()

        if not self.csrftoken:
            return

        login_form = {
            'csrfmiddlewaretoken': self.csrftoken,
            'username': self.username,
            'password': self.password
        }
        login_url = '{}{}'.format(settings.BK_PAAS_HOST, '/login/')

        resp = self.session.post(login_url, data=login_form, verify=False)

        try:
            resp.raise_for_status()
        except HTTPError as e:
            self.error = 'user[{}] login failed'.format(self.username)
            logger.error('Login login failed with error: {}, content: {}'.format(
                e,
                resp.content
            ))
        else:
            self.bk_token = resp.request._cookies['bk_token']


class BCSClient(object):
    def __init__(self, test=False):
        self.host = os.getenv('BKAPP_BCS_API_HOST')
        self.env_code = 't' if test else 'o'

    def _url(self, path):
        return '{host}/{env}/{path}'.format(
            host=self.host,
            env=self.env_code,
            path=path
        )

    def _get_access_token(self):
        username = os.getenv('BKAPP_BCS_PLUGINS_USERNAME', None)
        password = os.getenv('BKAPP_BCS_PLUGINS_PASSWORD', None)

        if not (username and password):
            return {
                'message': 'make sure BKAPP_BCS_PLUGINS_USERNAME and BKAPP_BCS_PLUGINS_PASSWORD is config in enviroments',
                'result': False
            }

        login = Login(username=username, password=password)
        login.login()

        if not login.bk_token:
            return {
                'message': login.error,
                'result': False
            }

        result = bkiam_client.get_access_token('authorization_code', 'bk_login', login.bk_token)
        if not result['result']:
            return {
                'message': result['message'],
                'result': False
            }

        return {
            'result': True,
            'data': result['data']
        }

    def _request(self, method, url, params=None, data=None, headers=None):
        method_func = getattr(requests, method)

        if params is None:
            params = {}

        if data is None:
            data = {}

        result = self._get_access_token()
        if not result['result']:
            return result

        access_token = result['data']['access_token']
        params['access_token'] = access_token
        data['access_token'] = access_token

        _headers = {
            "Content-Type": "application/json"
        }

        if headers:
            _headers.update(headers)

        logger.debug(
            'bcs client request({method}) {url} with headers: {headers}, data: {data}, params: {params}'.format(
                method=method, url=url, headers=_headers, data=data, params=params
            ))

        try:
            response = method_func(url, data=json.dumps(data or {}), headers=_headers, params=params or {})
        except Exception as e:
            message = 'bcs request({url}) error: {e}'.format(url=url, e=e)
            logger.error(message)

            return {
                'result': False,
                'message': message
            }

        try:
            response.raise_for_status()
        except HTTPError as e:
            message = 'bcs request({url}) error: {e}, response: {response}'.format(
                url=response.request.url, e=e, response=response.text)
            logger.error(message)

            return {
                'result': False,
                'message': message
            }

        try:
            resp_data = response.json()
            resp_data['result'] = resp_data['code'] == 0
            logger.debug('bcs request({url}) return: {data}'.format(url=response.request.url, data=resp_data))
            if not resp_data['result']:
                logger.error(
                    'bcs return error, message {message}, request_id={request_id}, '
                    'url={url}, headers={headers}, params={params}, data={data}, '
                    'response={response}'.format(
                        message=resp_data['message'],
                        request_id=resp_data.get('request_id'),
                        url=url,
                        headers=_headers,
                        params=params,
                        data=data,
                        response=response.text
                    )
                )
            return resp_data
        except Exception as e:
            message = 'bcs request({url}) error, response json convert failed: {e}, response: {response}'.format(
                url=response.request.url, e=e, response=response.text)
            logger.error(message)

            return {
                'result': False,
                'message': message
            }

    def get_clusters(self, project_id):
        return self._request(
            method='get',
            url=self._url('bk_bcs_app/cd_api/projects/{project_id}/clusters/'.format(project_id=project_id))
        )

    def get_musters(self, bk_biz_id, project_id):
        return self._request(
            method='get',
            url=self._url('bk_bcs_app/cd_api/apps/cc_app_ids/{cc_app_id}/projects/{project_id}/musters/'.format(
                cc_app_id=bk_biz_id,
                project_id=project_id
            ))
        )

    def get_muster_versions(self, bk_biz_id, project_id, muster_id):
        return self._request(
            method='get',
            url=self._url('bk_bcs_app/cd_api/apps/cc_app_ids/{cc_app_id}/projects/{project_id}/musters/{muster_id}/versions/'.format(
                cc_app_id=bk_biz_id,
                project_id=project_id,
                muster_id=muster_id
            ))
        )

    def get_namespaces(self, bk_biz_id, project_id):
        return self._request(
            method='get',
            url=self._url('bk_bcs_app/cd_api/ns/cc_app_ids/{cc_app_id}/projects/{project_id}/namespaces/'.format(
                cc_app_id=bk_biz_id,
                project_id=project_id
            ))
        )

    def get_version_templates(self, bk_biz_id, project_id, version_id):
        return self._request(
            method='get',
            url=self._url('bk_bcs_app/cd_api/apps/cc_app_ids/{cc_app_id}/projects/{project_id}/versions/{version_id}/templates/'.format(
                cc_app_id=bk_biz_id,
                project_id=project_id,
                version_id=version_id
            ))
        )

    def get_instances(self, bk_biz_id, project_id, category, namespace=None):
        params = {
            'category': category
        }
        if namespace:
            params['namespace'] = namespace
        return self._request(
            method='get',
            url=self._url('bk_bcs_app/cd_api/apps/cc_app_ids/{cc_app_id}/projects/{project_id}/instances/'.format(
                cc_app_id=bk_biz_id,
                project_id=project_id
            )),
            params=params
        )

    def get_instance_versions(self, bk_biz_id, project_id, instance_id):
        return self._request(
            method='get',
            url=self._url('bk_bcs_app/cd_api/apps/cc_app_ids/{cc_app_id}/projects/{project_id}/instances/{instance_id}/versions/'.format(
                cc_app_id=bk_biz_id,
                project_id=project_id,
                instance_id=instance_id
            ))
        )

    def create_instance(
        self,
        bk_biz_id,
        project_id,
        cluster_ns_info,
        version_id,
        show_version_id,
        instance_entity,
        show_version_name=None
    ):
        data = {
            'cluster_ns_info': cluster_ns_info,
            'version_id': version_id,
            'show_version_id': show_version_id,
            'instance_entity': instance_entity
        }
        if show_version_name:
            data['show_version_name'] = show_version_name

        return self._request(
            method='post',
            url=self._url('bk_bcs_app/cd_api/apps/cc_app_ids/{cc_app_id}/projects/{project_id}/instances/').format(
                cc_app_id=bk_biz_id,
                project_id=project_id
            ),
            data=data
        )

    def update_instance(
        self,
        bk_biz_id,
        project_id,
        instance_id,
        instance_num,
        version_id,
        variable=None
    ):
        data = {
            'instance_num': instance_num,
            'version_id': version_id,
        }

        if variable:
            data['variable'] = variable

        return self._request(
            method='put',
            url=self._url('bk_bcs_app/cd_api/apps/cc_app_ids/{cc_app_id}/projects/{project_id}/instances/{instance_id}/update/').format(
                cc_app_id=bk_biz_id,
                project_id=project_id,
                instance_id=instance_id
            ),
            data=data
        )

    def send_command(
        self,
        bk_biz_id,
        project_id,
        instance_id,
        command,
        username=None,
        work_dir=None,
        privileged=None,
        reserve_time=None,
        env=None
    ):
        data = {
            'command': command
        }
        if username:
            data['username'] = username
        if work_dir:
            data['work_dir'] = work_dir
        if privileged is not None:
            data['privileged'] = privileged
        if reserve_time is not None:
            data['reserve_time'] = reserve_time
        if env:
            data['env'] = env

        return self._request(
            method='post',
            url=self._url('bk_bcs_app/cd_api/apps/cc_app_ids/{cc_app_id}/projects/{project_id}/instances/{instance_id}/command/'.format(
                cc_app_id=bk_biz_id,
                project_id=project_id,
                instance_id=instance_id
            )),
            data=data
        )

    def get_instance_status(self, bk_biz_id, project_id, instance_id):
        return self._request(
            method='get',
            url=self._url('bk_bcs_app/cd_api/apps/cc_app_ids/{cc_app_id}/projects/{project_id}/instances/{instance_id}/status/'.format(
                cc_app_id=bk_biz_id,
                project_id=project_id,
                instance_id=instance_id
            ))
        )

    def get_command_status(self, bk_biz_id, project_id, instance_id, task_id):
        return self._request(
            method='get',
            url=self._url('bk_bcs_app/cd_api/apps/cc_app_ids/{cc_app_id}/projects/{project_id}/instances/{instance_id}/command/status/'.format(
                cc_app_id=bk_biz_id,
                project_id=project_id,
                instance_id=instance_id
            )),
            params={'task_id': task_id}
        )
