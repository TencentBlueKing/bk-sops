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

import datetime
import logging

from django.db.models import Count, Avg
from django.utils.translation import ugettext_lazy as _

from blueapps.utils.managermixins import ClassificationCountMixin
from pipeline.component_framework.models import ComponentModel
from pipeline.contrib.statistics.models import ComponentExecuteData, InstanceInPipeline
from pipeline.engine.utils import calculate_elapsed_time
from gcloud.core.constant import TASK_CATEGORY, AE
from gcloud.utils.dates import timestamp_to_datetime, format_datetime, gen_day_dates, get_month_dates
from gcloud.contrib.appmaker.models import AppMaker

logger = logging.getLogger("root")


class TaskFlowStatisticsMixin(ClassificationCountMixin):
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

    def group_by_project_id(self, taskflow, *args):
        # 查询不同业务对应的流程数
        total = taskflow.count()
        taskflow_list = taskflow.values(AE.project_id, AE.project__name).annotate(value=Count("project_id")).order_by()
        groups = []
        for data in taskflow_list:
            groups.append(
                {"code": data.get(AE.project_id), "name": data.get(AE.project__name), "value": data.get("value", 0)}
            )
        return total, groups

    def group_by_appmaker_instance(self, taskflow, filters, page, limit):
        # 查询不同轻应用对应的流程数

        # 获得所有类型的dict列表
        category_dict = dict(TASK_CATEGORY)

        taskflow_values = taskflow.values("create_info")
        order_by = filters.get("order_by", "-templateId")
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
                    "templateId": code,
                    "createTime": format_datetime(data.get("create_time")),
                    "editTime": format_datetime(data.get("edit_time")),
                    "creator": data.get("creator"),
                    "templateName": data.get("name"),
                    "projectId": data.get("project_id"),
                    "projectName": data.get("project__name"),
                    "category": category_dict[data.get("task_template__category")],
                    # 需要将 code 转为字符型
                    "instanceTotal": total_dict.get(str(appmaker_id), 0),
                    "appmakerId": data.get("id"),
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
        # 获得标准插件dict列表
        instance_id_list = taskflow.values_list("pipeline_instance__instance_id")
        # 获得标准插件
        component_data = (
            ComponentExecuteData.objects.filter(instance_id__in=instance_id_list)
            .values("component_code", "version")
            .annotate(execute_times=Count("*"))
            .order_by("component_code")
        )
        return ComponentModel.objects.get_component_dicts(component_data, "execute_times")

    def group_by_atom_execute_fail_times(self, taskflow, *args):
        # 查询各标准插件失败次数
        instance_id_list = taskflow.values_list("pipeline_instance__instance_id")
        # 获得标准插件
        component_failed_data = (
            ComponentExecuteData.objects.filter(instance_id__in=instance_id_list, status=False)
            .values("component_code", "version")
            .annotate(failed_times=Count("*"))
            .order_by("component_code")
        )
        return ComponentModel.objects.get_component_dicts(component_failed_data, "failed_times")

    def group_by_atom_avg_execute_time(self, taskflow, *args):
        # 查询各标准插件被执行次数
        # 获得标准插件dict列表
        instance_id_list = taskflow.values_list("pipeline_instance__instance_id")
        # 获得标准插件
        component_data = (
            ComponentExecuteData.objects.filter(instance_id__in=instance_id_list)
            .values("component_code", "version")
            .annotate(avg_execute_time=Avg("elapsed_time"))
            .order_by("component_code")
        )

        return ComponentModel.objects.get_component_dicts(component_data, "avg_execute_time")

    def group_by_atom_fail_percent(self, taskflow, *args):
        # 查询各标准插件重试次数
        instance_id_list = taskflow.values_list("pipeline_instance__instance_id")
        # 获得标准插件
        component_data = (
            ComponentExecuteData.objects.filter(instance_id__in=instance_id_list)
            .values("component_code", "version")
            .annotate(execute_times=Count("*"))
            .order_by("component_code")
        )
        component_failed_data = (
            component_data.filter(status=False)
            .values("component_code", "version")
            .annotate(failed_times=Count("*"))
            .order_by("component_code")
        )
        failed_dict = {
            "{}-{}".format(item["component_code"], item["version"]): item["failed_times"]
            for item in component_failed_data
        }
        fail_percent = []
        for component in component_data:
            component_code = "{}-{}".format(component["component_code"], component["version"])
            if component_code in failed_dict:
                execute_times = component["execute_times"]
                fail_percent.append(
                    {
                        "component_code": component["component_code"],
                        "version": component["version"],
                        "fail_percent": "%.2f" % ((failed_dict[component_code] * 1.00 / execute_times) * 100),
                    }
                )

        return ComponentModel.objects.get_component_dicts(fail_percent, "fail_percent")

    def group_by_atom_instance(self, taskflow, filters, page, limit):
        # 被引用的任务实例列表

        # 获得所有类型的dict列表
        category_dict = dict(TASK_CATEGORY)

        # 获得参数中的标准插件code
        component_code = filters.get("component_code")
        version = filters.get("version")
        # 获取到组件code对应的instance_id_list
        instance_id_list = ComponentExecuteData.objects.filter(is_sub=False)
        # 对code进行二次查找
        if component_code:
            instance_id_list = instance_id_list.filter(component_code=component_code, version=version).values_list(
                "instance_id"
            )
        else:
            instance_id_list = instance_id_list.values_list("instance_id")

        taskflow_list = taskflow.filter(pipeline_instance__instance_id__in=instance_id_list)
        # 获得总数
        total = taskflow_list.count()
        order_by = filters.get("order_by", "-templateId")
        if order_by == "-instanceId":
            taskflow_list = taskflow_list.order_by("-id")
        elif order_by == "instanceId":
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
                    "instanceId": data.get("id"),
                    "projectId": data.get("project_id"),
                    "projectName": data.get("project__name"),
                    "instanceName": data.get("pipeline_instance__name"),
                    "category": category_dict[data.get("category")],  # 需要将code转为名称
                    "createTime": format_datetime(data.get("pipeline_instance__create_time")),
                    "creator": data.get("pipeline_instance__creator"),
                }
            )
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
        total = taskflow.count()
        # 查询所有任务的统计数据
        instance_id_list = list(taskflow.values_list("pipeline_instance__instance_id", flat=True))
        instance_pipeline_data = InstanceInPipeline.objects.filter(instance_id__in=instance_id_list).values()
        instance_in_pipeline_dict = {}
        for instance in instance_pipeline_data:
            instance_in_pipeline_dict[instance["instance_id"]] = {
                "atomTotal": instance["atom_total"],
                "subprocessTotal": instance["subprocess_total"],
                "gatewaysTotal": instance["gateways_total"],
            }

        # 返回数据字段到相关数据库模型字段的映射表
        mapping = {
            "instanceId": "id",
            "instanceName": "pipeline_instance__name",
            "pipelineInstanceId": "pipeline_instance__instance_id",
            "projectId": "project__id",
            "projectName": "project__name",
            "categoryKey": "category",
            "createTime": "pipeline_instance__create_time",
            "creator": "pipeline_instance__creator",
            "startTime": "pipeline_instance__start_time",
            "finishTime": "pipeline_instance__finish_time",
        }
        tasks = taskflow.values(*list(mapping.values()))
        groups = []
        task_category = dict(TASK_CATEGORY)
        for task in tasks:
            item = {
                "instanceId": task[mapping["instanceId"]],
                "instanceName": task[mapping["instanceName"]],
                "projectId": task[mapping["projectId"]],
                "projectName": task[mapping["projectName"]],
                "category": task_category[task[mapping["categoryKey"]]],
                "createTime": format_datetime(
                    task[mapping["createTime"]],
                ),
                "creator": task[mapping["creator"]],
                "elapsedTime": calculate_elapsed_time(task[mapping["startTime"]], task[mapping["finishTime"]]),
                "atomTotal": 0,
                "subprocessTotal": 0,
                "gatewaysTotal": 0,
            }
            if task[mapping["pipelineInstanceId"]] in instance_in_pipeline_dict:
                item.update(instance_in_pipeline_dict[task[mapping["pipelineInstanceId"]]])
            groups.append(item)

        order_by = filters.get("order_by", "-instanceId")
        if order_by.startswith("-"):
            # 需要去除负号
            order_by = order_by[1:]
            groups = sorted(groups, key=lambda group: -group.get(order_by))
        else:
            groups = sorted(groups, key=lambda group: group.get(order_by))

        return total, groups[(page - 1) * limit : page * limit]

    def group_by_instance_time(self, taskflow, filters, *args):
        #  按起始时间、业务（可选）、类型（可选）、图表类型（日视图，月视图），查询每一天或每一月的执行数量
        instance_create_time_list = taskflow.values("pipeline_instance__create_time")
        total = instance_create_time_list.count()
        group_type = filters.get("type", "day")
        create_time = timestamp_to_datetime(filters["create_time"])
        end_time = timestamp_to_datetime(filters["finish_time"]) + datetime.timedelta(days=1)

        groups = []
        date_list = []
        for instance in instance_create_time_list:
            instance_time = instance["pipeline_instance__create_time"]
            date_key = ""
            # 添加在一个list中 之后使用count方法获取对应的数量
            if group_type == "day":
                date_key = instance_time.strftime("%Y-%m-%d")
            elif group_type == "month":
                date_key = instance_time.strftime("%Y-%m")
            date_list.append(date_key)
        if group_type == "day":
            #  日视图
            for d in gen_day_dates(create_time, (end_time - create_time).days + 1):
                date_key = d.strftime("%Y-%m-%d")
                groups.append({"time": date_key, "value": date_list.count(date_key)})
        elif group_type == "month":
            # 月视图
            # 直接拿到对应的（年-月），不需要在字符串拼接
            for date_key in get_month_dates(create_time, end_time):
                groups.append({"time": date_key, "value": date_list.count(date_key)})
        return total, groups

    def general_group_by(self, prefix_filters, group_by):
        try:
            total, groups = self.classified_count(prefix_filters, group_by)
        except Exception as e:
            message = "query_task_list params conditions[%s] have invalid key or value: %s" % (prefix_filters, e)
            return False, message, None, None
        return True, None, total, groups
