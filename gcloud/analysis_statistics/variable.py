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

from django.db import transaction

from gcloud.tasktmpl3.domains.constants import analysis_pipeline_constants_ref
from gcloud.analysis_statistics.models import TemplateVariableStatistics


def _constants_refs_count(refs: dict) -> int:
    count = 0
    for _, referencer in refs.items():
        count += len(referencer)
    return count


def update_statistics(project_id: int, template_id: int, pipeline_tree: dict):

    constants_refs = analysis_pipeline_constants_ref(pipeline_tree=pipeline_tree)

    variable_statistic = []

    for key, const in pipeline_tree.get("constants", {}).items():
        variable_statistic.append(
            TemplateVariableStatistics(
                project_id=project_id,
                template_id=template_id,
                variable_key=key,
                variable_type=const["source_tag"],
                variable_source=const["source_type"],
                refs=_constants_refs_count(constants_refs.get(key, {})),
            )
        )
    with transaction.atomic():
        TemplateVariableStatistics.objects.filter(template_id=template_id, project_id=project_id).delete()
        TemplateVariableStatistics.objects.bulk_create(variable_statistic, batch_size=100)
