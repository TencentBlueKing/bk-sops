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


class CollectionsNodeMan(object):
    """Collections of JOB APIS"""

    def __init__(self, client):
        self.client = client

        self.create_task = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi/v2/nodeman/create_task/',
            description='安装作业'
        )

        self.get_task_info = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi/v2/nodeman/get_task_info/',
            description='获取任务信息'
        )

        self.get_log = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi/v2/nodeman/get_log/',
            description='获取任务执行日志'
        )
        #  nodeman v2.0
        self.job_install = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/nodeman/api/job/install/',
            description='新安装Agent、新安装Proxy、重装、替换等操作'
        )

        self.job_operate = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/nodeman/api/job/operate/',
            description='用于只有bk_host_id参数的主机下线、重启等操作'
        )

        self.remove_host = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/nodeman/api/host/remove_host/',
            description='移除主机'
        )

        self.ap_list = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/nodeman/api/ap/',
            description='查询接入点列表'
        )

        self.get_job_log = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/nodeman/api/job/log/',
            description='查询单个主机操作日志'
        )

        self.job_details = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/nodeman/api/job/details/',
            description='查询任务执行状态'
        )

        self.search = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/nodeman/api/plugin/search/',
            description='查询主机'
        )

        self.get_cloud = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/nodeman/api/cloud/',
            description='查询去区域'
        )
