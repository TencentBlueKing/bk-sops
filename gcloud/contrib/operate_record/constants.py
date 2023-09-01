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
from enum import Enum

from django.utils.translation import ugettext_lazy as _


class OperateType(Enum):
    none = "None"
    create = _("创建")
    task_clone = _("克隆(创建)")
    start = _("执行")
    pause = _("暂停")
    resume = _("继续")
    revoke = _("撤消")
    delete = _("删除")
    update = _("修改")

    # 任务节点操作
    callback = _("回调")
    retry = _("重试")
    skip = _("跳过")
    skip_exg = _("跳过失败网关")
    skip_cpg = _("跳过并行条件网关")
    pause_subproc = _("暂停节点")
    resume_subproc = _("继续节点")
    forced_fail = _("强制失败")
    spec_nodes_timer_reset = _("调整时间")

    task_action = _("任务操作")
    nodes_action = _("节点操作")


class OperateSource(Enum):
    """任务记录来源"""

    app = _("app 页面")
    api = _("api 接口")
    parent = _("父任务")

    # 模版来源
    project = _("项目流程")
    common = _("公共流程")
    onetime = _("一次性任务")


class RecordType(Enum):
    """记录类型"""

    task = _("任务实例")
    template = _("项目模版")
    common_template = _("公共模版")
    task_node = _("任务节点")


TEMPLATE_TYPE = [RecordType.template.name, RecordType.common_template.name]

# 转为model可用的选项
OPERATE_TYPE = [(_type.name, _type.value) for _type in OperateType]
OPERATE_SOURCE = [(_source.name, _source.value) for _source in OperateSource]
INSTANCE_OBJECT_KEY = ["new_instance_id", "instance_id", "task_id"]
