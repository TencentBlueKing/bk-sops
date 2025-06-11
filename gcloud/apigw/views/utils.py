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

import logging
import traceback

from gcloud.tasktmpl3.domains import varschema
from gcloud.utils.dates import format_datetime

logger = logging.getLogger("root")  # noqa


def info_data_from_period_task(task, detail=True, tz=None):
    info = {
        "id": task.id,
        "name": task.name,
        "template_id": task.template_id,
        "template_source": task.template_source,
        "creator": task.creator,
        "cron": task.cron,
        "enabled": task.enabled,
        "last_run_at": format_datetime(task.last_run_at, tz),
        "total_run_count": task.total_run_count,
    }

    if detail:
        info["form"] = task.form
        info["pipeline_tree"] = task.pipeline_tree

    return info


def format_template_data(template, project=None, tz=None):
    pipeline_tree = template.pipeline_tree
    pipeline_tree.pop("line")
    pipeline_tree.pop("location")
    varschema.add_schema_for_input_vars(pipeline_tree)

    data = {
        "id": template.id,
        "name": template.pipeline_template.name,
        "creator": template.pipeline_template.creator,
        "create_time": format_datetime(template.pipeline_template.create_time, tz),
        "editor": template.pipeline_template.editor,
        "edit_time": format_datetime(template.pipeline_template.edit_time, tz),
        "category": template.category,
        "pipeline_tree": pipeline_tree,
    }
    if project:
        data.update(
            {
                "project_id": project.id,
                "project_name": project.name,
                "bk_biz_id": project.bk_biz_id,
                "bk_biz_name": project.name if project.from_cmdb else None,
            }
        )

    return data


def format_template_list_data(templates, project=None, return_id_list=False, tz=None):
    data = []
    ids = []
    for tmpl in templates:
        item = {
            "id": tmpl.id,
            "name": tmpl.pipeline_template.name,
            "creator": tmpl.pipeline_template.creator,
            "create_time": format_datetime(tmpl.pipeline_template.create_time, tz),
            "editor": tmpl.pipeline_template.editor,
            "edit_time": format_datetime(tmpl.pipeline_template.edit_time, tz),
            "category": tmpl.category,
        }

        if project:
            item.update(
                {
                    "project_id": project.id,
                    "project_name": project.name,
                    "bk_biz_id": project.bk_biz_id,
                    "bk_biz_name": project.name if project.from_cmdb else None,
                    "executor_proxy": tmpl.executor_proxy,
                }
            )

        if return_id_list:
            ids.append(item["id"])

        data.append(item)
    if not return_id_list:
        return data
    return data, ids


def format_task_info_data(task, project=None, tz=None):
    instance_start_time = task.pipeline_instance.start_time
    instance_finish_time = task.pipeline_instance.finish_time
    item = {
        "id": task.id,
        "name": task.pipeline_instance.name,
        "category": task.category_name,
        "create_method": task.create_method,
        "creator": task.pipeline_instance.creator,
        "executor": task.pipeline_instance.executor,
        "start_time": format_datetime(instance_start_time, tz) if tz else instance_start_time,
        "finish_time": format_datetime(instance_finish_time, tz) if tz else instance_finish_time,
        "is_started": task.pipeline_instance.is_started,
        "is_finished": task.pipeline_instance.is_finished,
        "template_source": task.template_source,
        "template_id": task.template_id,
        "is_child_taskflow": task.is_child_taskflow,
    }
    if project:
        item.update(
            {
                "project_id": project.id,
                "project_name": project.name,
                "bk_biz_id": project.bk_biz_id,
                "bk_biz_name": project.name if project.from_cmdb else None,
            }
        )
    return item


def format_task_list_data(tasks, project=None, return_id_list=False, tz=None):
    data = []
    ids = []
    for task in tasks:
        item = format_task_info_data(task, project, tz)
        data.append(item)
        if return_id_list:
            ids.append(item["id"])
    if not return_id_list:
        return data
    return data, ids


def format_function_task_list_data(function_tasks, project=None, tz=None):
    data = []
    for function_task in function_tasks:
        task_create_time = function_task.create_time
        task_claim_time = function_task.claim_time
        task_reject_time = function_task.reject_time
        task_transfer_time = function_task.transfer_time
        item = {
            "id": function_task.id,
            "name": function_task.task.name,
            "creator": function_task.creator,
            "rejecter": function_task.rejecter,
            "claimant": function_task.claimant,
            "predecessor": function_task.predecessor,
            "create_time": format_datetime(task_create_time, tz) if tz else task_create_time,
            "claim_time": format_datetime(task_claim_time, tz) if tz else task_claim_time,
            "reject_time": format_datetime(task_reject_time, tz) if tz else task_reject_time,
            "transfer_time": format_datetime(task_transfer_time, tz) if tz else task_transfer_time,
            "status": function_task.status,
        }
        task_item = format_task_info_data(function_task.task, project=project, tz=tz)
        item["task"] = task_item
        data.append(item)
    return data


def paginate_list_data(request, queryset, without_count: bool = False):
    """
    @summary: 读取request中的offset和limit参数，对筛选出的queryset进行分页
    @return: 分页结果列表, 分页前数据总数
    """
    try:
        offset = int(request.GET.get("offset", 0))
        limit = int(request.GET.get("limit", 100))
        # limit 最大数量为200
        limit = 200 if limit > 200 else limit
        count = -1 if without_count else queryset.count()

        if offset < 0 or limit < 0:
            raise Exception("offset and limit must be greater or equal to 0.")
        else:
            results = queryset[offset : offset + limit]
        return results, count
    except Exception as e:
        message = "[API] pagination error: {}".format(e)
        logger.error(message + "\n traceback: {}".format(traceback.format_exc()))
        raise Exception(message)
