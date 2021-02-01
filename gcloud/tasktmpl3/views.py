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
import logging

from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import permissions, viewsets
from rest_framework.exceptions import ErrorDetail
from pipeline.models import TemplateScheme

from gcloud import err_code
from gcloud.core.apis.drf.viewsets.utils import ApiMixin
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tasktmpl3.serializers import TemplateSchemeSerializer

logger = logging.getLogger("root")


class TemplateSchemeViewSet(ApiMixin, viewsets.ModelViewSet):
    queryset = TemplateScheme.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TemplateSchemeSerializer

    @action(methods=["post"], detail=False)
    def batch_operate(self, request, *args, **kwargs):
        current_schemes = request.data.get("schemes", {})
        template_id = request.data.get("template_id")
        project_id = request.data.get("project_id")

        if not template_id or not current_schemes:
            return Response(
                data={"detail": ErrorDetail("template_id or schemes is empty", err_code.REQUEST_PARAM_INVALID.code)},
                exception=True,
            )

        # 获取template 对象
        try:
            template = TaskTemplate.objects.get(pk=template_id, project_id=project_id)
        except TaskTemplate.DoesNotExist:
            message = "flow template[id={template_id}] in project[id={project_id}] does not exist".format(
                template_id=template_id, project_id=project_id
            )
            logger.error(message)
            return Response(data={"detail": ErrorDetail(message, err_code.UNKNOWN_ERROR.code)}, exception=True)

        pipeline_template_id = template.pipeline_template.id
        old_schemes_id_set = set(TemplateScheme.objects.filter(template__id=53).values_list("id", flat=True))
        need_create_schemes, scheme_id_list = [], []
        # 筛选待处理方案
        for scheme in current_schemes:
            scheme_id = scheme.get("id")
            scheme_id_list.append(scheme_id)
            if not scheme_id:
                scheme.update(
                    {
                        "unique_id": "{}-{}".format(template_id, scheme["name"]),
                        "template_id": pipeline_template_id,
                    }
                )
                need_create_schemes.append(TemplateScheme(**scheme))

        scheme_id_list_set = set(scheme_id_list)
        need_delete_schemes_id = old_schemes_id_set.difference(scheme_id_list_set)

        # 批量创建scheme
        TemplateScheme.objects.bulk_create(need_create_schemes)

        # 批量删除scheme
        TemplateScheme.objects.filter(id__in=list(need_delete_schemes_id)).delete()

        # 获取指定流程所有方案
        all_schemes_query = TemplateScheme.objects.filter(template_id=pipeline_template_id)

        serializer = self.get_serializer(all_schemes_query, many=True)

        return Response(serializer.data)
