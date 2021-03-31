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

from typing import Optional


class HooksMixin:
    def pre_prepare_run_pipeline(self, pipeline: dict, root_pipeline_data: dict, **options):
        """
        调用 pre_prepare_run_pipeline 前执行的钩子

        :param pipeline: 流程描述对象
        :type pipeline: dict
        :param root_pipeline_data 根流程数据
        :type root_pipeline_data dict
        """

    def post_prepare_run_pipeline(self, pipeline: dict, root_pipeline_data: dict, **options):
        """
        调用 pre_prepare_run_pipeline 后执行的钩子

        :param pipeline: 流程描述对象
        :type pipeline: dict
        :param root_pipeline_data 根流程数据
        :type root_pipeline_data dict
        """

    def pre_pause_pipeline(self, pipeline_id: str):
        """
        暂停 pipeline 前执行的钩子

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        """

    def post_pause_pipeline(self, pipeline_id: str):
        """
        暂停 pipeline 后执行的钩子

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        """

    def pre_revoke_pipeline(self, pipeline_id: str):
        """
        撤销 pipeline 前执行的钩子

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        """

    def post_revoke_pipeline(self, pipeline_id: str):
        """
        撤销 pipeline 后执行的钩子

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        """

    def pre_resume_pipeline(self, pipeline_id: str):
        """
        继续 pipeline 前执行的钩子

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        """

    def post_resume_pipeline(self, pipeline_id: str):
        """
        继续 pipeline 后执行的钩子

        :param pipeline_id: 流程 ID
        :type pipeline_id: str
        """

    def pre_resume_node(self, node_id: str):
        """
        继续节点后执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        """

    def post_resume_node(self, node_id: str):
        """
        继续节点后执行的钩子

        :param node_id: [description]节点 ID
        :type node_id: str
        """

    def pre_pause_node(self, node_id: str):
        """
        暂停节点前执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        """

    def post_pause_node(self, node_id: str):
        """
        暂停节点后执行的钩子

        :param node_id: [description]节点 ID
        :type node_id: str
        """

    def pre_retry_node(self, node_id: str, data: Optional[dict]):
        """
        重试节点前执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        :param data: 重试时使用的节点执行输入
        :type data: Optional[dict]
        """

    def post_retry_node(self, node_id: str, data: Optional[dict]):
        """
        重试节点后执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        :param data: 重试时使用的节点执行输入
        :type data: Optional[dict]
        """

    def pre_skip_node(self, node_id: str):
        """
        跳过节点前执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        """

    def post_skip_node(self, node_id: str):
        """
        跳过节点后执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        """

    def pre_skip_exclusive_gateway(self, node_id: str, flow_id: str):
        """
        跳过分支网关前执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        :param flow_id: 跳过后选择的目标流 ID
        :type flow_id: str
        """

    def post_skip_exclusive_gateway(self, node_id: str, flow_id: str):
        """
        跳过分支网关后执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        :param flow_id: 跳过后选择的目标流 ID
        :type flow_id: str
        """

    def pre_forced_fail_activity(self, node_id: str, ex_data: str):
        """
        强制失败节点前执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        :param ex_data: 写入节点执行数据的失败信息
        :type ex_data: str
        """

    def post_forced_fail_activity(self, node_id: str, ex_data: str):
        """
        强制失败节点后执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        :param ex_data: 写入节点执行数据的失败信息
        :type ex_data: str
        """

    def pre_callback(self, node_id: str, version: str, data: str):
        """
        回调节点前执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        :param version: 节点执行版本
        :type version: str
        :param data: 回调数据
        :type data: str
        """

    def post_callback(self, node_id: str, version: str, data: str):
        """
        回调节点后执行的钩子

        :param node_id: 节点 ID
        :type node_id: str
        :param version: 节点执行版本
        :type version: str
        :param data: 回调数据
        :type data: str
        """
