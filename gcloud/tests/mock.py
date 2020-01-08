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

from __future__ import absolute_import

import mock  # noqa
from mock import MagicMock, patch  # noqa

from django.utils.timezone import now


class MockRequest(object):
    def __init__(self, method, data):
        self.method = method
        setattr(self, method, data)
        self.user = MagicMock()


class MockJsonResponse(object):
    def __call__(self, dct):
        return dct


class MockBusiness(object):
    def __init__(self, **kwargs):
        self.cc_id = kwargs.get('cc_id', 'cc_id')
        self.cc_name = kwargs.get('cc_name', 'cc_name')
        self.time_zone = kwargs.get('time_zone', 'time_zone')


class MockPipelineTemplate(object):
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 'id')
        self.name = kwargs.get('name', 'name')
        self.creator = kwargs.get('creator', 'creator')
        self.edit_time = kwargs.get('edit_time', now())
        self.editor = kwargs.get('editor', 'editor')
        self.create_time = kwargs.get('create_time', now())


class MockBaseTemplate(object):
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 'id')
        self.name = kwargs.get('name', 'name')
        self.category = kwargs.get('category', 'category')
        self.pipeline_template = kwargs.get('pipeline_template', MockPipelineTemplate())
        self.pipeline_tree = kwargs.get('pipeline_tree',
                                        {'line': 'line', 'location': 'location', 'activities': []})
        self.get_pipeline_tree_by_version = MagicMock(return_value=self.pipeline_tree)


class MockTaskTemplate(MockBaseTemplate):
    pass


class MockCommonTemplate(MockBaseTemplate):
    pass


class MockTaskFlowInstance(object):
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 'id')
        self.task_action = MagicMock(return_value=kwargs.get('task_action_return', None))
        self.get_status = MagicMock(return_value=kwargs.get('get_status_return', None))
        self.get_status = MagicMock(**{'return_value': kwargs.get('get_status_return'),
                                       'side_effect': kwargs.get('get_status_raise')})
        self.format_pipeline_status = MagicMock(**{'return_value': kwargs.get('format_pipeline_status_return'),
                                                   'side_effect': kwargs.get('format_pipeline_status_raise')})
        self.url = kwargs.get('url', 'url')
        self.pipeline_tree = kwargs.get('pipeline_tree', 'pipeline_tree')
        self.callback = MagicMock(return_value=kwargs.get('callback_return', {'result': True,
                                                                              'message': 'success'}))
        self.get_task_detail = MagicMock(return_value=kwargs.get('get_task_detail_return', 'task_detail'))
        self.get_node_detail = MagicMock(return_value=kwargs.get('get_node_detail_return', {'result': True,
                                                                                            'data': 'data'}))


class MockPeriodicTask(object):
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 'id')
        self.name = kwargs.get('name', 'name')
        self.template_id = kwargs.get('template_id', 'template_id')
        self.creator = kwargs.get('creator', 'creator')
        self.cron = kwargs.get('cron', 'cron')
        self.enabled = kwargs.get('enabled', False)
        self.last_run_at = kwargs.get('last_run_at', now())
        self.total_run_count = kwargs.get('total_run_count', 0)
        self.form = kwargs.get('form', 'form')
        self.pipeline_tree = kwargs.get('pipeline_tre', 'pipeline_tree')

        self.set_enabled = MagicMock()
        self.modify_cron = MagicMock()
        self.modify_constants = MagicMock(return_value=kwargs.get('modify_constants_result'))


class MockQuerySet(object):
    def __init__(self,
                 get_result=None,
                 get_raise=None,
                 filter_result=None):
        self.get = MagicMock(return_value=get_result) if get_result else MagicMock(side_effect=get_raise)
        self.filter = MagicMock(return_value=filter_result)


class MockSyncPackageSource(object):
    def __init__(self, id, type):
        self.id = id
        self.type = MagicMock(return_value=type)
