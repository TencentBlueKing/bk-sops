# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from ..base import ComponentAPI


class CollectionsJOBV3(object):
    """Collections of JOBV3 APIS"""

    def __init__(self, client):
        self.client = client

        self.execute_job_plan = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/jobv3/execute_job_plan/",
            description="启动作业执行方案",
        )
        self.fast_execute_script = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/jobv3/fast_execute_script/",
            description="快速执行脚本",
        )
        self.fast_execute_sql = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/jobv3/fast_execute_sql/",
            description="快速执行SQL脚本",
        )
        self.fast_transfer_file = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/jobv3/fast_transfer_file/",
            description="快速分发文件",
        )
        self.get_account_list = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/jobv3/get_account_list/",
            description="查询业务下用户有权限的执行账号列表",
        )
        self.get_cron_detail = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/jobv3/get_cron_detail/",
            description="查询定时作业详情",
        )
        self.get_cron_list = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/jobv3/get_cron_list/",
            description="查询业务下定时作业信息",
        )
        self.get_job_instance_global_var_value = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/jobv3/get_job_instance_global_var_value/",
            description="获取作业实例全局变量的值",
        )
        self.get_job_instance_ip_log = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/jobv3/get_job_instance_ip_log/",
            description="根据ip查询作业执行日志",
        )
        self.get_job_instance_list = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/jobv3/get_job_instance_list/",
            description="查询作业实例列表（执行历史)",
        )
        self.get_job_instance_status = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/jobv3/get_job_instance_status/",
            description="根据作业实例 ID 查询作业执行状态",
        )
        self.get_job_plan_detail = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/jobv3/get_job_plan_detail/",
            description="根据作业执行方案 ID 查询作业执行方案详情",
        )
        self.get_job_plan_list = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/jobv3/get_job_plan_list/",
            description="查询执行方案列表",
        )
        self.get_job_template_list = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/jobv3/get_job_template_list/",
            description="查询作业模版列表",
        )
        self.get_public_script_list = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/jobv3/get_public_script_list/",
            description="查询公共脚本列表",
        )
        self.get_public_script_version_detail = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/jobv3/get_public_script_version_detail/",
            description="查询公共脚本版本详情",
        )
        self.get_public_script_version_list = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/jobv3/get_public_script_version_list/",
            description="查询公共脚本版本列表",
        )
        self.get_script_list = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/jobv3/get_script_list/",
            description="查询业务脚本列表",
        )
        self.get_script_version_detail = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/jobv3/get_script_version_detail/",
            description="查询业务脚本版本详情",
        )
        self.get_script_version_list = ComponentAPI(
            client=self.client,
            method="GET",
            path="/api/c/compapi{bk_api_ver}/jobv3/get_script_version_list/",
            description="查询业务脚本版本列表",
        )
        self.operate_job_instance = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/jobv3/operate_job_instance/",
            description="用于对执行的作业实例进行操作，例如终止作业。",
        )
        self.operate_step_instance = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/jobv3/operate_step_instance/",
            description="用于对执行的实例的步骤进行操作，例如重试，忽略错误等。",
        )
        self.save_cron = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/jobv3/save_cron/",
            description="新建或保存定时作业；新建定时作业，定时任务状态默认为暂停。",
        )
        self.update_cron_status = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/job/update_cron_status/",
            description="更新定时作业状态，如启动或暂停",
        )
        self.create_credential = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/jobv3/create_credential/",
            description="新建凭证",
        )
        self.create_file_source = ComponentAPI(
            client=self.client,
            method="POST",
            path="/api/c/compapi{bk_api_ver}/jobv3/create_file_source/",
            description="新建文件源",
        )
