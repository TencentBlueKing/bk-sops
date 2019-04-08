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

from ..base import ComponentAPI


class CollectionsGSE(object):
    """Collections of GSE APIS"""

    def __init__(self, client):
        self.client = client

        self.get_agent_info = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/gse/get_agent_info/',
            description=u'Agent心跳信息查询'
        )
        self.get_agent_status = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/gse/get_agent_status/',
            description=u'Agent在线状态查询'
        )
        self.proc_create_session = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/gse/proc_create_session/',
            description=u'进程管理：新建 session'
        )
        self.proc_get_task_result_by_id = ComponentAPI(
            client=self.client, method='GET',
            path='/api/c/compapi{bk_api_ver}/gse/proc_get_task_result_by_id/',
            description=u'进程管理：获取任务结果'
        )
        self.proc_run_command = ComponentAPI(
            client=self.client, method='POST',
            path='/api/c/compapi{bk_api_ver}/gse/proc_run_command/',
            description=u'进程管理：执行命令'
        )
