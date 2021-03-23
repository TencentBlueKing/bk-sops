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

from django.db import connection
from django.db.models import Count, Avg
from django.utils.translation import ugettext_lazy as _

from blueapps.utils.managermixins import ClassificationCountMixin
from pipeline.component_framework.models import ComponentModel
from pipeline.contrib.statistics.models import ComponentExecuteData
from gcloud.core.models import Project
from gcloud.core.constant import TASK_CATEGORY
from gcloud.utils.dates import timestamp_to_datetime, format_datetime
from gcloud.contrib.appmaker.models import AppMaker

logger = logging.getLogger("root")


class TaskFlowStatisticsMixin(ClassificationCountMixin):

    GB_INSTANCE_NODE_ORDER_PARAMS = {
        "-instanceId": ("T.id", "DESC"),
        "-atomTotal": ("I.atom_total", "DESC"),
        "-subprocessTotal": ("I.subprocess_total", "DESC"),
        "-gatewaysTotal": ("I.gateways_total", "DESC"),
        "-elapsedTime": ("elapsed_time", "DESC"),
        "instanceId": ("T.id", "ASC"),
        "atomTotal": ("I.atom_total", "ASC"),
        "subprocessTotal": ("I.subprocess_total", "ASC"),
        "gatewaysTotal": ("I.gateways_total", "ASC"),
        "elapsedTime": ("elapsed_time", "ASC"),
    }

    GB_INSTANCE_TIME_GROUP_PARAMS = {"day": "DATE(create_time)", "month": "YEAR(create_time), MONTH(create_time)"}

    TASK_CATEGORY_DICT = dict(TASK_CATEGORY)

    def _assemble_where_statement(self, filters):
        category = filters.get("category")
        project_id = filters.get("project_id")

        conditions = []
        if category is not None:
            conditions.append(
                '`category` = "%s"' % (category if category in self.TASK_CATEGORY_DICT else TASK_CATEGORY[-1][0])
            )

        if project_id:
            conditions.append("`project_id` = %s" % int(project_id))

        if conditions:
            return " WHERE %s" % (" AND ".join(conditions))
        else:
            return ""

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
        component_dict = ComponentModel.objects.get_component_dict()
        component_list = ComponentModel.objects.filter(status=True).values("code")

        instance_id_list = taskflow.values_list("pipeline_instance__instance_id")
        # 获得标准插件
        component = ComponentExecuteData.objects.filter(instance_id__in=instance_id_list)
        component_data = (
            component.values("component_code")
            .annotate(execute_times=Count("component_code"))
            .order_by("component_code")
        )
        total = component_list.count()
        execute_data = {}
        for component in component_data:
            value = component["execute_times"]
            execute_data[component["component_code"]] = value

        groups = []
        # todo 多版本插件先聚合到一起显示，暂不分开
        processed_components = set()
        for data in component_list:
            code = data.get("code")

            if code in processed_components:
                continue

            processed_components.add(code)
            groups.append({"code": code, "name": component_dict.get(code, None), "value": execute_data.get(code, 0)})
        return total, groups

    def group_by_atom_execute_fail_times(self, taskflow, *args):
        # 查询各标准插件失败次数
        component_dict = ComponentModel.objects.get_component_dict()
        component_list = ComponentModel.objects.filter(status=True).values("code")

        instance_id_list = taskflow.values_list("pipeline_instance__instance_id")
        # 获得标准插件
        component_data = ComponentExecuteData.objects.filter(instance_id__in=instance_id_list)
        component_failed_data = (
            component_data.filter(status=False)
            .values("component_code")
            .annotate(failed_times=Count("component_code"))
            .order_by("component_code")
        )
        failed_dict = {item["component_code"]: item["failed_times"] for item in component_failed_data}

        groups = []
        # todo 多版本插件先聚合到一起显示，暂不分开
        processed_components = set()
        for data in component_list:
            code = data.get("code")

            if code in processed_components:
                continue
            processed_components.add(code)

            groups.append({"code": code, "name": component_dict.get(code, None), "value": failed_dict.get(code, 0)})
        return component_list.count(), groups

    def group_by_atom_avg_execute_time(self, taskflow, *args):
        # 查询各标准插件被执行次数
        # 获得标准插件dict列表
        component_dict = ComponentModel.objects.get_component_dict()
        component_list = ComponentModel.objects.filter(status=True).values("code")

        instance_id_list = taskflow.values_list("pipeline_instance__instance_id")
        # 获得标准插件
        component = ComponentExecuteData.objects.filter(instance_id__in=instance_id_list)
        component_data = (
            component.values("component_code").annotate(avg_execute_time=Avg("elapsed_time")).order_by("component_code")
        )
        total = component_list.count()
        execute_data = {}
        for component in component_data:
            value = component["avg_execute_time"]
            execute_data[component["component_code"]] = value

        groups = []
        # todo 多版本插件先聚合到一起显示，暂不分开
        processed_components = set()
        for data in component_list:
            code = data.get("code")

            if code in processed_components:
                continue
            processed_components.add(code)

            groups.append({"code": code, "name": component_dict.get(code, None), "value": execute_data.get(code, 0)})
        return total, groups

    def group_by_atom_fail_percent(self, taskflow, *args):
        # 查询各标准插件重试次数
        component_dict = ComponentModel.objects.get_component_dict()
        component_list = ComponentModel.objects.filter(status=True).values("code")
        total = component_list.count()

        instance_id_list = taskflow.values_list("pipeline_instance__instance_id")
        # 获得标准插件
        component = ComponentExecuteData.objects.filter(instance_id__in=instance_id_list)
        component_data = (
            component.values("component_code")
            .annotate(execute_times=Count("component_code"))
            .order_by("component_code")
        )
        component_failed_data = (
            component_data.filter(status=False)
            .values("component_code")
            .annotate(failed_times=Count("component_code"))
            .order_by("component_code")
        )
        failed_dict = {item["component_code"]: item["failed_times"] for item in component_failed_data}
        fail_percent = {}
        for component in component_data:
            component_code = component["component_code"]
            if component_code in failed_dict:
                execute_times = component["execute_times"]
                fail_percent[component_code] = "%.2f" % ((failed_dict[component_code] * 1.00 / execute_times) * 100)

        groups = []
        # todo 多版本插件先聚合到一起显示，暂不分开
        processed_components = set()
        for data in component_list:
            code = data.get("code")

            if code in processed_components:
                continue
            processed_components.add(code)

            groups.append({"code": code, "name": component_dict.get(code, None), "value": fail_percent.get(code, 0)})
        return total, groups

    def group_by_atom_instance(self, taskflow, filters, page, limit):
        # 被引用的任务实例列表

        # 获得所有类型的dict列表
        category_dict = dict(TASK_CATEGORY)

        # 获得参数中的标准插件code
        component_code = filters.get("component_code")
        # 获取到组件code对应的instance_id_list
        instance_id_list = ComponentExecuteData.objects.filter(is_sub=False)
        # 对code进行二次查找
        if component_code:
            instance_id_list = (
                instance_id_list.filter(component_code=component_code).distinct().values_list("instance_id")
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

        statement = 'SELECT COUNT(*), `category` \
        FROM `taskflow3_taskflowinstance` T  INNER JOIN (\
            SELECT `id`\
            FROM `pipeline_pipelineinstance`\
            WHERE `create_time` >= "{create_time}" AND `create_time` < "{finish_time}"\
        ) P ON (`T`.`pipeline_instance_id` = `P`.`id`){where}\
        GROUP BY `T`.`category`;'.format(
            create_time=filters["create_time_datetime"],
            finish_time=filters["finish_time_datetime"],
            where=self._assemble_where_statement(filters),
        )

        with connection.cursor() as cursor:
            cursor.execute(statement)

            result = [
                {"code": row[1], "name": self.TASK_CATEGORY_DICT.get(row[1], row[1]), "value": row[0]}
                for row in cursor.fetchall()
            ]

        return 1, result

    def group_by_instance_node(self, taskflow, filters, page, limit):
        """
        @summary: 各任务实例执行的标准插件节点个数、子流程节点个数、网关节点数、执行耗时统计（支持排序）
        @param taskflow:
        @param filters:
        @param page:
        @param limit:
        @return:
        """
        order_by, order_method = self.GB_INSTANCE_NODE_ORDER_PARAMS.get(
            filters.get("order_by", "-instanceId"), self.GB_INSTANCE_NODE_ORDER_PARAMS["-instanceId"]
        )

        count_statement = 'SELECT COUNT(*)\
        FROM `taskflow3_taskflowinstance` T\
        INNER JOIN (SELECT `id` FROM `pipeline_pipelineinstance`\
        WHERE `create_time` >= "{create_time}" AND `create_time` < "{finish_time}") P\
        ON (`T`.`pipeline_instance_id` = `P`.`id`){where};'.format(
            create_time=filters["create_time_datetime"],
            finish_time=filters["finish_time_datetime"],
            where=self._assemble_where_statement(filters),
        )

        statement = 'SELECT T.id,\
        `name`,\
        `project_id`,\
        `category`,\
        `create_time`,\
        `creator`,\
        UNIX_TIMESTAMP(`finish_time`) - UNIX_TIMESTAMP(`start_time`) AS elapsed_time,\
        `atom_total`,\
        `subprocess_total`,\
        `gateways_total`\
        FROM `taskflow3_taskflowinstance` T INNER JOIN (\
            SELECT `id`, `instance_id`, `name`, `create_time`, `finish_time`, `start_time`, `creator`\
            FROM `pipeline_pipelineinstance`\
            WHERE `create_time` >= "{create_time}" AND `create_time` < "{finish_time}"\
        ) P ON (`T`.`pipeline_instance_id` = `P`.`id`)\
        INNER JOIN `statistics_instanceinpipeline` I ON (`I`.`instance_id` = `P`.`instance_id`){where}\
        ORDER BY {order_by} {order_method} LIMIT {start},{end};\
        '.format(
            create_time=filters["create_time_datetime"],
            finish_time=filters["finish_time_datetime"],
            order_by=order_by,
            order_method=order_method,
            start=int((page - 1) * limit),
            end=limit,
            where=self._assemble_where_statement(filters),
        )

        with connection.cursor() as cursor:
            cursor.execute(count_statement)
            count = cursor.fetchone()[0]
            if not count:
                return count, []

            cursor.execute(statement)
            projects = {p.id: p.name for p in Project.objects.all().only("id", "name")}
            result = [
                {
                    "instanceId": row[0],
                    "instanceName": row[1],
                    "projectId": row[2],
                    "projectName": projects.get(row[2], row[2]),
                    "category": self.TASK_CATEGORY_DICT.get(row[3], row[3]),
                    "createTime": row[4],
                    "creator": row[5],
                    "elapsedTime": row[6],
                    "atomTotal": row[7],
                    "subprocessTotal": row[8],
                    "gatewaysTotal": row[9],
                }
                for row in cursor.fetchall()
            ]

            return count, result

    def group_by_instance_time(self, taskflow, filters, page, limit):
        #  按起始时间、业务（可选）、类型（可选）、图表类型（日视图，月视图），查询每一天或每一月的执行数量
        default_group = self.GB_INSTANCE_TIME_GROUP_PARAMS["day"]
        group_type = filters.get("type", "day")

        statement = 'SELECT COUNT(*), {group_param}\
        FROM `taskflow3_taskflowinstance` T  INNER JOIN (\
            SELECT `id`, `create_time`\
            FROM `pipeline_pipelineinstance`\
            WHERE `create_time` >= "{create_time}" AND `create_time` < "{finish_time}"\
        ) P ON (`T`.`pipeline_instance_id` = `P`.`id`){where}\
        GROUP BY {group_param};'.format(
            create_time=filters["create_time_datetime"],
            finish_time=filters["finish_time_datetime"],
            where=self._assemble_where_statement(filters),
            group_param=self.GB_INSTANCE_TIME_GROUP_PARAMS.get(group_type, default_group),
        )

        result = []
        with connection.cursor() as cursor:
            cursor.execute(statement)

            if group_type == "day":
                result = [{"time": row[1], "value": row[0]} for row in cursor.fetchall()]
            elif group_type == "month":
                result = [{"time": "%s-%s" % (row[1], row[2]), "value": row[0]} for row in cursor.fetchall()]

        total = sum([i["value"] for i in result])

        return total, result

    def group_by_project_id(self, taskflow, filters, page, limit):
        # 查询不同业务对应的流程数
        statement = 'SELECT COUNT(*), `J`.`id`, `J`.`name` \
        FROM `taskflow3_taskflowinstance` T  INNER JOIN (\
            SELECT `id`\
            FROM `pipeline_pipelineinstance`\
            WHERE `create_time` >= "{create_time}" AND `create_time` < "{finish_time}"\
        ) P ON (`T`.`pipeline_instance_id` = `P`.`id`)\
        INNER JOIN `core_project` J ON (`T`.`project_id` = `J`.`id`){where}\
        GROUP BY `J`.`id`;'.format(
            create_time=filters["create_time_datetime"],
            finish_time=filters["finish_time_datetime"],
            where=self._assemble_where_statement(filters),
        )

        with connection.cursor() as cursor:
            cursor.execute(statement)

            result = [{"code": row[1], "name": row[2], "value": row[0]} for row in cursor.fetchall()]

        return 1, result

    def general_group_by(self, prefix_filters, group_by):
        try:
            total, groups = self.classified_count(prefix_filters, group_by)
        except Exception as e:
            message = "query_task_list params conditions[%s] have invalid key or value: %s" % (prefix_filters, e)
            return False, message, None, None
        return True, None, total, groups
