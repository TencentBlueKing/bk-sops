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

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models import Count

from pipeline.parser.utils import replace_all_id
from pipeline.component_framework.models import ComponentModel
from pipeline.contrib.periodic_task.models import PeriodicTask
from pipeline.models import PipelineInstance, TemplateRelationship, PipelineTemplate

from gcloud import err_code
from gcloud.constants import TASK_FLOW_TYPE, TASK_CATEGORY
from gcloud.constants import TEMPLATE_EXPORTER_SOURCE_PROJECT, AE
from gcloud.template_base.models import BaseTemplate, BaseTemplateManager
from gcloud.core.models import Project
from gcloud.utils.managermixins import ClassificationCountMixin
from gcloud.utils.dates import format_datetime
from gcloud.analysis_statistics.models import TemplateStatistics, TemplateNodeStatistics
from gcloud.utils.components import format_component_name

logger = logging.getLogger("root")


class TaskTemplateManager(BaseTemplateManager, ClassificationCountMixin):
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
        components = ComponentModel.objects.values("code", "version", "name")
        total = components.count()
        groups = []
        task_template_id_list = tasktmpl.values_list("id", flat=True)
        # 查询出符合条件的不同原子引用
        template_node_template_data = (
            TemplateNodeStatistics.objects.values("component_code", "version")
            .filter(task_template_id__in=task_template_id_list)
            .annotate(value=Count("id"))
        )

        groups = format_component_name(components, template_node_template_data)
        return total, groups

    def group_by_atom_template(self, tasktmpl, filters, page, limit):
        # 按起始时间、业务（可选）、类型（可选）、标准插件查询被引用的流程模板列表(dataTable)

        # 获得所有类型的dict列表
        category_dict = dict(TASK_CATEGORY)

        tasktmpl_id_list = tasktmpl.values_list("id", flat=True)
        # 获取标准插件code
        component_code = filters.get("component_code")
        version = filters.get("version")
        # 获取到组件code对应的template_id_list
        if component_code:
            template_node_template_data = TemplateNodeStatistics.objects.filter(
                task_template_id__in=tasktmpl_id_list, component_code=component_code, version=version
            )
        else:
            template_node_template_data = TemplateNodeStatistics.objects.filter(
                task_template_id__in=tasktmpl_id_list,
            )
        total = template_node_template_data.count()
        atom_template_data = template_node_template_data.values(
            "template_id",
            "task_template_id",
            "project_id",
            "category",
            "template_create_time",
            "template_creator",
        )[(page - 1) * limit : page * limit]
        groups = []
        # 在template_node_tempalte_data中注入project_name和template_name
        project_id_list = template_node_template_data.values_list("project_id", flat=True)
        template_id_list = template_node_template_data.values_list("template_id", flat=True)
        project_dict = dict(Project.objects.filter(id__in=project_id_list).values_list("id", "name"))
        template_dict = dict(PipelineTemplate.objects.filter(id__in=template_id_list).values_list("id", "name"))
        # 循环聚合信息
        for data in atom_template_data:
            groups.append(
                {
                    "template_id": data["task_template_id"],
                    "project_id": data["project_id"],
                    "project_name": project_dict.get(data["project_id"], ""),
                    "template_name": template_dict.get(int(data["template_id"]), ""),
                    "category": category_dict[data["category"]],  # 需要将code转为名称
                    "create_time": format_datetime(data["template_create_time"]),
                    "creator": data["template_creator"],
                }
            )
        # order_by字段错误的情况默认使用-template_d排序
        order_by = filters.get("order_by", "-template_id")
        if order_by.startswith("-"):
            # 需要去除负号
            order_by = order_by[1:]
            groups = sorted(groups, key=lambda group: group.get(order_by), reverse=True)
        else:
            groups = sorted(groups, key=lambda group: group.get(order_by), reverse=False)
        return total, groups

    def group_by_atom_execute(self, tasktmpl, filters, page, limit):
        # 需要获得符合的查询的对应 template_id 列表

        # 获得所有类型的dict列表
        category_dict = dict(TASK_CATEGORY)

        # 获取标准插件code
        component_code = filters.get("component_code")
        # 获取到组件code对应的template_node_template
        template_node_template_list = TemplateNodeStatistics.objects.filter(component_code=component_code)
        total = template_node_template_list.count()
        atom_template_data = template_node_template_list.values(
            "template_id",
            "project_id",
            "category",
            "template_edit_time",
            "template_creator",
        )[(page - 1) * limit : page * limit]
        # 获取project_name、template_name数据
        project_id_list = template_node_template_list.values_list("project_id", flat=True)
        template_id_list = template_node_template_list.values_list("template_id", flat=True)
        project_dict = dict(Project.objects.filter(id__in=project_id_list).values_list("id", "name"))
        tempalte_dict = dict(self.filter(id__in=template_id_list).values_list("id", "pipeline_template__name"))
        groups = []
        # 循环聚合信息
        for data in atom_template_data:
            groups.append(
                {
                    "template_id": data["template_id"],
                    "project_id": data["project_id"],
                    "project_name": project_dict.get(data["project_id"], ""),
                    "template_name": tempalte_dict.get(int(data["template_id"]), ""),
                    "category": category_dict[data["category"]],
                    "edit_time": format_datetime(data["template_edit_time"]),
                    "editor": data["template_creator"],
                }
            )
        return total, groups

    def group_by_template_node(self, tasktmpl, filters, page, limit):
        # 按起始时间、业务（可选）、类型（可选）查询各流程模板标准插件节点个数、子流程节点个数、网关节点数
        total = tasktmpl.count()
        groups = []

        template_id_list = list(tasktmpl.values_list("id", flat=True))
        template_in_statistics_data = TemplateStatistics.objects.filter(task_template_id__in=template_id_list)
        template_id_map = {template.template_id: template.task_template_id for template in template_in_statistics_data}
        # 计算relationshipTotal, instanceTotal, periodicTotal
        # 查询所有的流程引用，并统计引用数量
        relationship_list = (
            TemplateRelationship.objects.filter(descendant_template_id__in=template_id_list)
            .values("descendant_template_id")
            .annotate(relationship_total=Count("descendant_template_id"))
        )
        # 查询所有的任务，并统计每个template创建了多少个任务
        taskflow_list = list(
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
        relationship_dict = {}
        for relationship in relationship_list:
            try:
                relationship_dict[relationship["descendant_template_id"]] = relationship["relationship_total"]
            except KeyError:
                continue
        taskflow_dict = {}
        for taskflow in taskflow_list:
            try:
                taskflow_dict[template_id_map[str(taskflow["template_id"])]] = taskflow["instance_total"]
            except KeyError:
                continue
        periodic_dict = {}
        for periodic_task in periodic_list:
            try:
                periodic_dict[periodic_task["template__template_id"]] = periodic_task["periodic_total"]
            except KeyError:
                continue
        # 查询所有project_name
        project_id_list = list(template_in_statistics_data.values_list("project_id", flat=True))
        project_dict = dict(Project.objects.filter(id__in=project_id_list).values_list("id", "name"))
        # 查询所有template_name
        template_id_list = list(template_in_statistics_data.values_list("template_id", flat=True))
        template_dict = dict(PipelineTemplate.objects.filter(id__in=template_id_list).values_list("id", "name"))
        for data in template_in_statistics_data:
            groups.append(
                {
                    "template_id": data.template_id,
                    "project_id": data.project_id,
                    "project_name": project_dict.get(data.project_id, ""),
                    "template_name": template_dict.get(int(data.template_id), ""),
                    "category": data.category,
                    "create_time": data.template_create_time,
                    "edit_time": data.template_edit_time,
                    "creator": data.template_creator,
                    "atom_toal": data.atom_total,
                    "subprocess_total": data.subprocess_total,
                    "gateways_total": data.gateways_total,
                    "relationship_total": relationship_dict.get(data.template_id, 0),
                    "instance_total": taskflow_dict.get(data.template_id, 0),
                    "periodic_total": periodic_dict.get(data.template_id, 0),
                    "output_count": data.output_count,
                    "input_count": data.input_count,
                }
            )
        # order_by字段错误的情况默认使用-templateId排序
        order_by = filters.get("order_by", "-template_id")
        if order_by.startswith("-"):
            # 需要去除负号
            order_by = order_by[1:]
            groups = sorted(groups, key=lambda group: group.get(order_by), reverse=True)
        else:
            groups = sorted(groups, key=lambda group: group.get(order_by), reverse=False)
        return total, groups[(page - 1) * limit : page * limit]

    def general_group_by(self, prefix_filters, group_by):
        try:
            total, groups = self.classified_count(prefix_filters, group_by)
            return True, None, total, groups
        except Exception as e:
            message = "query_task_list params conditions[%s] have invalid key or value: %s" % (prefix_filters, e)
            return False, message, None, None

    def export_templates(self, template_id_list, project_id):
        if self.filter(id__in=template_id_list, project_id=project_id).count() != len(template_id_list):
            raise self.model.DoesNotExist("{}(id={}) does not exist.".format(self.model.__name__, template_id_list))
        data = super(TaskTemplateManager, self).export_templates(template_id_list)
        data["template_source"] = TEMPLATE_EXPORTER_SOURCE_PROJECT
        return data

    def import_operation_check(self, template_data, project_id):
        data = super(TaskTemplateManager, self).import_operation_check(template_data)

        template = template_data["template"]

        relate_project_ids = self.filter(id__in=list(template.keys()), is_deleted=False).values_list(
            "project_id", flat=True
        )
        is_multiple_relate = len(set(relate_project_ids)) > 1
        is_across_override = relate_project_ids and relate_project_ids[0] != int(project_id)
        has_common_template = not all([tmpl.get("project_id") for _, tmpl in list(template_data["template"].items())])

        can_override = not (is_multiple_relate or is_across_override or has_common_template)

        # 以文件中设定的禁止覆盖设定为最高优先级
        if template_data.get("override_forbidden", False):
            can_override = False

        if not can_override:
            data["override_template"] = []

        result = {
            "can_override": can_override,
            "new_template": data["new_template"],
            "override_template": data["override_template"],
        }
        return result

    def _reset_biz_selector_value(self, templates_data, bk_biz_id):
        for template in templates_data["pipeline_template_data"]["template"].values():
            for act in [act for act in template["tree"]["activities"].values() if act["type"] == "ServiceActivity"]:
                act_info = act["component"]["data"]
                biz_cc_id_field = act_info.get("biz_cc_id") or act_info.get("bk_biz_id")
                if biz_cc_id_field and (not biz_cc_id_field["hook"]):
                    biz_cc_id_field["value"] = bk_biz_id

            for constant in template["tree"]["constants"].values():
                if constant["source_tag"].endswith(".biz_cc_id") and constant["value"]:
                    constant["value"] = bk_biz_id

    def import_templates(self, template_data, override, project_id, operator=None):
        project = Project.objects.get(id=project_id)
        check_info = self.import_operation_check(template_data, project_id)
        # reset biz_cc_id select in templates
        self._reset_biz_selector_value(template_data, project.bk_biz_id)

        # operation validation check
        if override and (not check_info["can_override"]):
            return {
                "result": False,
                "message": _("跨业务导入模版不支持覆盖相同ID"),
                "data": 0,
                "code": err_code.INVALID_OPERATION.code,
            }

        def defaults_getter(template_dict):
            return {
                "project": project,
                "category": template_dict["category"],
                "notify_type": template_dict["notify_type"],
                "notify_receivers": template_dict["notify_receivers"],
                "time_out": template_dict["time_out"],
                "pipeline_template_id": template_dict["pipeline_template_id"],
                "is_deleted": False,
            }

        return super(TaskTemplateManager, self)._perform_import(
            template_data=template_data,
            check_info=check_info,
            override=override,
            defaults_getter=defaults_getter,
            operator=operator,
        )

    def replace_all_template_tree_node_id(self):
        templates = self.filter(is_deleted=False)
        success = 0
        for template in templates:
            tree_data = template.pipeline_template.data
            try:
                replace_all_id(tree_data)
            except Exception:
                continue
            template.pipeline_template.update_template(tree_data)
            success += 1
        return len(templates), success

    def get_collect_template(self, project_id, username):
        user_model = get_user_model()
        collected_templates = user_model.objects.get(username=username).tasktemplate_set.values_list("id", flat=True)
        collected_templates_list = []
        template_list = self.filter(is_deleted=False, project_id=project_id, id__in=list(collected_templates))
        for template in template_list:
            collected_templates_list.append({"id": template.id, "name": template.name})
        return True, collected_templates_list

    def get_templates_with_expired_subprocess(self, project_id):
        tmpl_and_pipeline_id = self.filter(project_id=project_id, is_deleted=False).values("id", "pipeline_template_id")
        return self.check_templates_subprocess_expired(tmpl_and_pipeline_id)


class TaskTemplate(BaseTemplate):
    project = models.ForeignKey(Project, verbose_name=_("所属项目"), null=True, blank=True, on_delete=models.SET_NULL)
    executor_proxy = models.CharField(_("任务执行人代理"), max_length=255, default="", blank=True)
    default_flow_type = models.CharField(_("偏好任务流程类型"), max_length=255, choices=TASK_FLOW_TYPE, default="common")

    objects = TaskTemplateManager()

    def __unicode__(self):
        return "%s_%s" % (self.project, self.pipeline_template)

    class Meta(BaseTemplate.Meta):
        verbose_name = _("流程模板 TaskTemplate")
        verbose_name_plural = _("流程模板 TaskTemplate")
