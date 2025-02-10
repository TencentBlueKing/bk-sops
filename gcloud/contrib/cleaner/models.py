# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from gcloud.constants import TASK_CREATE_METHOD, TEMPLATE_SOURCE, PROJECT

from gcloud.core.models import EngineConfig


class ArchivedTaskInstance(models.Model):
    id = models.BigAutoField(_("id"), primary_key=True)
    task_id = models.BigIntegerField(_("任务 ID"), help_text="过期任务 ID")
    project_id = models.BigIntegerField(_("项目 ID"), default=-1, help_text="模板所属项目ID")
    name = models.CharField(_("实例名称"), max_length=128, default="default_instance")
    template_id = models.CharField(_("Pipeline模板ID"), max_length=32, null=True, blank=True)
    task_template_id = models.CharField(_("Task模板ID"), max_length=32, null=True, blank=True)
    template_source = models.CharField(_("流程模板来源"), max_length=32, choices=TEMPLATE_SOURCE, default=PROJECT)
    create_method = models.CharField(_("创建方式"), max_length=30, choices=TASK_CREATE_METHOD, default="app")
    create_info = models.CharField(_("创建任务额外信息（App maker ID或APP CODE或周期任务ID）"), max_length=255, null=True, blank=True)
    creator = models.CharField(_("创建者"), max_length=32, null=True, blank=True)
    create_time = models.DateTimeField(_("任务创建时间"), db_index=True)
    archived_time = models.DateTimeField(_("任务归档时间"), db_index=True, auto_now_add=True)
    executor = models.CharField(_("执行者"), max_length=32, blank=True, null=True)
    recorded_executor_proxy = models.CharField(_("任务执行人代理"), max_length=255, default=None, blank=True, null=True)
    start_time = models.DateTimeField(_("启动时间"), null=True, blank=True)
    finish_time = models.DateTimeField(_("结束时间"), null=True, blank=True)
    is_started = models.BooleanField(_("是否已经启动"), default=False)
    is_finished = models.BooleanField(_("是否已经完成"), default=False)
    is_revoked = models.BooleanField(_("是否已经撤销"), default=False)
    is_deleted = models.BooleanField(_("是否删除"), default=False)
    current_flow = models.CharField(_("当前任务流程阶段"), max_length=255, null=True, blank=True)
    engine_ver = models.IntegerField(_("引擎版本"), choices=EngineConfig.ENGINE_VER, default=2)
    is_child_taskflow = models.BooleanField(_("是否为子任务"), default=False)
    snapshot_id = models.CharField(_("实例结构数据，指向实例对应的模板的结构数据"), blank=True, null=True, max_length=32)
    extra_info = models.TextField(_("额外信息"), blank=True, null=True)

    class Meta:
        verbose_name = _("归档任务实例")
        verbose_name_plural = _("归档任务实例")
        index_together = ("project_id", "task_template_id")
