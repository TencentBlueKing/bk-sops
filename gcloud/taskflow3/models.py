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
from django.db.models import Count
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

from pipeline.core.constants import PE
from pipeline.component_framework.constant import ConstantPool
from pipeline.models import PipelineInstance
from pipeline.engine import states
from pipeline.validators.gateway import validate_gateways
from pipeline.validators.utils import format_node_io_to_list
from pipeline_web.core.abstract import NodeAttr
from pipeline.component_framework.models import ComponentModel
from pipeline.contrib.statistics.models import ComponentExecuteData

from pipeline_web.core.models import NodeInInstance
from pipeline_web.parser.clean import PipelineWebTreeCleaner
from pipeline_web.wrapper import PipelineTemplateWebWrapper

from gcloud import err_code
from gcloud.conf import settings
from gcloud.constants import TASK_FLOW_TYPE, TASK_CATEGORY
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

logger = logging.getLogger("root")

MANUAL_INTERVENTION_EXEMPT_STATES = frozenset([states.CREATED, states.FINISHED, states.REVOKED])

MANUAL_INTERVENTION_REQUIRED_STATES = frozenset([states.FAILED, states.SUSPENDED])

MANUAL_INTERVENTION_COMP_CODES = frozenset(["pause_node"])


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
        statement = 'SELECT COUNT(*),`component_code`, `version`\
        FROM `statistics_componentexecutedata` S\
        INNER JOIN (SELECT `instance_id`, `id` FROM `pipeline_pipelineinstance`\
        WHERE `create_time` >= "{create_time}" AND `create_time` < "{finish_time}") P\
        ON (`S`.`instance_id` = `P`.`instance_id`){filter_project}\
        GROUP BY `S`.`component_code`,`S`.`version`'.format(
            create_time=args[0]["create_time_datetime"],
            finish_time=args[0]["finish_time_datetime"],
            filter_project=self._filter_project(args[0]["project_id"]),
        )
        with connection.cursor() as cursor:
            cursor.execute(statement)
            return ComponentModel.objects.get_component_dicts(cursor.fetchall())

    def group_by_atom_execute_fail_times(self, taskflow, *args):
        # 查询各标准插件失败次数
        statement = 'SELECT COUNT(*),`component_code`, `version`\
        FROM `statistics_componentexecutedata` S\
        INNER JOIN (SELECT `instance_id`, `id` FROM `pipeline_pipelineinstance`\
        WHERE `create_time` >= "{create_time}" AND `create_time` < "{finish_time}") P\
        ON (`S`.`instance_id` = `P`.`instance_id` AND `S`.`status` = FALSE ){filter_project}\
        GROUP BY `S`.`component_code`,`S`.`version`'.format(
            create_time=args[0]["create_time_datetime"],
            finish_time=args[0]["finish_time_datetime"],
            filter_project=self._filter_project(args[0]["project_id"]),
        )
        with connection.cursor() as cursor:
            cursor.execute(statement)
            return ComponentModel.objects.get_component_dicts(cursor.fetchall())

    def group_by_atom_avg_execute_time(self, taskflow, *args):
        # 查询各标准插件执行平均时间
        statement = 'SELECT ROUND(AVG(`elapsed_time`),2),`component_code`, `version`\
        FROM `statistics_componentexecutedata` S\
        INNER JOIN (SELECT `instance_id`, `id` FROM `pipeline_pipelineinstance`\
        WHERE `create_time` >= "{create_time}" AND `create_time` < "{finish_time}") P\
        ON (`S`.`instance_id` = `P`.`instance_id`){filter_project}\
        GROUP BY `S`.`component_code`,`S`.`version`'.format(
            create_time=args[0]["create_time_datetime"],
            finish_time=args[0]["finish_time_datetime"],
            filter_project=self._filter_project(args[0]["project_id"]),
        )
        with connection.cursor() as cursor:
            cursor.execute(statement)
            return ComponentModel.objects.get_component_dicts(cursor.fetchall())

    def group_by_atom_fail_percent(self, taskflow, *args):
        # 查询各标准插件执行失败率
        statement = 'SELECT ROUND(sum(if(status=0,1,0))/count(*)*100,2) fail_percent, `component_code`, `version`\
        FROM `statistics_componentexecutedata` S\
        INNER JOIN (SELECT `instance_id`, `id` FROM `pipeline_pipelineinstance`\
        WHERE `create_time` >= "{create_time}" AND `create_time` < "{finish_time}" AND `is_deleted` = FALSE) P\
        ON (`S`.`instance_id` = `P`.`instance_id`){filter_project}\
        GROUP BY `S`.`component_code`,`S`.`version` \
        HAVING sum(if(status=0,1,0))/count(*)*100 >0\
        ORDER BY fail_percent DESC'.format(
            create_time=args[0]["create_time_datetime"],
            finish_time=args[0]["finish_time_datetime"],
            filter_project=self._filter_project(args[0]["project_id"]),
        )

        with connection.cursor() as cursor:
            cursor.execute(statement)
            return ComponentModel.objects.get_component_dicts(cursor.fetchall())

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
        FROM `taskflow3_taskflowinstance` T INNER JOIN (\
            SELECT `id`, `instance_id`, `name`, `create_time`, `finish_time`, `start_time`, `creator`\
            FROM `pipeline_pipelineinstance`\
            WHERE `create_time` >= "{create_time}" AND `create_time` < "{finish_time}"\
        ) P ON (`T`.`pipeline_instance_id` = `P`.`id`)\
        INNER JOIN `statistics_instanceinpipeline` I ON (`I`.`instance_id` = `P`.`instance_id`){where};'.format(
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

        TaskFlowInstanceManager.preview_pipeline_tree_exclude_task_nodes(pipeline_tree, exclude_task_nodes_id)

        # change constants
        for key, constant in pipeline_tree[PE.constants].items():
            # set meta field for meta var, so frontend can render meta form
            if constant.get("is_meta"):
                constant["meta"] = deepcopy(constant)
                constant["value"] = constant["value"]["default"]
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

    @staticmethod
    def _replace_node_incoming(next_node, replaced_incoming, new_incoming):
        if isinstance(next_node[PE.incoming], list):
            next_node[PE.incoming].pop(next_node[PE.incoming].index(replaced_incoming))
            next_node[PE.incoming].extend(new_incoming)
        else:
            is_boring_list = isinstance(new_incoming, list) and len(new_incoming) == 1
            next_node[PE.incoming] = new_incoming[0] if is_boring_list else new_incoming

    @staticmethod
    def _ignore_act(act, locations, lines, pipeline_tree):

        # change next_node's incoming: task node、control node is different
        # change incoming_flow's target to next node
        # delete outgoing_flow
        incoming_id_list, outgoing_id = act[PE.incoming], act[PE.outgoing]
        incoming_id_list = incoming_id_list if isinstance(incoming_id_list, list) else [incoming_id_list]

        outgoing_flow = pipeline_tree[PE.flows][outgoing_id]
        target_id = outgoing_flow[PE.target]

        next_node = (
            pipeline_tree[PE.activities].get(target_id)
            or pipeline_tree[PE.gateways].get(target_id)
            or pipeline_tree[PE.end_event]
        )

        TaskFlowInstanceManager._replace_node_incoming(
            next_node=next_node, replaced_incoming=outgoing_id, new_incoming=incoming_id_list
        )

        for incoming_id in incoming_id_list:
            incoming_flow = pipeline_tree[PE.flows][incoming_id]
            incoming_flow[PE.target] = next_node["id"]

        pipeline_tree[PE.flows].pop(outgoing_id)

        # web location data
        try:
            locations.pop(act["id"])
            lines.pop(outgoing_id)

            for incoming_id in incoming_id_list:
                lines[incoming_id][PE.target]["id"] = next_node["id"]
        except Exception:
            logger.exception(
                "create_pipeline_instance_exclude_task_nodes adjust web data error: %s" % traceback.format_exc()
            )

    @staticmethod
    def _remove_useless_constants(exclude_task_nodes_id, pipeline_tree):
        # pop unreferenced constant
        data = {}
        for act_id, act in list(pipeline_tree[PE.activities].items()):
            if act["type"] == PE.ServiceActivity:
                node_data = {("%s_%s" % (act_id, key)): value for key, value in list(act["component"]["data"].items())}
            # PE.SubProcess
            else:
                node_data = {
                    ("%s_%s" % (act_id, key)): value
                    for key, value in list(act["constants"].items())
                    if value["show_type"] == "show"
                }
            data.update(node_data)

        for gw_id, gw in list(pipeline_tree[PE.gateways].items()):
            if gw["type"] in [PE.ExclusiveGateway, PE.ConditionalParallelGateway]:
                gw_data = {
                    ("%s_%s" % (gw_id, key)): {"value": value["evaluate"]}
                    for key, value in list(gw["conditions"].items())
                }
                data.update(gw_data)

        # get all referenced constants in flow
        constants = pipeline_tree[PE.constants]

        referenced_keys = []
        while True:
            last_count = len(referenced_keys)
            cons_pool = ConstantPool(data, lazy=True)
            refs = cons_pool.get_reference_info(strict=False)
            for keys in list(refs.values()):
                for key in keys:
                    # add outputs keys later
                    if key in constants and key not in referenced_keys:
                        referenced_keys.append(key)
                        data.update({key: constants[key]})
            if len(referenced_keys) == last_count:
                break

        # keep outputs constants
        outputs_keys = [key for key, value in list(constants.items()) if value["source_type"] == "component_outputs"]
        referenced_keys = list(set(referenced_keys + outputs_keys))
        pipeline_tree[PE.outputs] = [key for key in pipeline_tree[PE.outputs] if key in referenced_keys]

        # rebuild constants index
        referenced_keys.sort(key=lambda x: constants[x]["index"])
        new_constants = {}
        for index, key in enumerate(referenced_keys):
            value = constants[key]
            value["index"] = index
            # delete constant reference info to task node
            for act_id in exclude_task_nodes_id:
                if act_id in value["source_info"]:
                    value["source_info"].pop(act_id)
            new_constants[key] = value
        pipeline_tree[PE.constants] = new_constants

    @staticmethod
    def _try_to_ignore_parallel(parallel, converge_id, lines, locations, pipeline_tree):

        ignore_whole_parallel = True
        converge = pipeline_tree[PE.gateways][converge_id]
        parallel_outgoing = deepcopy(parallel[PE.outgoing])

        for outgoing_id in parallel_outgoing:
            # meet not converge node
            if pipeline_tree[PE.flows][outgoing_id][PE.target] != converge_id:
                ignore_whole_parallel = False
                continue

            # remove boring sequence
            converge[PE.incoming].remove(outgoing_id)
            parallel[PE.outgoing].remove(outgoing_id)
            pipeline_tree[PE.flows].pop(outgoing_id)
            lines.pop(outgoing_id)

        if not ignore_whole_parallel:
            return

        target_of_converge = pipeline_tree[PE.flows][converge[PE.outgoing]][PE.target]
        next_node_of_converge = (
            pipeline_tree[PE.activities].get(target_of_converge)
            or pipeline_tree[PE.gateways].get(target_of_converge)
            or pipeline_tree[PE.end_event]
        )

        # remove converge outgoing
        lines.pop(converge[PE.outgoing])
        pipeline_tree[PE.flows].pop(converge[PE.outgoing])

        # sequences not come from parallel to be removed
        new_incoming_list = []
        # redirect converge rerun incoming
        for incoming in converge[PE.incoming]:
            pipeline_tree[PE.flows][incoming][PE.target] = target_of_converge
            lines[incoming][PE.target]["id"] = target_of_converge
            new_incoming_list.append(incoming)

        # redirect parallel rerun incoming
        gateway_incoming = parallel[PE.incoming]
        gateway_incoming = gateway_incoming if isinstance(gateway_incoming, list) else [gateway_incoming]
        for incoming in gateway_incoming:
            pipeline_tree[PE.flows][incoming][PE.target] = target_of_converge
            lines[incoming][PE.target]["id"] = target_of_converge
            new_incoming_list.append(incoming)

        # process next node's incoming
        TaskFlowInstanceManager._replace_node_incoming(
            next_node=next_node_of_converge, replaced_incoming=converge[PE.outgoing], new_incoming=new_incoming_list
        )

        # remove parallel and converge
        pipeline_tree[PE.gateways].pop(parallel["id"])
        pipeline_tree[PE.gateways].pop(converge["id"])
        locations.pop(parallel["id"])
        locations.pop(converge["id"])

    @staticmethod
    def _remove_useless_parallel(pipeline_tree, lines, locations):
        copy_tree = deepcopy(pipeline_tree)

        for act in list(copy_tree["activities"].values()):
            format_node_io_to_list(act, o=False)

        for gateway in list(copy_tree["gateways"].values()):
            format_node_io_to_list(gateway, o=False)

        format_node_io_to_list(copy_tree["end_event"], o=False)

        converges = validate_gateways(copy_tree)

        while True:

            gateway_count = len(pipeline_tree[PE.gateways])

            for converge_id, converged_list in list(converges.items()):

                for converged in converged_list:

                    gateway = pipeline_tree[PE.gateways].get(converged)

                    if not gateway:  # had been removed
                        continue

                    is_parallel = gateway[PE.type] in {PE.ParallelGateway, PE.ConditionalParallelGateway}

                    # only process parallel gateway
                    if not is_parallel:
                        continue

                    TaskFlowInstanceManager._try_to_ignore_parallel(
                        parallel=gateway,
                        converge_id=converge_id,
                        lines=lines,
                        locations=locations,
                        pipeline_tree=pipeline_tree,
                    )

            if gateway_count == len(pipeline_tree[PE.gateways]):
                break

    @staticmethod
    def preview_pipeline_tree_exclude_task_nodes(pipeline_tree, exclude_task_nodes_id=None):
        if exclude_task_nodes_id is None:
            exclude_task_nodes_id = []

        locations = {item["id"]: item for item in pipeline_tree.get("location", [])}
        lines = {item["id"]: item for item in pipeline_tree.get("line", [])}

        for act_id in exclude_task_nodes_id:
            if act_id not in pipeline_tree[PE.activities]:
                error = "task node[id=%s] is not in template pipeline tree" % act_id
                raise Exception(error)

            act = pipeline_tree[PE.activities].pop(act_id)

            if not act["optional"]:
                error = "task node[id=%s] is not optional" % act_id
                raise Exception(error)

            TaskFlowInstanceManager._ignore_act(act=act, locations=locations, lines=lines, pipeline_tree=pipeline_tree)

        TaskFlowInstanceManager._remove_useless_parallel(pipeline_tree, lines, locations)

        pipeline_tree["line"] = list(lines.values())
        pipeline_tree["location"] = list(locations.values())

        TaskFlowInstanceManager._remove_useless_constants(
            exclude_task_nodes_id=exclude_task_nodes_id, pipeline_tree=pipeline_tree
        )

        return True

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

    @classmethod
    def task_url(cls, project_id, task_id):
        return "%staskflow/execute/%s/?instance_id=%s" % (settings.APP_HOST, project_id, task_id)

    def get_node_data(self, node_id, username, component_code=None, subprocess_stack=None, loop=None):
        if not self.has_node(node_id):
            message = "node[node_id={node_id}] not found in task[task_id={task_id}]".format(
                node_id=node_id, task_id=self.id
            )
            return {"result": False, "message": message, "data": {}, "code": err_code.INVALID_OPERATION.code}

        dispatcher = NodeCommandDispatcher(engine_ver=self.engine_ver, node_id=node_id)
        return dispatcher.get_node_data(
            username=username,
            component_code=component_code,
            loop=loop,
            pipeline_instance=self.pipeline_instance,
            subprocess_stack=subprocess_stack or [],
            project_id=self.project.id,
        )

    def get_node_detail(
        self, node_id, username, component_code=None, subprocess_stack=None, loop=None, include_data=True
    ):
        if not self.has_node(node_id):
            message = "node[node_id={node_id}] not found in task[task_id={task_id}]".format(
                node_id=node_id, task_id=self.id
            )
            return {"result": False, "message": message, "data": {}, "code": err_code.REQUEST_PARAM_INVALID.code}

        dispatcher = NodeCommandDispatcher(engine_ver=self.engine_ver, node_id=node_id)

        node_data = {}
        if include_data:
            node_data_result = dispatcher.get_node_data(
                username=username,
                component_code=component_code,
                loop=loop,
                pipeline_instance=self.pipeline_instance,
                subprocess_stack=subprocess_stack,
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
            return {"result": False, "message": message}

        dispatcher = NodeCommandDispatcher(engine_ver=self.engine_ver, node_id=node_id)

        try:
            return dispatcher.dispatch(action, username, **kwargs)
        except Exception as e:
            message = "task[id=%s] node[id=%s] action failed:%s" % (self.id, node_id, e)
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
        return self.pk

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
            return {"result": False, "message": message}

        dispatcher = NodeCommandDispatcher(engine_ver=self.engine_ver, node_id=node_id)

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

        outputs_table = [{"key": key, "value": val} for key, val in list(outputs.get("outputs", {}).items())]
        for out in outputs_table:
            out["name"] = constants[out["key"]]["name"]
        data.update({"outputs": outputs_table, "ex_data": outputs.get("ex_data", "")})

        return data

    def callback(self, act_id, data, version=""):
        if not self.has_node(act_id):
            return {
                "result": False,
                "message": "task[{tid}] does not have node[{nid}]".format(tid=self.id, nid=act_id),
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }

        dispatcher = NodeCommandDispatcher(engine_ver=self.engine_ver, node_id=act_id)
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

        return list(set(receivers))

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


def preview_template_tree(project_id, template_source, template_id, version, exclude_task_nodes_id):

    if template_source == PROJECT:
        template = TaskTemplate.objects.get(pk=template_id, is_deleted=False, project_id=project_id)
    else:
        template = CommonTemplate.objects.get(pk=template_id, is_deleted=False)
    pipeline_tree = template.get_pipeline_tree_by_version(version)
    template_constants = deepcopy(pipeline_tree["constants"])
    TaskFlowInstance.objects.preview_pipeline_tree_exclude_task_nodes(pipeline_tree, exclude_task_nodes_id)

    constants_not_referred = {
        key: value for key, value in list(template_constants.items()) if key not in pipeline_tree["constants"]
    }

    return {"pipeline_tree": pipeline_tree, "constants_not_referred": constants_not_referred}


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
