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
import time
import jsonschema
import pytz

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils import timezone

from gcloud.contrib.analysis.schemas import (
    ANALYSIS_CATEGORY_AND_BUSINESS_PARAMS,
    ANALYSIS_TASK_CATEGORY_PARAMS,
    ANALYSIS_ATOM_TEMPLATE_PARAMS,
    ANALYSIS_ATOM_INSTANCE_PARAMS,
    ANALYSIS_ATOM_EXECUTE_PARAMS,
    ANALYSIS_TEMPLATE_CITE_PARAMS,
    ANALYSIS_TEMPLATE_NODE_PARAMS,
    ANALYSIS_APPMAKER_INSTANCE_PARAMS,
    ANALYSIS_INSTANCE_NODE_PARAMS,
    ANALYSIS_INSTANCE_DETAILS_PARAMS,
    ANALYSIS_NO_DATA_PARAMS,
    ANALYSIS_TASK_CATEGORY_NO_DATA_PARAMS,
    ANALYSIS_INSTANCE_TIME_PARAMS,
)
from gcloud.contrib.analysis.views import (
    query_atom_by_group,
    query_template_by_group,
    get_task_category,
    query_appmaker_by_group,
    query_instance_by_group,
)
from gcloud.core.constant import AE


class Analysis(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        tz = pytz.timezone('Asia/Shanghai')

        # 初始请求数据
        conditions = {
            'create_time': int(time.mktime(timezone.datetime(2018, 6, 12, tzinfo=tz).timetuple())) * 1000,
            'finish_time': int(time.mktime(timezone.now().timetuple())) * 1000,
            'biz_cc_id': 2,
            'category': 'OpsTools',
            'type': 'day'
        }
        conditions = json.dumps(conditions)
        self.postRequest = self.factory.post('', data={
            'conditions': conditions,
            'group_by': '',
            'limit': 15,
            'pageIndex': 1
        })
        self.getRequest = self.factory.get('', data={
            'conditions': conditions,
            'group_by': '',
            'limit': 15,
            'pageIndex': 1
        })
        # 创建测试数据 测试管理员
        user_model = get_user_model()
        # 获得管理员user
        self.postRequest.user = user_model.objects.create(username='admin', is_superuser=True, is_staff=True)
        self.getRequest.user = self.postRequest.user
        self.postRequest.POST = self.postRequest.POST.copy()

    def test_instance_group_by_time(self):
        """
        按起始时间、业务（可选）、类型（可选）、图表类型（日视图，月视图），查询每一天或每一月的执行数量
        :return:
        """
        self.postRequest.path = '/analysis/query_instance_by_group/'
        self.postRequest.POST['group_by'] = AE.instance_time
        response = query_instance_by_group(self.postRequest)
        response_dict = json.loads(response.content)
        if response_dict["data"]["total"] == 0:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_NO_DATA_PARAMS), None)
        else:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_INSTANCE_TIME_PARAMS), None)

    def test_instance_group_by_details(self):
        """
        任务实例各任务执行耗时
        :return:
        """
        self.postRequest.path = '/analysis/query_instance_by_group/'
        self.postRequest.POST['group_by'] = AE.instance_details
        response = query_instance_by_group(self.postRequest)
        response_dict = json.loads(response.content)
        if response_dict["data"]["total"] == 0:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_NO_DATA_PARAMS), None)
        else:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_INSTANCE_DETAILS_PARAMS), None)

    def test_instance_group_by_node(self):
        """
        任务实例各任务中实际执行的标准插件节点、子流程节点、网关节点个数
        :return:
        """
        self.postRequest.path = '/analysis/query_instance_by_group/'
        self.postRequest.POST['group_by'] = AE.instance_node
        response = query_instance_by_group(self.postRequest)
        response_dict = json.loads(response.content)
        if response_dict["data"]["total"] == 0:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_NO_DATA_PARAMS), None)
        else:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_INSTANCE_NODE_PARAMS), None)

    def test_instance_group_by_cc_id(self):
        """
        任务实例按业务维度统计数据
        :return:
        """
        self.postRequest.path = '/analysis/query_instance_by_group/'
        self.postRequest.POST['group_by'] = AE.biz_cc_id
        response = query_instance_by_group(self.postRequest)
        response_dict = json.loads(response.content)
        if response_dict["data"]["total"] == 0:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_NO_DATA_PARAMS), None)
        else:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_CATEGORY_AND_BUSINESS_PARAMS), None)

    def test_instance_group_by_category(self):
        """
        任务实例分类统计数据
        :return:
        """
        self.postRequest.path = '/analysis/query_instance_by_group/'
        self.postRequest.POST['group_by'] = AE.category
        response = query_instance_by_group(self.postRequest)
        response_dict = json.loads(response.content)
        if response_dict["data"]["total"] == 0:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_NO_DATA_PARAMS), None)
        else:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_CATEGORY_AND_BUSINESS_PARAMS), None)

    def test_appmaker_group_by_instance(self):
        """
        各轻应用详情和创建任务个数
        :return:
        """
        self.postRequest.path = '/analysis/query_appmaker_by_group/'
        self.postRequest.POST['group_by'] = AE.appmaker_instance
        response = query_appmaker_by_group(self.postRequest)
        response_dict = json.loads(response.content)
        if response_dict["data"]["total"] == 0:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_NO_DATA_PARAMS), None)
        else:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_APPMAKER_INSTANCE_PARAMS), None)

    def test_appmaker_group_by_category(self):
        """
        各类型轻应用个数和占比
        :return:
        """
        self.postRequest.path = '/analysis/query_appmaker_by_group/'
        self.postRequest.POST['group_by'] = AE.category
        response = query_appmaker_by_group(self.postRequest)
        response_dict = json.loads(response.content)
        if response_dict["data"]["total"] == 0:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_NO_DATA_PARAMS), None)
        else:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_CATEGORY_AND_BUSINESS_PARAMS), None)

    def test_appmaker_group_by_cc_id(self):
        """
        各业务中轻应用个数和占比
        :return:
        """
        self.postRequest.path = '/analysis/query_appmaker_by_group/'
        self.postRequest.POST['group_by'] = AE.biz_cc_id
        response = query_appmaker_by_group(self.postRequest)
        response_dict = json.loads(response.content)
        if response_dict["data"]["total"] == 0:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_NO_DATA_PARAMS), None)
        else:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_CATEGORY_AND_BUSINESS_PARAMS), None)

    def test_template_group_by_cc_id(self):
        """
        流程模板按业务维度统计数据
        :return:
        """
        self.postRequest.path = '/analysis/query_template_by_group/'
        self.postRequest.POST['group_by'] = AE.biz_cc_id
        response = query_template_by_group(self.postRequest)
        response_dict = json.loads(response.content)
        if response_dict["data"]["total"] == 0:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_NO_DATA_PARAMS), None)
        else:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_CATEGORY_AND_BUSINESS_PARAMS), None)

    def test_template_group_by_category(self):
        """
        流程模板分类统计数据
        :return:
        """
        self.postRequest.path = '/analysis/query_template_by_group/'
        self.postRequest.POST['group_by'] = AE.category
        response = query_template_by_group(self.postRequest)
        response_dict = json.loads(response.content)
        if response_dict["data"]["total"] == 0:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_NO_DATA_PARAMS), None)
        else:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_CATEGORY_AND_BUSINESS_PARAMS), None)

    def test_template_group_by_node(self):
        """
        各流程模板中标准插件节点、子流程节点、网关节点个数
        :return:
        """
        self.postRequest.path = '/analysis/query_template_by_group/'
        self.postRequest.POST['group_by'] = AE.template_node
        response = query_template_by_group(self.postRequest)
        response_dict = json.loads(response.content)
        if response_dict["data"]["total"] == 0:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_NO_DATA_PARAMS), None)
        else:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_TEMPLATE_NODE_PARAMS), None)

    def test_template_group_by_cite(self):
        """
        各流程模板被引用为子流程次数、创建轻应用个数、创建任务个数
        :return:
        """
        self.postRequest.path = '/analysis/query_template_by_group/'
        self.postRequest.POST['group_by'] = AE.template_cite
        response = query_template_by_group(self.postRequest)
        response_dict = json.loads(response.content)
        if response_dict["data"]["total"] == 0:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_NO_DATA_PARAMS), None)
        else:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_TEMPLATE_CITE_PARAMS), None)

    def test_atom_group_by_execute(self):
        """
        标准插件执行耗时
        :return:
        """
        self.postRequest.path = '/analysis/query_atom_by_group/'
        self.postRequest.POST['group_by'] = AE.atom_execute
        response = query_atom_by_group(self.postRequest)
        response_dict = json.loads(response.content)
        if response_dict["data"]["total"] == 0:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_NO_DATA_PARAMS), None)
        else:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_ATOM_EXECUTE_PARAMS), None)

    def test_atom_group_by_instance(self):
        """
        标准插件任务详情
        :return:
        """
        self.postRequest.path = '/analysis/query_atom_by_group/'
        self.postRequest.POST['group_by'] = AE.atom_instance
        response = query_atom_by_group(self.postRequest)
        response_dict = json.loads(response.content)
        if response_dict["data"]["total"] == 0:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_NO_DATA_PARAMS), None)
        else:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_ATOM_INSTANCE_PARAMS), None)

    def test_atom_group_by_template(self):
        """
        标准插件流程详情
        :return:
        """
        self.postRequest.path = '/analysis/query_atom_by_group/'
        self.postRequest.POST['group_by'] = AE.atom_template
        response = query_atom_by_group(self.postRequest)
        response_dict = json.loads(response.content)
        if response_dict["data"]["total"] == 0:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_NO_DATA_PARAMS), None)
        else:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_ATOM_TEMPLATE_PARAMS), None)

    def test_atom_group_by_cite(self):
        """
        标准插件引用次数
        :return:
        """
        self.postRequest.path = '/analysis/query_atom_by_group/'
        self.postRequest.POST['group_by'] = AE.atom_cite
        response = query_atom_by_group(self.postRequest)
        response_dict = json.loads(response.content)
        if response_dict["data"]["total"] == 0:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_NO_DATA_PARAMS), None)
        else:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_CATEGORY_AND_BUSINESS_PARAMS), None)

    def test_task_category(self):
        """
        分组内容
        :return:
        """
        self.getRequest.path = '/analysis/get_task_category/'
        response = get_task_category(self.getRequest)
        response_dict = json.loads(response.content)
        if len(response_dict["data"]) == 0:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_TASK_CATEGORY_NO_DATA_PARAMS), None)
        else:
            self.assertEqual(jsonschema.validate(response_dict, ANALYSIS_TASK_CATEGORY_PARAMS), None)
