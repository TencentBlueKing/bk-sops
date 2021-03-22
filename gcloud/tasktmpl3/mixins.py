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

from django.db import connection
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

from blueapps.utils.managermixins import ClassificationCountMixin
from pipeline.component_framework.models import ComponentModel
from pipeline.contrib.statistics.models import ComponentInTemplate, TemplateInPipeline
from pipeline.contrib.periodic_task.models import PeriodicTask
from pipeline.models import PipelineInstance, TemplateRelationship

from gcloud.utils.dates import format_datetime, timestamp_to_datetime
from gcloud.core.constant import TASK_CATEGORY, AE

logger = logging.getLogger("root")


class TaskTmplStatisticsMixin(ClassificationCountMixin):
    def group_by_state(self, tasktmpl, *args):
        # 按流程模板执行状态查询流程个数
        total = tasktmpl.count()
        groups = [
            {
                "code": "CREATED",
                "name": _("未执行"),
                "value": tasktmpl.filter(pipeline_template__is_started=False).count(),
            },
            {
                "code": "EXECUTING",
                "name": _("执行中"),
                "value": tasktmpl.filter(
                    pipeline_template__is_started=True, pipeline_template__is_finished=False
                ).count(),
            },
            {
                "code": "FINISHED",
                "name": _("已完成"),
                "value": tasktmpl.filter(pipeline_template__is_finished=True).count(),
            },
        ]
        return total, groups

    def group_by_project_id(self, tasktmpl, *args):
        # 查询不同业务的模板个数
        total = tasktmpl.count()
        template_list = (
            tasktmpl.values(AE.project_id, AE.project__name).annotate(value=Count("project_id")).order_by("value")
        )
        groups = []
        for data in template_list:
            groups.append(
                {"code": data.get(AE.project_id), "name": data.get(AE.project__name), "value": data.get("value", 0)}
            )
        return total, groups

    def group_by_atom_cite(self, tasktmpl, *args):
        # 查询不同原子引用的个数
        statement = 'SELECT COUNT(*) ref, `component_code`, `version` \
        FROM statistics_componentintemplate AS S \
        INNER JOIN (SELECT `template_id` FROM `pipeline_pipelinetemplate` \
        WHERE `create_time` >= "{create_time}" AND `create_time` < "{finish_time}" AND `is_deleted` = FALSE) P \
        ON (`S`.`template_id` = `P`.`template_id`){filter_project} \
        GROUP BY `S`.`component_code`,`S`.`version` \
        ORDER BY ref DESC'.format(
            create_time=timestamp_to_datetime(args[0]["create_time"]),
            finish_time=timestamp_to_datetime(args[0]["finish_time"]),
            filter_project="INNER JOIN (SELECT `pipeline_template_id` FROM `tasktmpl3_tasktemplate` \
                  WHERE `project_id`={}) T \
                  ON (P.template_id = T.pipeline_template_id AND S.template_id=T.pipeline_template_id)".format(
                args[0]["project_id"]
            )
            if args[0]["project_id"]
            else "",
        )
        with connection.cursor() as cursor:
            cursor.execute(statement)
            return ComponentModel.objects.get_component_dicts(cursor.fetchall())

    def group_by_atom_template(self, tasktmpl, filters, page, limit):
        # 按起始时间、业务（可选）、类型（可选）、标准插件查询被引用的流程模板列表(dataTable)

        # 获得所有类型的dict列表
        category_dict = dict(TASK_CATEGORY)

        # 获取标准插件code
        component_code = filters.get("component_code")
        version = filters.get("version")
        # 获取到组件code对应的template_id_list
        if component_code:
            template_id_list = ComponentInTemplate.objects.filter(
                component_code=component_code, version=version
            ).values_list("template_id")
        else:
            template_id_list = ComponentInTemplate.objects.all().values_list("template_id")
        template_list = tasktmpl.filter(pipeline_template__template_id__in=template_id_list)
        total = template_list.count()
        order_by = filters.get("order_by", "-templateId")
        if order_by == "-templateId":
            template_list = template_list.order_by("-id")
        if order_by == "templateId":
            template_list = template_list.order_by("id")
        template_list = template_list.values(
            "id",
            "project_id",
            "project__name",
            "pipeline_template__name",
            "category",
            "pipeline_template__create_time",
            "pipeline_template__creator",
        )[(page - 1) * limit : page * limit]
        groups = []
        # 循环聚合信息
        for data in template_list:
            groups.append(
                {
                    "templateId": data.get("id"),
                    "projectId": data.get("project_id"),
                    "projectName": data.get("project__name"),
                    "templateName": data.get("pipeline_template__name"),
                    "category": category_dict[data.get("category")],  # 需要将code转为名称
                    "createTime": format_datetime(data.get("pipeline_template__create_time")),
                    "creator": data.get("pipeline_template__creator"),
                }
            )
        return total, groups

    def group_by_atom_execute(self, tasktmpl, filters, page, limit):
        # 需要获得符合的查询的对应 template_id 列表

        # 获得所有类型的dict列表
        category_dict = dict(TASK_CATEGORY)

        # 获取标准插件code
        component_code = filters.get("component_code")
        # 获取到组件code对应的template_id
        template_id_list = list(
            ComponentInTemplate.objects.filter(component_code=component_code).values_list("template_id", flat=True)
        )
        total = len(template_id_list)
        template_list = tasktmpl.filter(pipeline_template__template_id__in=template_id_list).values(
            "id",
            "project__name",
            "project_id",
            "pipeline_template__name",
            "category",
            "pipeline_template__edit_time",
            "pipeline_template__editor",
        )[(page - 1) * limit : page * limit]
        groups = []
        # 循环聚合信息
        for data in template_list:
            groups.append(
                {
                    "templateId": data.get("id"),
                    "projectId": data.get("project_id"),
                    "projectName": data.get("project__name"),
                    "templateName": data.get("pipeline_template__name"),
                    "category": category_dict[data.get("category")],
                    "editTime": data.get("pipeline_template__edit_time").strftime("%Y-%m-%d %H:%M:%S"),
                    "editor": data.get("pipeline_template__editor"),
                }
            )
        return total, groups

    def group_by_template_node(self, tasktmpl, filters, page, limit):
        # 按起始时间、业务（可选）、类型（可选）查询各流程模板标准插件节点个数、子流程节点个数、网关节点数
        total = tasktmpl.count()
        groups = []

        # 获得所有类型的dict列表
        category_dict = dict(TASK_CATEGORY)

        # 过滤得到所有符合查询条件的流程
        template_id_list = list(tasktmpl.values_list("pipeline_template__template_id", flat=True))
        id_list = tasktmpl.values("pipeline_template__id", "pipeline_template__template_id")
        template_pipeline_data = TemplateInPipeline.objects.filter(template_id__in=template_id_list)
        # 查询所有的流程引用，并统计引用数量
        relationship_list = (
            TemplateRelationship.objects.filter(descendant_template_id__in=template_id_list)
            .values("descendant_template_id")
            .annotate(relationship_total=Count("descendant_template_id"))
        )
        # 构造id： template_id字典，方便后面对不同model进行查询
        template_id_map = {
            template["pipeline_template__id"]: template["pipeline_template__template_id"] for template in id_list
        }
        # 查询所有的任务，并统计每个template创建了多少个任务
        taskflow_list = (
            PipelineInstance.objects.filter(template_id__in=list(template_id_map.keys()))
            .values("template_id")
            .annotate(instance_total=Count("template_id"))
            .order_by()
        )
        # 查询所有归档的周期任务，并统计每个template创建了多少个周期任务
        periodic_list = (
            PeriodicTask.objects.filter(template__template_id__in=template_id_list)
            .values("template__template_id")
            .annotate(periodic_total=Count("template__id"))
        )

        pipeline_dict = {}
        for pipeline in template_pipeline_data:
            pipeline_dict[pipeline.template_id] = {
                "atom_total": pipeline.atom_total,
                "subprocess_total": pipeline.subprocess_total,
                "gateways_total": pipeline.gateways_total,
            }
        relationship_dict = {}
        for relationship in relationship_list:
            relationship_dict[relationship["descendant_template_id"]] = relationship["relationship_total"]

        taskflow_dict = {}
        for taskflow in taskflow_list:
            taskflow_dict[template_id_map[taskflow["template_id"]]] = taskflow["instance_total"]

        periodic_dict = {}
        for periodic_task in periodic_list:
            periodic_dict[periodic_task["template__template_id"]] = periodic_task["periodic_total"]

        # 需要循环执行计算相关节点
        for template in tasktmpl:
            pipeline_template = template.pipeline_template
            template_id = template.id
            pipeline_template_id = pipeline_template.template_id
            # 插入信息
            groups.append(
                {
                    "templateId": template_id,
                    "projectId": template.project.id,
                    "projectName": template.project.name,
                    "templateName": pipeline_template.name,
                    "category": category_dict[template.category],
                    "createTime": format_datetime(pipeline_template.create_time),
                    "creator": pipeline_template.creator,
                    "atomTotal": pipeline_dict[pipeline_template_id]["atom_total"],
                    "subprocessTotal": pipeline_dict[pipeline_template_id]["subprocess_total"],
                    "gatewaysTotal": pipeline_dict[pipeline_template_id]["gateways_total"],
                    "relationshipTotal": relationship_dict.get(pipeline_template_id, 0),
                    "instanceTotal": taskflow_dict.get(pipeline_template_id, 0),
                    "periodicTotal": periodic_dict.get(pipeline_template_id, 0),
                }
            )

        order_by = filters.get("order_by", "-templateId")
        if order_by.startswith("-"):
            # 需要去除负号
            order_by = order_by[1:]
            groups = sorted(groups, key=lambda group: -group.get(order_by))
        else:
            groups = sorted(groups, key=lambda group: group.get(order_by))
        return total, groups[(page - 1) * limit : page * limit]

    def general_group_by(self, prefix_filters, group_by):
        try:
            total, groups = self.classified_count(prefix_filters, group_by)
            return True, None, total, groups
        except Exception as e:
            message = "query_task_list params conditions[%s] have invalid key or value: %s" % (prefix_filters, e)
            return False, message, None, None
