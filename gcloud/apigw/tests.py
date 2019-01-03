# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json
import requests

from django.test import TestCase
from gcloud.conf import settings


# 运行流程-> 查询所有模板->查询单个模板->创建模板->运行->暂停->继续执行


class APITest(TestCase):
    kwargs = {
        'app_code': settings.APP_CODE,
        'app_secret': settings.SECRET_KEY,
        'name': u'测试模板',
        'flow_type': 'common',
    }
    header_kwargs = {
        'BK-USERNAME': 'admin',
    }

    def test_template(self):
        """
        测试获取所有模板，获取单个模板，创建模板，执行模板，查询任务状态，暂停执行模板，查询任务状态,继续执行模板，查询任务状态
        """

        # 添加access_token 或BK_TOKEN
        self.kwargs.update(settings.TEST_TOKEN)
        # 获取所有模板
        self.test_flow('%s/get_template_list/%s/' % (settings.TEST_API_URL, settings.TEST_BK_BIZ_ID), False)

        # 获取单个模板
        self.test_flow('%s/get_template_info/%s/%s/' % (
            settings.TEST_API_URL, settings.TEST_TEMPLATE_ID, settings.TEST_BK_BIZ_ID), False)

        # 创建任务并获得id
        task_id = self.test_flow('%s/create_task/%s/%s/' % (
            settings.TEST_API_URL, settings.TEST_TEMPLATE_ID, settings.TEST_BK_BIZ_ID), True, True)

        # 执行任务
        self.test_flow('%s/start_task/%s/%s/' % (settings.TEST_API_URL, task_id, settings.TEST_BK_BIZ_ID), True)

        # 查询当前执行状态
        self.test_flow('%s/get_task_status/%s/%s/' % (settings.TEST_API_URL, task_id, settings.TEST_BK_BIZ_ID),
                       False)

        # 暂停流程
        self.kwargs['action'] = 'pause'
        self.test_flow('%s/operate_task/%s/%s/' % (settings.TEST_API_URL, task_id, settings.TEST_BK_BIZ_ID), True)
        self.test_flow('%s/get_task_status/%s/%s/' % (settings.TEST_API_URL, task_id, settings.TEST_BK_BIZ_ID),
                       False)

        # 继续执行
        self.kwargs['action'] = 'resume'
        self.test_flow('%s/operate_task/%s/%s/' % (settings.TEST_API_URL, task_id, settings.TEST_BK_BIZ_ID), True)
        self.test_flow('%s/get_task_status/%s/%s/' % (settings.TEST_API_URL, task_id, settings.TEST_BK_BIZ_ID),
                       False)

    def test_flow(self, url, post_or_get, has_task_id=False):
        """
        :param url: 发送api的网址
        :param post_or_get: post 或者get请求
        :param has_task_id:是否需要返回任务id
        """
        task_id = None
        if post_or_get:
            response = requests.post(url, json.dumps(self.kwargs), headers=self.header_kwargs)
        else:
            response = requests.get(url, self.kwargs, headers=self.header_kwargs)
        result = response.json()
        self.assertTrue(self, result['result'])
        if has_task_id:
            task_id = result['data']['task_id']
        return task_id
