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
from collections import Counter

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from pipeline.component_framework.models import ComponentModel
from pipeline.contrib.periodic_task.models import PeriodicTask
from pipeline.models import PipelineInstance, PipelineTemplate, TemplateRelationship
from pipeline.parser.utils import replace_all_id

from gcloud import err_code
from gcloud.analysis_statistics.models import (
    ProjectStatisticsDimension,
    TaskflowStatistics,
    TaskTmplExecuteTopN,
    TemplateNodeStatistics,
    TemplateStatistics,
)
from gcloud.constants import AE, TASK_CATEGORY, TASK_FLOW_TYPE
from gcloud.core.models import Project
from gcloud.shortcuts.cmdb import get_business_attrinfo
from gcloud.template_base.models import BaseTemplate, BaseTemplateManager
from gcloud.template_base.utils import fill_default_version_to_service_activities, replace_biz_id_value
from gcloud.utils.components import format_component_name_with_remote
from gcloud.utils.dates import format_datetime
from gcloud.utils.managermixins import ClassificationCountMixin

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
        total = ComponentModel.objects.count()
        comp_name_dict = dict(ComponentModel.objects.values_list("code", "name"))
        task_template_id_list = tasktmpl.values_list("id", flat=True)
        # 查询出符合条件的不同原子引用
        template_node_template_data = list(
            TemplateNodeStatistics.objects.values("component_code", "version", "is_remote")
            .filter(task_template_id__in=task_template_id_list)
            .annotate(value=Count("id"))
        )
        groups = format_component_name_with_remote(template_node_template_data, comp_name_dict)
        return total, groups

    def group_by_atom_template(self, tasktmpl, filters, page, limit):
        # 按起始时间、业务（可选）、类型（可选）、标准插件查询被引用的流程模板列表(dataTable)

        # 获得所有类型的dict列表
        category_dict = dict(TASK_CATEGORY)

        tasktmpl_id_list = tasktmpl.values_list("id", flat=True)
        # 获取标准插件code
        component_code = filters.get("component_code")
        version = filters.get("version")
        is_remote = filters.get("is_remote", False)
        order_by = filters.get("order_by", "-template_create_time")
        # 对创建时间做一层转换
        if order_by.replace("-", "") == "create_time":
            order_by = order_by.replace("create_time", "template_create_time")
        # 获取到组件code对应的template_id_list
        if component_code:
            template_node_template_data = TemplateNodeStatistics.objects.filter(
                task_template_id__in=tasktmpl_id_list,
                component_code=component_code,
                version=version,
                is_remote=is_remote,
            )
        else:
            template_node_template_data = TemplateNodeStatistics.objects.filter(
                task_template_id__in=tasktmpl_id_list,
            )
        # 查询数据去重处理
        distinct_template_data = (
            template_node_template_data.values(
                "template_id",
                "task_template_id",
                "project_id",
                "category",
                "template_create_time",
                "template_creator",
            )
            .distinct()
            .order_by(order_by)
        )
        total = distinct_template_data.count()
        atom_template_data = distinct_template_data[(page - 1) * limit : page * limit]
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
        groups = []

        task_template_id_list = list(tasktmpl.values_list("id", flat=True))
        template_id_dict = dict(tasktmpl.values_list("pipeline_template__template_id", "id"))
        template_id_list = list(template_id_dict.keys())
        template_in_statistics_data = TemplateStatistics.objects.filter(task_template_id__in=task_template_id_list)
        total = template_in_statistics_data.count()
        template_id_map = {template.template_id: template.template_id for template in template_in_statistics_data}
        # 计算relationshipTotal, instanceTotal, periodicTotal
        # 查询所有的流程引用，并统计引用数量
        relationship_list = (
            TemplateRelationship.objects.filter(descendant_template_id__in=template_id_list)
            .values("descendant_template_id")
            .annotate(relationship_total=Count("descendant_template_id"))
        )
        # 查询所有的任务，并统计每个template已创建了多少个任务
        taskflow_list = list(
            PipelineInstance.objects.filter(template__id__in=list(template_id_map.keys()))
            .values("template_id")
            .annotate(instance_total=Count("template_id"))
            .order_by()
        )
        # 统计每个template已经启动了多少个任务
        taskflow_list_start = list(
            PipelineInstance.objects.filter(template__id__in=list(template_id_map.keys()), is_started=True)
            .values("template_id")
            .annotate(instance_total=Count("template_id"))
            .order_by()
        )
        # 查询所有归档的周期任务，并统计每个template创建了多少个周期任务
        periodic_list = (
            PeriodicTask.objects.filter(template__id__in=list(template_id_map.keys()))
            .values("template__id")
            .annotate(periodic_total=Count("template__id"))
        )
        relationship_dict = {}
        for relationship in relationship_list:
            try:
                relationship_dict[template_id_dict[relationship["descendant_template_id"]]] = relationship[
                    "relationship_total"
                ]
            except KeyError:
                continue
        taskflow_dict = {}
        for taskflow in taskflow_list:
            try:
                taskflow_dict[template_id_map[taskflow["template_id"]]] = taskflow["instance_total"]
            except KeyError:
                continue
        taskflow_start_dict = {}
        for taskflow in taskflow_list_start:
            try:
                taskflow_start_dict[template_id_map[taskflow["template_id"]]] = taskflow["instance_total"]
            except KeyError:
                continue
        periodic_dict = {}
        for periodic_task in periodic_list:
            try:
                periodic_dict[periodic_task["template__id"]] = periodic_task["periodic_total"]
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
                    "template_id": data.task_template_id,
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
                    "relationship_total": relationship_dict.get(data.task_template_id, 0),
                    "instance_total": taskflow_start_dict.get(data.template_id, 0),
                    "periodic_total": periodic_dict.get(data.template_id, 0),
                    "taskflow_total": taskflow_dict.get(data.template_id, 0),
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

    def group_by_template_execute_times(self, tasktmpl, filters, page, limit):
        topn = TaskTmplExecuteTopN.objects.all().first()
        if not topn:
            # 默认返回top5
            topn = 5
        else:
            topn = topn.topn
        tasktmpl_dict = dict(tasktmpl.values_list("id", "pipeline_template__name"))
        tasktmpl_id_list = list(tasktmpl_dict.keys())
        # 计算使用过的流程使用次数
        used = TaskflowStatistics.objects.filter(task_template_id__in=tasktmpl_id_list).values_list(
            "task_template_id", flat=True
        )
        task_create_methods = TaskflowStatistics.objects.filter(task_template_id__in=used).values(
            "task_template_id", "create_method"
        )
        tmpl_task_dict = {}
        for tmpl in task_create_methods:
            create_method = tmpl["create_method"]
            tmpl_task_dict.setdefault(tmpl["task_template_id"], {create_method: 0})
            tmpl_task_dict[tmpl["task_template_id"]][create_method] = (
                tmpl_task_dict[tmpl["task_template_id"]].setdefault(create_method, 0) + 1
            )
        used_count = dict(Counter(used))
        total = topn
        groups = []
        for task_template_id, count in used_count.items():
            groups.append(
                {
                    "template_id": task_template_id,
                    "template_name": tasktmpl_dict.get(int(task_template_id), ""),
                    "count": count,
                    "create_method": [
                        {"name": name, "value": value}
                        for name, value in tmpl_task_dict.get(task_template_id, {}).items()
                    ],
                }
            )
        groups.sort(key=lambda item: item.get("count", 0), reverse=True)
        return total, groups[0:topn]

    def group_by_execute_in_biz(self, tasktmpl, filters, page, limit):
        project_dict = dict(Project.objects.values_list("id", "name"))
        proj_id_list = tasktmpl.values("project", "pipeline_template__id")
        proj_dict = {}
        # 生成项目-流程字典
        for item in proj_id_list:
            proj_dict[item["project"]] = proj_dict.get(item["project"], [])
            proj_dict[item["project"]].append(str(item["pipeline_template__id"]))
        groups = []
        total = len(proj_dict)
        for proj, tasktmpl_list in proj_dict.items():
            all_tasktmpl_count = len(tasktmpl_list)
            used_count = (
                TaskflowStatistics.objects.filter(template_id__in=tasktmpl_list)
                .values("template_id")
                .distinct()
                .count()
            )
            unused_count = all_tasktmpl_count - used_count
            groups.append(
                {
                    "project_id": proj,
                    "project_name": project_dict[proj],
                    "useage": [{"name": "已使用", "value": used_count}, {"name": "未使用", "value": unused_count}],
                }
            )
        groups.sort(key=lambda x: x["useage"][0]["value"], reverse=True)
        return total, groups

    def group_by_template_biz(self, tasktmpl, filters, page, limit):
        proj_task_count = dict(
            tasktmpl.values_list("project__bk_biz_id").annotate(value=Count("project__id")).order_by("value")
        )
        proj_dimension_dict = dict(
            ProjectStatisticsDimension.objects.values_list("dimension_id", "dimension_name")
        ) or {"bk_biz_name": _("业务")}
        proj_dimension_id_list = proj_dimension_dict.keys()
        # 获取全部业务对应维度信息
        total = len(proj_dimension_id_list)
        groups = []
        proj_attr_info = get_business_attrinfo(tasktmpl.project.tenant_id, proj_dimension_id_list)
        for dimension in proj_dimension_id_list:
            result = {}
            # 对应统计维度cmdb总数
            dimension_total = 0
            for info in proj_attr_info:
                value = proj_task_count.get(info["bk_biz_id"], 0)
                result.setdefault(info[dimension], {"project_id": info["bk_biz_id"], "value": 0})["value"] += value
                dimension_total += value
            info = [{"name": key, "value": value["value"]} for key, value in result.items()]
            groups.append(
                {
                    "dimension_id": dimension,
                    "dimension_name": proj_dimension_dict[dimension],
                    "dimension_total": dimension_total,
                    "info": sorted(info, key=lambda item: item["value"], reverse=True),
                }
            )
        return total, groups

    def general_group_by(self, prefix_filters, group_by):
        try:
            total, groups = self.classified_count(prefix_filters, group_by)
            return True, None, total, groups
        except Exception as e:
            message = "query_task_list params conditions[%s] have invalid key or value: %s" % (prefix_filters, e)
            return False, message, None, None

    def export_templates(self, template_id_list, **kwargs):
        query_params = {"project_id": kwargs["project_id"]}
        if kwargs.get("is_full"):
            template_id_list = list(self.filter(**query_params).values_list("id", flat=True))
        else:
            query_params["id__in"] = template_id_list
            if self.filter(**query_params).count() != len(template_id_list):
                raise self.model.DoesNotExist("{}(id={}) does not exist.".format(self.model.__name__, template_id_list))

        export_data = super(TaskTemplateManager, self).export_templates(template_id_list, **kwargs)

        if kwargs.get("export_app_maker"):

            # 导出任务流程关联的轻应用
            from gcloud.contrib.appmaker.models import AppMaker

            app_maker_cls: AppMaker = apps.get_model("appmaker", "AppMaker")
            app_makers = list(
                app_maker_cls.objects.filter(task_template_id__in=template_id_list).values(
                    "id", "name", "desc", "creator", "task_template_id", "template_scheme_id", "project_id"
                )
            )
            # formatter
            for app_maker in app_makers:
                app_maker["username"] = app_maker.pop("creator")
                app_maker["template_id"] = app_maker.pop("task_template_id")
            export_data["app_makers"] = app_makers

        return export_data

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
            replace_biz_id_value(template["tree"], bk_biz_id)

    def _reset_project_id(self, templates_data, project_id):
        for app_maker in templates_data.get("app_makers") or []:
            app_maker["project_id"] = project_id

        for clocked_task in templates_data.get("clocked_tasks") or []:
            clocked_task["project_id"] = project_id

    def import_templates(self, template_data, override, project_id, operator=None):
        project = Project.objects.get(id=project_id)
        check_info = self.import_operation_check(template_data, project_id)
        # reset biz_cc_id select in templates
        self._reset_biz_selector_value(template_data, project.bk_biz_id)
        # 替换导出数据中的 project_id
        self._reset_project_id(template_data, project_id)
        for template in template_data["pipeline_template_data"]["template"].values():
            fill_default_version_to_service_activities(template["tree"])

        # operation validation check
        if override and (not check_info["can_override"]):
            message = _("流程导入失败: 跨业务导入流程不支持覆盖相同ID, 请检查配置 | import_templates")
            logger.error(message)
            return {"result": False, "message": message, "data": 0, "code": err_code.INVALID_OPERATION.code}

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
    default_flow_type = models.CharField(
        _("偏好任务流程类型"), max_length=255, choices=TASK_FLOW_TYPE, default="common"
    )

    objects = TaskTemplateManager()

    @property
    def instance_id(self):
        return self.id

    def __unicode__(self):
        return "%s_%s" % (self.project, self.pipeline_template)

    class Meta(BaseTemplate.Meta):
        verbose_name = _("流程模板 TaskTemplate")
        verbose_name_plural = _("流程模板 TaskTemplate")
