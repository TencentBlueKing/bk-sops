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
from itertools import chain
from django.db import transaction

from gcloud.tasktmpl3.domains.constants import analysis_pipeline_constants_ref
from gcloud.analysis_statistics.models import TemplateVariableStatistics


def update_statistics(project_id: int, template_id: int, pipeline_tree: dict) -> set:

    constants_refs = analysis_pipeline_constants_ref(pipeline_tree=pipeline_tree)
    constants = pipeline_tree.get("constants", {})

    variable_statistic = []
    custom_constants_types = set({})
    collected_keys = set({})

    # collect referenced key
    for key, refs in constants_refs.items():
        const = constants.get(key)
        if const:
            variable_type, variable_source = const["source_tag"], const["source_type"]
        elif key.startswith("${_env_"):
            variable_type, variable_source = "", "project"
        else:
            continue

        variable_statistic.append(
            TemplateVariableStatistics(
                project_id=project_id,
                template_id=template_id,
                variable_key=key,
                variable_type=variable_type,
                variable_source=variable_source,
                refs=len(list(chain(*refs.values()))),
            )
        )
        collected_keys.add(key)

    # collect not referenced key and custom constants types
    for key, const in constants.items():
        if const["source_type"] == "custom":
            custom_constants_types.add(const["source_tag"])

        if key not in collected_keys:
            variable_statistic.append(
                TemplateVariableStatistics(
                    project_id=project_id,
                    template_id=template_id,
                    variable_key=key,
                    variable_type=const["source_tag"],
                    variable_source=const["source_type"],
                    refs=0,
                )
            )

    with transaction.atomic():
        TemplateVariableStatistics.objects.filter(template_id=template_id, project_id=project_id).delete()
        TemplateVariableStatistics.objects.bulk_create(variable_statistic, batch_size=100)

    return custom_constants_types
