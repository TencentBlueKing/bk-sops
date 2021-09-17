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
import datetime
import logging

from django.utils import translation, timezone
from django.utils.translation import ugettext_lazy as _

from engine_pickle_obj.context import SystemObject
from gcloud.core.models import Business, ProjectConfig, Project

logger = logging.getLogger("root")


class TaskContext(object):
    """
    @summary: 流程任务内置环境变量
    """

    prefix = "_system"

    def __init__(self, taskflow, username):
        # 执行任务的操作员
        operator = taskflow.executor or username
        self.language = translation.get_language()
        self.project_id = taskflow.project.id
        self.project_name = taskflow.project.name
        self.bk_biz_id = taskflow.project.bk_biz_id
        self.bk_biz_name = taskflow.project.name
        if taskflow.project.from_cmdb:
            self.biz_supplier_account = Business.objects.get(cc_id=taskflow.project.bk_biz_id).cc_owner
        else:
            self.biz_supplier_account = None
        self.operator = operator
        self.executor = self.task_executor(taskflow, operator)
        self.task_id = taskflow.id
        self.task_name = taskflow.pipeline_instance.name
        # 兼容V3.4.X版本之前的引用非标准命名的插件
        self.biz_cc_id = self.bk_biz_id
        self.biz_cc_name = self.bk_biz_name
        # 任务开始时间
        project = Project.objects.get(id=self.project_id)
        project_tz = timezone.pytz.timezone(project.time_zone)
        self.task_start_time = datetime.datetime.now(tz=project_tz).strftime("%Y-%m-%d %H:%M:%S")

    def task_executor(self, taskflow, operator):
        """获取该任务的实际执行人

        :param taskflow: 任务对象
        :type taskflow: TaskFlowInstance
        :param operator: 当前操作者
        :type operator: str
        :return: 该任务执行时实际使用的执行人
        :rtype: str
        """
        return taskflow.executor_proxy or ProjectConfig.objects.task_executor_for_project(self.project_id, operator)

    def context(self):
        return {"${%s}" % TaskContext.prefix: {"type": "plain", "is_param": True, "value": self}}

    @classmethod
    def to_flat_key(cls, key):
        return "${%s.%s}" % (cls.prefix, key)

    @classmethod
    def flat_details(cls):
        # index: 展示在前端全局变量的顺序，越小越靠前
        details = {
            cls.to_flat_key("task_start_time"): {
                "key": cls.to_flat_key("task_start_time"),
                "name": _("任务开始时间"),
                "index": -8,
                "desc": "",
            },
            cls.to_flat_key("language"): {
                "key": cls.to_flat_key("language"),
                "name": _("执行环境语言CODE"),
                "index": -7,
                "desc": _("中文对应 zh-hans，英文对应 en"),
            },
            cls.to_flat_key("bk_biz_id"): {
                "key": cls.to_flat_key("bk_biz_id"),
                "name": _("任务所属的CMDB业务ID"),
                "index": -6,
                "desc": "",
            },
            cls.to_flat_key("bk_biz_name"): {
                "key": cls.to_flat_key("bk_biz_name"),
                "name": _("任务所属的CMDB业务名称"),
                "index": -5,
                "desc": "",
            },
            cls.to_flat_key("operator"): {
                "key": cls.to_flat_key("operator"),
                "name": _("任务的操作员（点击开始执行的人员）"),
                "index": -4,
                "desc": "",
            },
            cls.to_flat_key("executor"): {
                "key": cls.to_flat_key("executor"),
                "name": _("任务的执行者（调用API网关接口的人员）"),
                "index": -3,
                "desc": "",
            },
            cls.to_flat_key("task_id"): {"key": cls.to_flat_key("task_id"), "index": -2, "name": _("任务ID"), "desc": ""},
            cls.to_flat_key("task_name"): {
                "key": cls.to_flat_key("task_name"),
                "name": _("任务名称"),
                "index": -1,
                "desc": "",
            },
        }
        for item in list(details.values()):
            item.update(
                {
                    "show_type": "hide",
                    "source_type": "system",
                    "source_tag": "",
                    "source_info": {},
                    "custom_type": "",
                    "value": "",
                    "hook": False,
                    "validation": "",
                }
            )
        return details


def root_pipeline_context_provider(root_pipeline_data: dict):
    return {"${_system}": SystemObject(root_pipeline_data)}


def subprocess_context_provider(root_pipeline_data: dict):
    return {"${_system}": SystemObject(root_pipeline_data)}
