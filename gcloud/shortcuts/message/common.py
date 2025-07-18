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

from django.utils.translation import gettext as _

from gcloud.core.models import Project


def title_and_content_for_atom_failed(taskflow, pipeline_inst, node_name, executor):
    title = _("【标准运维APP通知】执行失败")
    base_content = _(
        "您在【{cc_name}】业务中的任务【{task_name}】执行失败，当前失败节点是【{node_name}】，"
        "操作员是【{executor}】，请前往标准运维APP{url}查看详情！"
    ).format(
        cc_name=taskflow.project.name, task_name=pipeline_inst.name, node_name=node_name, executor=executor, url="{url}"
    )
    content = base_content.format(url="( {} )".format(taskflow.url))
    email_content = base_content.format(url="<a href={}>( {} )</a>".format(taskflow.url, taskflow.url))
    return title, content, email_content


def title_and_content_for_flow_finished(taskflow, pipeline_inst, node_name, executor):
    title = _("【标准运维APP通知】执行完成")
    base_content = _(
        "您在【{cc_name}】业务中的任务【{task_name}】执行成功，操作员是【{executor}】，"
        "请前往标准运维APP{url}查看详情！"
    ).format(
        cc_name=taskflow.project.name,
        task_name=pipeline_inst.name,
        executor=executor,
        url="{url}",
    )

    content = base_content.format(url="( {} )".format(taskflow.url))
    email_content = base_content.format(url="<a href={}>( {} )</a>".format(taskflow.url, taskflow.url))
    return title, content, email_content


def title_and_content_for_pending_processing(taskflow, pipeline_inst, node_name, executor):
    title = _("【标准运维APP通知】等待处理")
    base_content = _(
        "您在【{cc_name}】业务中的任务【{task_name}】等待处理中，操作员是【{executor}】，"
        "请前往标准运维APP{url}查看详情！"
    ).format(
        cc_name=taskflow.project.name,
        task_name=pipeline_inst.name,
        executor=executor,
        url="{url}",
    )

    content = base_content.format(url="( {} )".format(taskflow.url))
    email_content = base_content.format(url="<a href={}>( {} )</a>".format(taskflow.url, taskflow.url))
    return title, content, email_content


def title_and_content_for_periodic_task_start_fail(periodic_task, history):
    title = _("【标准运维APP通知】周期任务启动失败")
    content = _(
        "您在【{cc_name}】业务中计划于【{start_time}】执行的周期任务【{task_name}】启动失败，" "错误信息：【{ex_data}】"
    ).format(
        cc_name=periodic_task.project.name,
        start_time=history.start_at,
        task_name=periodic_task.name,
        ex_data=history.ex_data,
    )
    return title, content


def title_and_content_for_clocked_task_create_fail(clocked_task, ex_data):
    try:
        proj = Project.objects.get(id=clocked_task.project_id)
        cc_name = proj.name
    except Exception:
        cc_name = clocked_task.project_id
    title = _("【标准运维APP通知】计划任务创建失败")
    content = _(
        "您在【{cc_name}】业务中的计划任务【{task_name}】于{plan_start_time}创建失败，" "错误信息：【{ex_data}】"
    ).format(
        cc_name=cc_name, task_name=clocked_task.task_name, plan_start_time=clocked_task.plan_start_time, ex_data=ex_data
    )
    return title, content
