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
specific lan
"""

import json
import typing
from datetime import datetime, timezone

from pipeline.models import PipelineTemplate

from gcloud.clocked_task.models import ClockedTask
from gcloud.conf import settings
from gcloud.constants import PROJECT
from gcloud.contrib.appmaker.models import AppMaker
from pipeline_web.wrapper import PipelineTemplateWebWrapper


def import_clocked_tasks(
    project_id: int, clocked_tasks: typing.List[typing.Dict[str, typing.Any]], id_map: typing.Dict[str, typing.Any]
) -> typing.Dict[int, typing.Dict[str, typing.Any]]:
    """
    导入计划任务
    :param project_id:
    :param clocked_tasks: 导出的计划任务数据
    :param id_map:
    :return:
    """

    old_id__new_clocked_task_info_map: typing.Dict[int, typing.Dict[str, typing.Any]] = {}
    new_temp_id__pipeline_obj_map: typing.Dict[str, PipelineTemplate] = {
        obj.template_id: obj
        for obj in PipelineTemplate.objects.filter(
            template_id__in=id_map[PipelineTemplateWebWrapper.ID_MAP_KEY].values()
        )
    }

    for clocked_task in clocked_tasks:

        # replace project id
        clocked_task["project_id"] = project_id

        # replace template_id & template_name
        old_tid: int = clocked_task["template_id"]
        template_recreated_info: typing.Dict[str, typing.Any] = id_map["template_recreated_info"][
            clocked_task["template_source"]
        ][str(old_tid)]
        new_tid: int = template_recreated_info["id"]
        new_pipeline_template_id: str = template_recreated_info["import_data"]["pipeline_template_id"]
        clocked_task["template_id"] = new_tid
        clocked_task["template_name"] = new_temp_id__pipeline_obj_map[new_pipeline_template_id].name

        # transfer plan_start_time
        dt: datetime = datetime.strptime(clocked_task["plan_start_time"], "%Y-%m-%d %H:%M:%S %Z")
        clocked_task["plan_start_time"] = dt.replace(tzinfo=timezone.utc)

        # replace task_params template_schemes_id
        clocked_task["task_params"]["template_schemes_id"] = [
            id_map["scheme_id_old_to_new"].get(old_scheme_id, old_scheme_id)
            for old_scheme_id in clocked_task["task_params"]["template_schemes_id"]
        ]

        # transfer task_params to json string
        clocked_task["task_params"] = json.dumps(clocked_task["task_params"])

        # remove increase id
        old_clocked_task_id: int = clocked_task.pop("id", None)

        # import
        new_clocked_task_obj: ClockedTask = ClockedTask.objects.create_task(**clocked_task)
        old_id__new_clocked_task_info_map[old_clocked_task_id] = {"id": new_clocked_task_obj.id}

    return old_id__new_clocked_task_info_map


def import_app_makers(
    app_makers: typing.List[typing.Dict[str, typing.Any]], id_map: typing.Dict[str, typing.Any]
) -> typing.Dict[int, typing.Dict[str, typing.Any]]:
    """
    导入轻应用
    :param app_makers: 导出的轻应用任务数据
    :param id_map:
    :return:
    """

    old_id__new_app_maker_info_map: typing.Dict[int, typing.Dict[str, typing.Any]] = {}
    for app_maker in app_makers:
        # 1. replace template_id
        old_tid = app_maker["template_id"]
        # 轻应用仅引用项目流程
        template_recreated_info = id_map["template_recreated_info"][PROJECT][str(old_tid)]
        app_maker["template_id"] = template_recreated_info["id"]

        # 2. replace template_scheme_id
        old_scheme_id = app_maker["template_scheme_id"]
        app_maker["template_scheme_id"] = id_map["scheme_id_old_to_new"].get(old_scheme_id)

        app_maker["logo_content"] = None
        old_id = app_maker.pop("id", None)

        if settings.IS_LOCAL:
            app_maker["link_prefix"] = "http://localhost/appmaker/"
            fake = True
        else:
            app_maker["link_prefix"] = "%sappmaker/" % settings.APP_HOST
            fake = False

        result, app_maker_obj_or_message = AppMaker.objects.save_app_maker(
            app_maker["project_id"], app_maker, fake=fake
        )

        if not result:
            print(app_maker_obj_or_message)

        new_app_maker_obj: AppMaker = app_maker_obj_or_message
        old_id__new_app_maker_info_map[old_id] = {"id": new_app_maker_obj.id}

    return old_id__new_app_maker_info_map
