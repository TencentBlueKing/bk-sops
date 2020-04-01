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

import logging

from gcloud.tasktmpl3 import varschema
from gcloud.core.utils import format_datetime

logger = logging.getLogger("root")  # noqa


def info_data_from_period_task(task, detail=True):
    info = {
        "id": task.id,
        "name": task.name,
        "template_id": task.template_id,
        "template_source": task.template_source,
        "creator": task.creator,
        "cron": task.cron,
        "enabled": task.enabled,
        "last_run_at": format_datetime(task.last_run_at),
        "total_run_count": task.total_run_count,
    }

    if detail:
        info["form"] = task.form
        info["pipeline_tree"] = task.pipeline_tree

    return info


def format_template_data(template, project=None):
    pipeline_tree = template.pipeline_tree
    varschema.add_schema_for_input_vars(pipeline_tree)

    data = {
        "id": template.id,
        "name": template.pipeline_template.name,
        "creator": template.pipeline_template.creator,
        "create_time": format_datetime(template.pipeline_template.create_time),
        "editor": template.pipeline_template.editor,
        "edit_time": format_datetime(template.pipeline_template.edit_time),
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


def format_template_list_data(templates, project=None):
    data = []
    for tmpl in templates:
        item = {
            "id": tmpl.id,
            "name": tmpl.pipeline_template.name,
            "creator": tmpl.pipeline_template.creator,
            "create_time": format_datetime(tmpl.pipeline_template.create_time),
            "editor": tmpl.pipeline_template.editor,
            "edit_time": format_datetime(tmpl.pipeline_template.edit_time),
            "category": tmpl.category,
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

        data.append(item)

    return data
