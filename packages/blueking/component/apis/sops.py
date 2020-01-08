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

from ..base import ComponentAPI


class CollectionsSOPS(object):
    """Collections of SOPS APIS"""

    def __init__(self, client):
        self.client = client

        self.create_task = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/sops/create_task/',
            description=u'创建任务'
        )
        self.get_task_status = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/sops/get_task_status/',
            description=u'查询任务或节点状态'
        )
        self.get_template_info = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/sops/get_template_info/',
            description=u'查询单个模板详情'
        )
        self.get_template_list = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/sops/get_template_list/',
            description=u'查询模板列表'
        )
        self.operate_task = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/sops/operate_task/',
            description=u'操作任务'
        )
        self.query_task_count = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/sops/query_task_count/',
            description=u'查询任务分类统计'
        )
        self.start_task = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/sops/start_task/',
            description=u'开始任务'
        )
