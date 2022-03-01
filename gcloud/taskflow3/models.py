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
import datetime
import traceback
from copy import deepcopy

import ujson as json
from django.db import connection
from django.db.models import Count, Q
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

from pipeline.core.constants import PE
from pipeline.models import PipelineInstance
from pipeline.engine import states

from gcloud.taskflow3.utils import parse_node_timeout_configs
from pipeline_web.core.abstract import NodeAttr
from pipeline.component_framework.models import ComponentModel
from pipeline_web.core.models import NodeInInstance
from pipeline_web.parser.clean import PipelineWebTreeCleaner
from pipeline_web.wrapper import PipelineTemplateWebWrapper
from pipeline_web.preview_base import PipelineTemplateWebPreviewer

from gcloud import err_code
from gcloud.conf import settings
from gcloud.constants import TASK_FLOW_TYPE, TASK_CATEGORY, TASKFLOW_NODE_TIMEOUT_CONFIG_BATCH_CREAT_COUNT
from gcloud.core.models import Project, EngineConfig, StaffGroupSet
from gcloud.core.utils import convert_readable_username
from gcloud.contrib.appmaker.models import AppMaker
from gcloud.utils.dates import timestamp_to_datetime, format_datetime
from gcloud.utils.managermixins import ClassificationCountMixin
from gcloud.common_template.models import CommonTemplate
from gcloud.template_base.utils import replace_template_id
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.constants import NON_COMMON_TEMPLATE_TYPES
from gcloud.taskflow3.domains.context import TaskContext
from gcloud.constants import TASK_CREATE_METHOD, TEMPLATE_SOURCE, PROJECT, ONETIME
from gcloud.taskflow3.domains.dispatchers import TaskCommandDispatcher, NodeCommandDispatcher
from gcloud.shortcuts.cmdb import get_business_group_members
from gcloud.project_constants.domains.context import get_project_constants_context
from gcloud.analysis_statistics.models import (
    TaskflowStatistics,
    TaskflowExecutedNodeStatistics,
    ProjectStatisticsDimension,
)
from gcloud.utils.components import format_component_name_with_remote, get_remote_plugin_name
from gcloud.shortcuts.cmdb import get_business_attrinfo

logger = logging.getLogger("root")

MANUAL_INTERVENTION_EXEMPT_STATES = frozenset([states.CREATED, states.FINISHED, states.REVOKED])

MANUAL_INTERVENTION_REQUIRED_STATES = frozenset([states.FAILED, states.SUSPENDED])

MANUAL_INTERVENTION_COMP_CODES = frozenset(["pause_node"])


class TaskFlowStatisticsMixin(ClassificationCountMixin):
    TASK_CATEGORY_DICT = dict(TASK_CATEGORY)

    def _assemble_where_statement(self, filters):
        category = filters.get("category")
        project_id = filters.get("project_id")

        conditions = []
        if category:
            conditions.append(
                '`category` = "%s"' % (category if category in self.TASK_CATEGORY_DICT else TASK_CATEGORY[-1][0])
            )

        if project_id:
            conditions.append("`project_id` = %s" % int(project_id))

        if conditions:
            return " WHERE %s" % (" AND ".join(conditions))
        else:
            return ""

    def _filter_project(self, project_id=""):
        return (
            "INNER JOIN (SELECT `pipeline_instance_id` FROM `taskflow3_taskflowinstance` \
                  WHERE `project_id`={}) T \
                  ON (P.id = T.pipeline_instance_id)".format(
                project_id
            )
            if project_id
            else ""
        )

    def group_by_state(self, taskflow, *args):
        # 按流程执行状态查询流程个数
        total = taskflow.count()
        groups = [
            {
                "code": "CREATED",
                "name": _("未执行"),
                "value": taskflow.filter(pipeline_instance__is_started=False).count(),
            },
            {
                "code": "EXECUTING",
                "name": _("执行中"),
                "value": taskflow.filter(
                    pipeline_instance__is_started=True, pipeline_instance__is_finished=False
                ).count(),
            },
            {
                "code": "FINISHED",
                "name": _("已完成"),
                "value": taskflow.filter(pipeline_instance__is_finished=True).count(),
            },
        ]
        return total, groups

    def group_by_appmaker_instance(self, taskflow, filters, page, limit):
        # 查询不同轻应用对应的流程数

        # 获得所有类型的dict列表
        category_dict = dict(TASK_CATEGORY)

        taskflow_values = taskflow.values("create_info")
        order_by = filters.get("order_by", "-template_id")
        project_id = filters.get("project_id", "")
        category = filters.get("category", "")
        started_time = timestamp_to_datetime(filters["create_time"])
        end_time = timestamp_to_datetime(filters["finish_time"]) + datetime.timedelta(days=1)
        appmaker_data = AppMaker.objects.filter(
            is_deleted=False, create_time__gte=started_time, create_time__lte=end_time
        )
        if project_id != "":
            appmaker_data = appmaker_data.filter(project_id=project_id)
        if category != "":
            appmaker_data = appmaker_data.filter(task_template__category=category)
        # 获取所有轻应用数据数量
        total = appmaker_data.count()
        # 获得每一个轻应用的实例数量并变为 dict 字典数据进行查询
        total_dict = {
            appmaker["create_info"]: appmaker["instance_total"]
            for appmaker in taskflow_values.annotate(instance_total=Count("create_info")).order_by()
        }
        id_list = appmaker_data.values_list("id")[:]

        id_list = sorted(id_list, key=lambda tuples_id: -total_dict.get(str(tuples_id[0]), 0))
        id_list = id_list[(page - 1) * limit : page * limit]
        app_id_list = [tuples[0] for tuples in id_list]
        # 获得轻应用对象对应的模板和轻应用名称
        appmaker_data = appmaker_data.filter(id__in=app_id_list).values(
            "id",
            "task_template_id",
            "name",
            "create_time",
            "edit_time",
            "creator",
            "project_id",
            "project__name",
            "task_template__category",
        )
        groups = []

        for data in appmaker_data:
            code = data.get("task_template_id")
            appmaker_id = data.get("id")
            groups.append(
                {
                    "template_id": code,
                    "create_time": format_datetime(data.get("create_time")),
                    "edit_time": format_datetime(data.get("edit_time")),
                    "creator": data.get("creator"),
                    "template_name": data.get("name"),
                    "project_id": data.get("project_id"),
                    "project_name": data.get("project__name"),
                    "category": category_dict[data.get("task_template__category")],
                    # 需要将 code 转为字符型
                    "instance_total": total_dict.get(str(appmaker_id), 0),
                    "appmaker_id": data.get("id"),
                }
            )
        if order_by.startswith("-"):
            # 需要去除负号
            order_by = order_by[1:]
            groups = sorted(groups, key=lambda group: -group.get(order_by))
        else:
            groups = sorted(groups, key=lambda group: group.get(order_by))
        return total, groups

    def group_by_atom_execute_times(self, taskflow, *args):
        # 查询各标准插件被执行次数
        total = ComponentModel.objects.count()
        comp_name_dict = dict(ComponentModel.objects.values_list("code", "name"))
        taskflow_id_list = taskflow.values_list("id", flat=True)
        # 查询出符合条件的执行过的不同流程引用
        components_data = list(
            TaskflowExecutedNodeStatistics.objects.filter(task_instance_id__in=taskflow_id_list)
            .values("component_code", "version", "is_remote")
            .annotate(value=Count("task_instance_id"))
        )
        groups = format_component_name_with_remote(components_data, comp_name_dict)
        return total, groups

    def group_by_atom_execute_fail_times(self, taskflow, *args):
        # 查询各标准插件失败次数
        total = ComponentModel.objects.count()
        comp_name_dict = dict(ComponentModel.objects.values_list("code", "name"))
        # 查询出符合条件的执行过的不同流程引用
        components_data = list(
            TaskflowExecutedNodeStatistics.objects.values("component_code", "version", "is_remote").annotate(
                value=Count("id", filter=Q(status=False))
            )
        )

        groups = format_component_name_with_remote(components_data, comp_name_dict)
        return total, groups

    def group_by_atom_avg_execute_time(self, taskflow, *args):
        # 查询各插件平均执行耗时
        total = ComponentModel.objects.count()
        comp_name_dict = dict(ComponentModel.objects.values_list("code", "name"))
        taskflow_id_list = taskflow.values_list("id", flat=True)
        # 查询出符合条件的执行过的插件的执行耗时
        components_data = TaskflowExecutedNodeStatistics.objects.values(
            "component_code", "version", "elapsed_time", "is_remote"
        ).filter(task_instance_id__in=taskflow_id_list)

        # 插件名国际化、计算平均耗时
        remote_plugin_dict = get_remote_plugin_name()
        elapsed_time_dict = {}
        code_count_dict = {}
        for comp in components_data:
            version = comp["version"]
            # 插件名国际化
            if not comp["is_remote"]:
                # 系统内置插件
                name = comp_name_dict.get(comp["component_code"], comp["component_code"]).split("-")
                name = "{}-{}-{}".format(_(name[0]), _(name[1]), version)
            else:
                # 第三方插件
                name = remote_plugin_dict.get(comp["component_code"], comp["component_code"]).split("-")
                name = "{}-{}-{}".format(_("第三方插件"), _(name[0]), version)
            code = "{}-{}".format(comp["component_code"], comp["version"])
            value = comp["elapsed_time"]

            # 计算平均耗时
            code_count_dict.setdefault(code, {"code": code, "sum_time": value, "count": 1})["sum_time"] += value
            code_count_dict.setdefault(code, {"code": code, "sum_time": value, "count": 1})["count"] += 1
            elapsed_time_dict.setdefault(code, {"code": code, "name": name, "value": value})["value"] = round(
                code_count_dict[code]["sum_time"] / code_count_dict[code]["count"], 2
            )
        return total, list(elapsed_time_dict.values())

    def group_by_atom_fail_percent(self, taskflow, *args):
        # 查询各插件执行失败率
        total = ComponentModel.objects.count()
        comp_name_dict = dict(ComponentModel.objects.values_list("code", "name"))
        taskflow_id_list = taskflow.values_list("id", flat=True)
        # 查询出符合条件的执行过的插件数据
        components_data = list(
            TaskflowExecutedNodeStatistics.objects.values("component_code", "version", "status", "is_remote").filter(
                task_instance_id__in=taskflow_id_list
            )
        )

        # 插件名国际化、计算失败率
        remote_plugin_dict = get_remote_plugin_name()
        fail_suc_cou_dict = {}
        result_dict = {}
        for comp in components_data:
            version = comp["version"]
            # 插件名国际化
            if not comp["is_remote"]:
                # 系统内置插件
                name = comp_name_dict.get(comp["component_code"], comp["component_code"]).split("-")
                name = "{}-{}-{}".format(_(name[0]), _(name[1]), version)
            else:
                # 第三方插件
                name = remote_plugin_dict.get(comp["component_code"], comp["component_code"]).split("-")
                name = "{}-{}-{}".format(_("第三方插件"), _(name[0]), version)
            code = "{}-{}".format(comp["component_code"], comp["version"])
            success = 0 if not comp["status"] else 1
            fail = 1 if not comp["status"] else 0
            fail_suc_cou_dict.setdefault(code, {"success": 0, "fail": 0})
            fail_suc_cou_dict[code]["success"] += success
            fail_suc_cou_dict[code]["fail"] += fail
            result_dict.setdefault(code, {"code": code, "name": name, "value": 0})["value"] = round(
                fail_suc_cou_dict[code]["fail"] * 100 / (sum(fail_suc_cou_dict[code].values())), 2
            )
        return total, list(result_dict.values())

    def group_by_atom_instance(self, taskflow, filters, page, limit):
        # 被引用的任务实例列表

        # 获得参数中的标准插件code
        component_code = filters.get("component_code")
        version = filters.get("version")
        is_remote = filters.get("is_remote", False)
        if component_code:
            instance_id_list = TaskflowExecutedNodeStatistics.objects.filter(
                is_sub=False, component_code=component_code, version=version, is_remote=is_remote
            ).values_list("instance_id", flat=True)
        else:
            instance_id_list = TaskflowExecutedNodeStatistics.objects.filter(is_sub=False).values_list(
                "instance_id", flat=True
            )

        taskflow_list = taskflow.filter(pipeline_instance__id__in=instance_id_list)
        # 获得总数
        total = taskflow_list.count()
        order_by = filters.get("order_by", "-instance_id")
        if order_by == "-instance_id":
            taskflow_list = taskflow_list.order_by("-id")
        elif order_by == "instance_id":
            taskflow_list = taskflow_list.order_by("id")
        taskflow_list = taskflow_list.values(
            "id",
            "project_id",
            "project__name",
            "pipeline_instance__name",
            "category",
            "pipeline_instance__create_time",
            "pipeline_instance__creator",
        )[(page - 1) * limit : page * limit]
        groups = []
        # 循环信息
        for data in taskflow_list:
            groups.append(
                {
                    "instance_id": data.get("id"),
                    "project_id": data.get("project_id"),
                    "project_name": data.get("project__name"),
                    "instance_name": data.get("pipeline_instance__name"),
                    "category": self.TASK_CATEGORY_DICT[data.get("category")],  # 需要将code转为名称
                    "create_time": format_datetime(data.get("pipeline_instance__create_time")),
                    "creator": data.get("pipeline_instance__creator"),
                }
            )
        return total, groups

    def group_by_category(self, taskflow, filters, page, limit):
        """
        根据分类对任务进行聚合
        :param taskflow: 上层传入的初始筛选 queryset，此处不使用
        :type taskflow: [type]
        :param filters: 过滤参数
        :type filters: [type]
        :param page: 数据页
        :type page: [type]
        :param limit: 返回数据条数
        :type limit: [type]
        """

        task_instance_id_list = taskflow.values_list("id", flat=True)
        taskflow_statistics_data = (
            TaskflowStatistics.objects.filter(task_instance_id__in=task_instance_id_list)
            .values("category")
            .annotate(value=Count("category"))
        )

        total = 1
        groups = [
            {
                "code": data["category"],
                "name": self.TASK_CATEGORY_DICT.get(data["category"], data["category"]),
                "value": data["value"],
            }
            for data in taskflow_statistics_data
        ]

        return total, groups

    def group_by_instance_node(self, taskflow, filters, page, limit):
        """
        @summary: 各任务实例执行的标准插件节点个数、子流程节点个数、网关节点数、执行耗时统计（支持排序）
        @param taskflow:
        @param filters:
        @param page:
        @param limit:
        @return:
        """

        # 查询出有序的taskflow统计数据
        total = taskflow.count()
        task_instance_id_list = taskflow.values_list("id", flat=True)
        taskflow_statistics_data = list(
            TaskflowStatistics.objects.filter(task_instance_id__in=task_instance_id_list)[
                (page - 1) * limit : page * limit
            ].values(
                "instance_id",
                "task_instance_id",
                "project_id",
                "category",
                "create_time",
                "creator",
                "elapsed_time",
                "atom_total",
                "subprocess_total",
                "gateways_total",
                "create_method",
            )
        )
        # 注入instance_name和project_name
        instance_id_list = [data["instance_id"] for data in taskflow_statistics_data]
        project_id_list = [data["project_id"] for data in taskflow_statistics_data]
        instance_dict = dict(PipelineInstance.objects.filter(id__in=instance_id_list).values_list("id", "name"))
        project_dict = dict(Project.objects.filter(id__in=project_id_list).values_list("id", "name"))
        groups = [
            {
                "instance_id": data["task_instance_id"],
                "instance_name": instance_dict.get(data["instance_id"], data["instance_id"]),
                "project_id": data["project_id"],
                "project_name": project_dict.get(data["project_id"], data["project_id"]),
                "category": self.TASK_CATEGORY_DICT.get(data["category"], data["category"]),
                "create_time": format_datetime(data["create_time"]),
                "creator": data["creator"],
                "elapsed_time": data["elapsed_time"],
                "atom_total": data["atom_total"],
                "subprocess_total": data["subprocess_total"],
                "gateways_total": data["gateways_total"],
                "create_method": data["create_method"],
            }
            for data in taskflow_statistics_data
        ]
        return total, groups

    def group_by_instance_time(self, taskflow, filters, page, limit):
        #  按起始时间、业务（可选）、类型（可选）、图表类型（日视图，月视图），查询每一天或每一月的执行数量
        task_instance_id_list = taskflow.values_list("id", flat=True)
        group_type = filters.get("type", "day")
        select = {"time": connection.ops.date_trunc_sql(group_type, "create_time")}
        results = (
            TaskflowStatistics.objects.filter(task_instance_id__in=task_instance_id_list)
            .extra(select=select)
            .values("time", "create_method")
            .annotate(value=Count("id"))
        ).order_by("time")
        total = sum([result["value"] for result in results])

        def format_groups(type):
            time_dict = {}
            for result in results:
                if type == "day":
                    str_time = "{:0}-{:1}-{:2}".format(result["time"].year, result["time"].month, result["time"].day)
                else:
                    str_time = "{:0}-{:1}".format(result["time"].year, result["time"].month)
                if str_time not in time_dict.keys():
                    time_dict[str_time] = {
                        "time": str_time,
                        "value": result["value"],
                        "create_method": [{"name": result["create_method"], "value": result["value"]}],
                    }
                else:
                    time_dict[str_time]["value"] += result["value"]
                    time_dict[str_time]["create_method"].append(
                        {"name": result["create_method"], "value": result["value"]}
                    )
            return list(time_dict.values())

        groups = format_groups(group_type)
        return total, groups

    def group_by_project_id(self, taskflow, filters, page, limit):
        # 查询不同业务对应的流程数
        taskflow_id_list = taskflow.values_list("id", flat=True)
        taskflow_statistics_data = (
            TaskflowStatistics.objects.filter(task_instance_id__in=taskflow_id_list)
            .values("project_id", "create_method")
            .annotate(value=Count("id"))
        )
        # 获取project_name
        project_id_list = taskflow_statistics_data.values_list("project_id", flat=True)
        project_dict = dict(Project.objects.filter(id__in=project_id_list).values_list("id", "name"))
        total = 1
        groups = [
            {
                "code": project_id,
                "name": project_dict.get(project_id, ""),
                "value": sum([data["value"] for data in taskflow_statistics_data if data["project_id"] == project_id]),
                "create_method": [
                    {"name": data["create_method"], "value": data["value"]}
                    for data in taskflow_statistics_data
                    if data["project_id"] == project_id
                ],
            }
            for project_id in project_dict.keys()
        ]

        return total, groups

    def group_by_common_func(self, taskflow, filters, page, limit):
        project_dict = dict(Project.objects.values_list("id", "name"))
        proj_flow_type = taskflow.values_list("project", "flow_type")
        # 计算各业务的各类型任务数量
        proj_flow_dict = {}
        for proj_flow in proj_flow_type:
            proj_id = proj_flow[0]
            flow_type = proj_flow[1]
            flow_type = "common_cou" if flow_type == "common" else "common_func_cou"
            proj_flow_dict.setdefault(proj_id, {"common_cou": 0, "common_func_cou": 0})[flow_type] += 1
        # 计算total、groups
        total = len(project_dict)
        groups = [
            {
                "project_name": project_dict[proj_id],
                "project_id": proj_id,
                "common_cou": value["common_cou"],
                "common_func_cou": value["common_func_cou"],
            }
            for proj_id, value in proj_flow_dict.items()
        ]
        return total, groups

    def group_by_instance_biz(self, taskflow, filters, page, limit):
        proj_task_count = dict(
            taskflow.values_list("project__bk_biz_id").annotate(value=Count("project__id")).order_by("value")
        )
        proj_dimension_dict = dict(ProjectStatisticsDimension.objects.values_list("dimension_id", "dimension_name"))
        proj_dimension_id_list = proj_dimension_dict.keys()
        # 获取全部业务对应维度信息
        total = len(proj_dimension_id_list)
        groups = []
        proj_attr_info = get_business_attrinfo(proj_dimension_id_list)
        for dimension in proj_dimension_id_list:
            result = {}
            dimension_total = 0
            for info in proj_attr_info:
                value = proj_task_count.get(info["bk_biz_id"], 0)
                result.setdefault(info[dimension], {"project_id": info["bk_biz_id"], "value": 0})
                result[info[dimension]]["value"] += value
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
        except Exception as e:
            message = "query_task_list params conditions[%s] have invalid key or value: %s" % (prefix_filters, e)
            return False, message, None, None
        return True, None, total, groups


class TaskFlowInstanceManager(models.Manager, TaskFlowStatisticsMixin):
    @staticmethod
    def create_pipeline_instance(template, **kwargs):
        pipeline_tree = kwargs["pipeline_tree"]
        replace_template_id(template.__class__, pipeline_tree)
        pipeline_template_data = {
            "name": kwargs["name"],
            "creator": kwargs["creator"],
            "description": kwargs.get("description", ""),
        }
        PipelineTemplateWebWrapper.unfold_subprocess(pipeline_tree, template.__class__)

        pipeline_web_cleaner = PipelineWebTreeCleaner(pipeline_tree)
        nodes_attr = pipeline_web_cleaner.clean(with_subprocess=True)

        pipeline_instance, id_maps = PipelineInstance.objects.create_instance(
            template.pipeline_template if template else None, pipeline_tree, spread=True, **pipeline_template_data
        )

        # create node in instance
        nodes_attr = pipeline_web_cleaner.replace_id(nodes_attr, id_maps, with_subprocess=True)
        pipeline_web_cleaner.to_web(nodes_attr, with_subprocess=True)
        NodeInInstance.objects.create_nodes_in_instance(pipeline_instance, pipeline_tree)
        return pipeline_instance

    @staticmethod
    def create_pipeline_instance_exclude_task_nodes(
        template, task_info, constants=None, exclude_task_nodes_id=None, simplify_vars=None
    ):
        """
        :param template: 任务模板
        :type template: TaskTemplate
        :param task_info: 任务信息 {
            'name': '',
            'creator': '',
            'description': '',
        }
        :type task_info: dict
        :param constants: 覆盖参数，如 {'${a}': '1', '${b}': 2}
        :type constants: dict, optional
        :param exclude_task_nodes_id: 取消执行的可选节点
        :type exclude_task_nodes_id: list
        :param simplify_vars: 需要进行类型简化的变量的 key 列表
        :type simplify_vars: list, optional
        :return: pipeline instance
        :rtype: PipelineInstance
        """
        if constants is None:
            constants = {}

        if simplify_vars is None:
            simplify_vars = {}
        else:
            simplify_vars = set(simplify_vars)

        pipeline_tree = template.pipeline_tree

        PipelineTemplateWebPreviewer.preview_pipeline_tree_exclude_task_nodes(pipeline_tree, exclude_task_nodes_id)

        # change constants
        for key, constant in pipeline_tree[PE.constants].items():
            # set meta field for meta var, so frontend can render meta form
            if constant.get("is_meta"):
                constant["meta"] = deepcopy(constant)
                # 下拉框类型默认值字段为default，表格类型为default_text
                constant["value"] = constant["value"].get("default") or constant["value"].get("default_text", "")
            if key in constants:
                constant["value"] = constants[key]

        # simplify var
        for key in simplify_vars:
            if key in pipeline_tree[PE.constants]:
                var = pipeline_tree[PE.constants][key]

                # 非自定义类型变量不允许简化
                if var["source_type"] != "custom":
                    continue

                var["custom_type"] = "textarea"
                var[
                    "form_schema"
                ] = """{
                    "type": "textarea",
                    "attrs": {
                        "name": "文本框",
                        "hookable": true,
                        "validation": [
                            {
                                "type": "required"
                            }
                        ]
                    }
                }"""
                var["source_tag"] = "textarea.textarea"
                var["is_meta"] = False

        task_info["pipeline_tree"] = pipeline_tree
        pipeline_inst = TaskFlowInstanceManager.create_pipeline_instance(template, **task_info)

        return pipeline_inst

    def creator_for(self, id):
        qs = self.filter(id=id).values("pipeline_instance__creator")

        if not qs:
            raise self.model.DoesNotExist("{}(id={}) does not exist.".format(self.model.__name__, id))

        return qs.first()["pipeline_instance__creator"]

    def fetch_values(self, id, *values):
        qs = self.filter(id=id).values(*values)

        if not qs:
            raise self.model.DoesNotExist("{}(id={}) does not exist.".format(self.model.__name__, id))

        return qs.first()

    def is_task_started(self, project_id, id):
        qs = self.filter(project_id=project_id, id=id).only("pipeline_instance")

        if not qs:
            raise self.model.DoesNotExist("{}(id={}) does not exist.".format(self.model.__name__, id))

        return qs.first().pipeline_instance.is_started


class TaskFlowInstance(models.Model):
    project = models.ForeignKey(Project, verbose_name=_("所属项目"), null=True, blank=True, on_delete=models.SET_NULL)
    pipeline_instance = models.ForeignKey(PipelineInstance, blank=True, null=True, on_delete=models.SET_NULL)
    category = models.CharField(_("任务类型，继承自模板"), choices=TASK_CATEGORY, max_length=255, default="Default")
    template_id = models.CharField(_("创建任务所用的模板ID"), max_length=255, blank=True)
    template_source = models.CharField(_("流程模板来源"), max_length=32, choices=TEMPLATE_SOURCE, default=PROJECT)
    create_method = models.CharField(_("创建方式"), max_length=30, choices=TASK_CREATE_METHOD, default="app")
    create_info = models.CharField(_("创建任务额外信息（App maker ID或APP CODE或周期任务ID）"), max_length=255, blank=True)
    flow_type = models.CharField(_("任务流程类型"), max_length=255, choices=TASK_FLOW_TYPE, default="common")
    current_flow = models.CharField(_("当前任务流程阶段"), max_length=255)
    is_deleted = models.BooleanField(_("是否删除"), default=False)
    engine_ver = models.IntegerField(_("引擎版本"), choices=EngineConfig.ENGINE_VER, default=1)

    objects = TaskFlowInstanceManager()

    def __unicode__(self):
        return "%s_%s" % (self.project, self.pipeline_instance.name)

    class Meta:
        verbose_name = _("流程实例 TaskFlowInstance")
        verbose_name_plural = _("流程实例 TaskFlowInstance")
        ordering = ["-id"]

    def delete(self, real_delete=False):
        if real_delete:
            super().delete()
        setattr(self, "is_deleted", True)
        self.save()

    @property
    def instance_id(self):
        return self.id

    @property
    def category_name(self):
        return self.get_category_display()

    @property
    def creator(self):
        return self.pipeline_instance.creator

    @property
    def creator_name(self):
        return convert_readable_username(self.creator)

    @property
    def executor(self):
        return self.pipeline_instance.executor

    @property
    def executor_name(self):
        return convert_readable_username(self.executor)

    @property
    def pipeline_tree(self):
        tree = self.pipeline_instance.execution_data
        # add nodes attr
        pipeline_web_clean = PipelineWebTreeCleaner(tree)
        nodes = NodeInInstance.objects.filter(instance_id=self.pipeline_instance.instance_id)
        nodes_attr = NodeAttr.get_nodes_attr(nodes, "instance")
        pipeline_web_clean.to_web(nodes_attr, with_subprocess=True)
        return tree

    @property
    def is_expired(self):
        return self.pipeline_instance.is_expired

    @property
    def name(self):
        return self.pipeline_instance.name

    @property
    def create_time(self):
        return self.pipeline_instance.create_time

    @property
    def start_time(self):
        return self.pipeline_instance.start_time

    @property
    def finish_time(self):
        return self.pipeline_instance.finish_time

    @property
    def is_started(self):
        return self.pipeline_instance.is_started

    @property
    def is_finished(self):
        return self.pipeline_instance.is_finished

    @property
    def is_revoked(self):
        return self.pipeline_instance.is_revoked

    @property
    def elapsed_time(self):
        return self.pipeline_instance.elapsed_time

    @property
    def template(self):
        if self.template_source == ONETIME:
            return None
        elif self.template_source in NON_COMMON_TEMPLATE_TYPES:
            return TaskTemplate.objects.get(pk=self.template_id)
        else:
            return CommonTemplate.objects.get(pk=self.template_id)

    @property
    def executor_proxy(self):
        if self.template_source not in NON_COMMON_TEMPLATE_TYPES:
            return None
        return TaskTemplate.objects.filter(id=self.template_id).values_list("executor_proxy", flat=True).first()

    @property
    def url(self):
        return self.__class__.task_url(project_id=self.project_id, task_id=self.id)

    @property
    def subprocess_info(self):
        return self.pipeline_instance.template.subprocess_version_info if self.template else {}

    @property
    def is_manual_intervention_required(self):
        """判断当前任务是否需要人工干预

        :return: 是否需要人工干预
        :rtype: boolean
        """
        if not self.is_started:
            return False

        dispatcher = TaskCommandDispatcher(
            engine_ver=self.engine_ver,
            taskflow_id=self.id,
            pipeline_instance=self.pipeline_instance,
            project_id=self.project_id,
        )
        task_result = dispatcher.get_task_status()
        if not task_result["result"]:
            raise ValueError("dispatcher.get_task_status fail: {}".format(task_result["message"]))
        status_tree = task_result["data"]

        # judge root status
        if status_tree["state"] in MANUAL_INTERVENTION_EXEMPT_STATES:
            return False

        # collect children status
        state_nodes_map = {}
        state_nodes_map[status_tree["state"]] = {status_tree["id"]}

        def _collect_child_states(children_states):
            if not children_states:
                return

            for child in children_states.values():
                state_nodes_map.setdefault(child["state"], set()).add(child["id"])
                _collect_child_states(child.get("children"))

        _collect_child_states(status_tree["children"])

        # first check, found obvious manual intervention required states
        if MANUAL_INTERVENTION_REQUIRED_STATES.intersection(state_nodes_map.keys()):
            return True

        # without running nodes
        if states.RUNNING not in state_nodes_map:
            return False

        # check running nodes
        manual_intervention_nodes = set()

        def _collect_manual_intervention_nodes(pipeline_tree):
            for act in pipeline_tree["activities"].values():
                if act["type"] == "SubProcess":
                    _collect_manual_intervention_nodes(act["pipeline"])
                elif act["component"]["code"] in MANUAL_INTERVENTION_COMP_CODES:
                    manual_intervention_nodes.add(act["id"])

        _collect_manual_intervention_nodes(self.pipeline_instance.execution_data)

        # has running manual intervention nodes
        if manual_intervention_nodes.intersection(state_nodes_map[states.RUNNING]):
            return True

        return False

    @property
    def function_task_claimant(self):
        """
        获取当前任务实例的职能化认领单的认领人
        """
        # 如果任务流程类型不是职能化任务流程，直接返回
        if self.flow_type != "common_func":
            return None

        # 如果是职能化任务流程，返回对应的职能化认领单实例
        return self.function_task.filter(task=self).values_list("claimant", flat=True).first()

    @classmethod
    def task_url(cls, project_id, task_id):
        return "%staskflow/execute/%s/?instance_id=%s" % (settings.APP_HOST, project_id, task_id)

    def get_node_data(self, node_id, username, component_code=None, subprocess_stack=None, loop=None):
        if not self.has_node(node_id):
            message = "node[node_id={node_id}] not found in task[task_id={task_id}]".format(
                node_id=node_id, task_id=self.id
            )
            return {"result": False, "message": message, "data": {}, "code": err_code.REQUEST_PARAM_INVALID.code}

        dispatcher = NodeCommandDispatcher(engine_ver=self.engine_ver, node_id=node_id, taskflow_id=self.id)
        return dispatcher.get_node_data(
            username=username,
            component_code=component_code,
            loop=loop,
            pipeline_instance=self.pipeline_instance,
            subprocess_stack=subprocess_stack or [],
            project_id=self.project_id,
        )

    def get_node_detail(
        self, node_id, username, component_code=None, subprocess_stack=None, loop=None, include_data=True, **kwargs
    ):
        if not self.has_node(node_id):
            message = "node[node_id={node_id}] not found in task[task_id={task_id}]".format(
                node_id=node_id, task_id=self.id
            )
            return {"result": False, "message": message, "data": {}, "code": err_code.REQUEST_PARAM_INVALID.code}

        dispatcher = NodeCommandDispatcher(engine_ver=self.engine_ver, node_id=node_id, taskflow_id=self.id)

        node_data = {}
        if include_data:
            node_data_result = dispatcher.get_node_data(
                username=username,
                component_code=component_code,
                loop=loop,
                pipeline_instance=self.pipeline_instance,
                subprocess_stack=subprocess_stack,
                project_id=kwargs["project_id"],
            )
            if not node_data_result["result"]:
                return node_data_result
            node_data = node_data_result["data"]

        node_detail_result = dispatcher.get_node_detail(
            username=username,
            component_code=component_code,
            loop=loop,
            pipeline_instance=self.pipeline_instance,
            subprocess_stack=subprocess_stack,
        )
        if not node_detail_result["result"]:
            return node_detail_result

        detail = node_detail_result["data"]
        detail.update(node_data)

        return {"result": True, "data": detail, "message": "", "code": err_code.SUCCESS.code}

    def task_claim(self, username, constants, name):
        if self.flow_type != "common_func":
            return {"result": False, "message": "task is not functional"}
        elif self.current_flow != "func_claim":
            return {"result": False, "message": "task with current_flow:%s cannot be claimed" % self.current_flow}

        with transaction.atomic():
            if name:
                self.pipeline_instance.name = name
            self.set_task_context(constants)
            result = self.function_task.get(task=self).claim_task(username)
            if result["result"]:
                self.current_flow = "execute_task"
                self.pipeline_instance.save()
                self.save()

        return result

    def _get_task_celery_queue(self, engine_ver):
        queue = ""
        if engine_ver == EngineConfig.ENGINE_VER_V1 and self.create_method == "api":
            queue = settings.API_TASK_QUEUE_NAME
        elif engine_ver == EngineConfig.ENGINE_VER_V2 and self.create_method == "api":
            queue = settings.API_TASK_QUEUE_NAME_V2
        return queue

    def task_action(self, action, username):
        if self.current_flow != "execute_task":
            return {
                "result": False,
                "message": "task with current_flow:%s cannot be %sed" % (self.current_flow, action),
                "code": err_code.INVALID_OPERATION.code,
            }

        dispatcher = TaskCommandDispatcher(
            engine_ver=self.engine_ver,
            taskflow_id=self.id,
            pipeline_instance=self.pipeline_instance,
            project_id=self.project_id,
            queue=self._get_task_celery_queue(self.engine_ver),
        )

        try:
            return dispatcher.dispatch(action, username)
        except Exception as e:
            message = "task[id=%s] action failed:%s" % (self.id, e)
            logger.exception(traceback.format_exc())
            return {"result": False, "message": message, "code": err_code.UNKNOWN_ERROR.code}

    def nodes_action(self, action, node_id, username, **kwargs):
        if not self.has_node(node_id):
            message = "node[node_id={node_id}] not found in task[task_id={task_id}]".format(
                node_id=node_id, task_id=self.id
            )
            return {"result": False, "message": message, "code": err_code.REQUEST_PARAM_INVALID.code}

        dispatcher = NodeCommandDispatcher(engine_ver=self.engine_ver, node_id=node_id, taskflow_id=self.id)

        try:
            return dispatcher.dispatch(action, username, **kwargs)
        except Exception as e:
            message = "task[id=%s] node[id=%s] action failed: %s" % (self.id, node_id, e)
            logger.exception(traceback.format_exc())
            return {"result": False, "message": message, "code": err_code.UNKNOWN_ERROR.code}

    def clone(self, username, **kwargs):
        clone_pipeline = self.pipeline_instance.clone(username, **kwargs)
        self.pk = None
        self.pipeline_instance = clone_pipeline
        if "create_method" in kwargs:
            self.create_method = kwargs["create_method"]
            self.create_info = kwargs.get("create_info", "")
        if self.flow_type == "common_func":
            self.current_flow = "func_claim"
        else:
            self.current_flow = "execute_task"
        self.is_deleted = False
        self.save()
        return self

    def set_task_context(self, constants):
        dispatcher = TaskCommandDispatcher(
            engine_ver=self.engine_ver,
            taskflow_id=self.id,
            pipeline_instance=self.pipeline_instance,
            project_id=self.project_id,
        )
        return dispatcher.set_task_context(
            task_is_started=self.pipeline_instance.is_started,
            task_is_finished=self.pipeline_instance.is_finished,
            context=constants,
        )

    def spec_nodes_timer_reset(self, node_id, username, inputs):
        if not self.has_node(node_id):
            message = "node[node_id={node_id}] not found in task[task_id={task_id}]".format(
                node_id=node_id, task_id=self.id
            )
            return {"result": False, "message": message, "code": err_code.REQUEST_PARAM_INVALID.code}

        dispatcher = NodeCommandDispatcher(engine_ver=self.engine_ver, node_id=node_id, taskflow_id=self.id)

        action_result = dispatcher.dispatch(command="forced_fail", operator=username)
        if not action_result["result"]:
            return action_result

        action_result = dispatcher.dispatch(command="retry", operator=username, inputs=inputs)
        if not action_result["result"]:
            return action_result

        return action_result

    def get_act_web_info(self, act_id):
        def get_act_of_pipeline(pipeline_tree):
            for node_id, node_info in list(pipeline_tree["activities"].items()):
                if node_id == act_id:
                    return node_info
                elif node_info["type"] == "SubProcess":
                    act = get_act_of_pipeline(node_info["pipeline"])
                    if act:
                        return act

        return get_act_of_pipeline(self.pipeline_tree)

    def has_node(self, node_id):
        return node_id in self.pipeline_instance.node_id_set

    def get_task_detail(self):
        data = {
            "id": self.id,
            "project_id": int(self.project.id),
            "project_name": self.project.name,
            "name": self.name,
            "create_time": format_datetime(self.create_time),
            "creator": self.creator,
            "create_method": self.create_method,
            "template_id": int(self.template_id),
            "start_time": format_datetime(self.start_time),
            "finish_time": format_datetime(self.finish_time),
            "executor": self.executor,
            "elapsed_time": self.elapsed_time,
            "pipeline_tree": self.pipeline_tree,
            "task_url": self.url,
        }
        exec_data = self.pipeline_instance.execution_data
        # inputs data
        constants = exec_data["constants"]
        data["constants"] = constants
        # outputs data, if task has not executed, outputs is empty list
        instance_id = self.pipeline_instance.instance_id

        dispatcher = NodeCommandDispatcher(engine_ver=self.engine_ver, node_id=instance_id)
        outputs_result = dispatcher.get_outputs()
        if not outputs_result["result"]:
            logger.error("dispatcher.get_outputs failed: {}".format(outputs_result["message"]))
        outputs = outputs_result["data"]

        if self.engine_ver == EngineConfig.ENGINE_VER_V1:
            outputs_table = [{"key": key, "value": val} for key, val in outputs.get("outputs", {}).items()]
        else:
            outputs_table = [{"key": key, "value": val} for key, val in outputs.items()]

        for out in outputs_table:
            out["name"] = constants[out["key"]]["name"]
        data.update({"outputs": outputs_table, "ex_data": outputs.get("ex_data", "")})

        return data

    def callback(self, node_id, data, version=""):
        if not self.has_node(node_id):
            return {
                "result": False,
                "message": "task[{tid}] does not have node[{nid}]".format(tid=self.id, nid=node_id),
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }

        dispatcher = NodeCommandDispatcher(engine_ver=self.engine_ver, node_id=node_id, taskflow_id=self.id)
        return dispatcher.dispatch(command="callback", operator="", data=data, version=version)

    def get_stakeholders(self):
        notify_receivers = json.loads(self.template.notify_receivers)
        receiver_group = notify_receivers.get("receiver_group", [])
        receivers = [self.executor]

        if self.project.from_cmdb:
            cc_group_members = get_business_group_members(self.project.bk_biz_id, receiver_group)
            receivers.extend(cc_group_members)

        members = list(
            StaffGroupSet.objects.filter(
                project_id=self.project.id,
                is_deleted=False,
                id__in=[group for group in receiver_group if isinstance(group, int)],
            ).values_list("members", flat=True)
        )
        if members:
            members = ",".join(members).split(",")
            receivers.extend(members)

        # 如果职能化单认领人存在，则通知上加上认领人
        if self.function_task_claimant:
            receivers.append(self.function_task_claimant)

        receiver_set = set(receivers)
        receiver_set.discard(self.executor)
        # 这里保证执行人在列表第一位，且名单中通知人唯一，其他接收人不保证顺序
        return sorted(set(receivers), key=receivers.index)

    def get_notify_type(self):
        notify_type = json.loads(self.template.notify_type)
        return notify_type if isinstance(notify_type, dict) else {"success": notify_type, "fail": notify_type}


def get_instance_context(pipeline_instance, data_type, username=""):
    try:
        taskflow = TaskFlowInstance.objects.get(pipeline_instance=pipeline_instance)
    except TaskFlowInstance.DoesNotExist:
        logger.warning("TaskFlowInstance does not exist: pipeline_template.id=%s" % pipeline_instance.pk)
        return {}
    # pipeline的root_pipeline_params数据，最终会传给插件的parent_data，是简单地字典格式
    if data_type == "data":
        return TaskContext(taskflow, username).__dict__
    # pipeline的root_pipeline_context数据，可以直接在参数中引用，如 ${_system.biz_cc_id}
    else:
        context = TaskContext(taskflow, username).context()
        # 注入业务级别变量
        context.update(
            {
                key: {"type": "plain", "is_param": True, "value": value}
                for key, value in get_project_constants_context(taskflow.project_id).items()
            }
        )
        return context


class TaskOperationTimesConfig(models.Model):
    project_id = models.IntegerField(_("项目 ID"))
    operation = models.CharField(
        _("任务操作"),
        choices=(("start", _("启动")), ("pause", _("暂停")), ("resume", _("恢复")), ("revoke", _("撤销"))),
        max_length=64,
    )
    times = models.IntegerField(_("限制操作次数"))
    time_unit = models.CharField(_("限制时间单位"), choices=(("m", "分钟"), ("h", "小时"), ("d", "天")), max_length=10)

    class Meta:
        verbose_name = _("任务操作次数限制配置 TaskOperationTimesConfig")
        verbose_name_plural = _("任务操作次数限制配置 TaskOperationTimesConfig")
        unique_together = ("project_id", "operation")


class AutoRetryNodeStrategy(models.Model):
    taskflow_id = models.BigIntegerField(verbose_name="taskflow id")
    root_pipeline_id = models.CharField(verbose_name="root pipeline id", max_length=64)
    node_id = models.CharField(verbose_name="task node id", max_length=64, primary_key=True)
    retry_times = models.IntegerField(verbose_name="retry times", default=0)
    max_retry_times = models.IntegerField(verbose_name="retry times", default=5)
    interval = models.IntegerField(verbose_name="retry interval", default=0)

    class Meta:
        verbose_name = _("节点自动重试策略 AutoRetryNodeStrategy")
        verbose_name_plural = _("节点自动重试策略 AutoRetryNodeStrategy")
        index_together = [("root_pipeline_id", "node_id")]


class TimeoutNodeConfigManager(models.Manager):
    def batch_create_node_timeout_config(self, taskflow_id: int, root_pipeline_id: str, pipeline_tree: dict):
        """批量创建节点超时配置"""

        config_parse_result = parse_node_timeout_configs(pipeline_tree)
        # 这里忽略解析失败的情况，保证即使解析失败也能正常创建任务
        if not config_parse_result["result"]:
            logger.error(
                f'[batch_create_node_timeout_config] parse node timeout config failed: {config_parse_result["result"]}'
            )
            return
        configs = config_parse_result["data"] or []
        config_objs = [
            TimeoutNodeConfig(
                task_id=taskflow_id,
                action=config["action"],
                root_pipeline_id=root_pipeline_id,
                node_id=config["node_id"],
                timeout=config["timeout"],
            )
            for config in configs
        ]
        self.bulk_create(config_objs, batch_size=TASKFLOW_NODE_TIMEOUT_CONFIG_BATCH_CREAT_COUNT)


class TimeoutNodeConfig(models.Model):
    ACTION_TYPE = (("forced_fail", _("强制失败")), ("forced_fail_and_skip", _("强制失败并跳过")))
    task_id = models.BigIntegerField(verbose_name="taskflow id")
    root_pipeline_id = models.CharField(verbose_name="root pipeline id", max_length=64)
    action = models.CharField(verbose_name="action", choices=ACTION_TYPE, max_length=32)
    node_id = models.CharField(verbose_name="task node id", max_length=64, primary_key=True)
    timeout = models.IntegerField(verbose_name="node timeout time")

    objects = TimeoutNodeConfigManager()

    class Meta:
        verbose_name = _("节点超时配置 TimeoutNodeConfig")
        verbose_name_plural = _("节点超时配置 TimeoutNodeConfig")
        index_together = [("root_pipeline_id", "node_id")]


class TimeoutNodesRecord(models.Model):
    id = models.BigAutoField(verbose_name="ID", primary_key=True)
    timeout_nodes = models.TextField(verbose_name="超时节点信息")

    class Meta:
        verbose_name = _("超时节点数据记录 TimeoutNodesRecord")
        verbose_name_plural = _("超时节点数据记录 TimeoutNodesRecord")
