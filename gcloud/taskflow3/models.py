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

import re
import datetime
import json
import logging
import traceback
from copy import deepcopy

from django.db import models, transaction
from django.db.models import Count, Avg, Sum
from django.utils.translation import ugettext_lazy as _

from blueapps.utils import managermixins

from pipeline.core.constants import PE
from pipeline.component_framework import library
from pipeline.component_framework.constant import ConstantPool
from pipeline.models import PipelineInstance
from pipeline.engine import exceptions
from pipeline.engine import api as pipeline_api
from pipeline.engine.models import Data
from pipeline.utils.context import get_pipeline_context
from pipeline.engine import states
from pipeline.log.models import LogEntry
from pipeline.component_framework.models import ComponentModel
from pipeline.contrib.statistics.models import (
    ComponentExecuteData,
    InstanceInPipeline
)
from pipeline.exceptions import (
    ConvergeMatchError,
    ConnectionValidateError,
    IsolateNodeError,
    StreamValidateError
)
from pipeline.validators.gateway import validate_gateways
from pipeline_web.parser import WebPipelineAdapter
from pipeline_web.wrapper import PipelineTemplateWebWrapper
from pipeline_web.parser.format import format_node_io_to_list

from gcloud.conf import settings
from gcloud.contrib.appmaker.models import AppMaker
from gcloud.core.constant import TASK_FLOW_TYPE, TASK_CATEGORY, AE
from gcloud.core.models import Business
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.commons.template.models import replace_template_id, CommonTemplate, CommonTmplPerm
from gcloud.taskflow3.constants import (
    TASK_CREATE_METHOD,
    TEMPLATE_SOURCE,
)
from gcloud.core.utils import (
    convert_readable_username,
    strftime_with_timezone,
    timestamp_to_datetime,
    format_datetime,
    camel_case_to_underscore_naming,
    gen_day_dates,
    get_month_dates
)
from gcloud.taskflow3.signals import taskflow_started

logger = logging.getLogger("root")

PIPELINE_REGEX = re.compile(r'^name|create_time|creator|create_time|executor|'
                            r'start_time|finish_time|is_started|is_finished')

INSTANCE_ACTIONS = {
    'start': None,
    'pause': pipeline_api.pause_pipeline,
    'resume': pipeline_api.resume_pipeline,
    'revoke': pipeline_api.revoke_pipeline
}
NODE_ACTIONS = {
    'revoke': pipeline_api.resume_node_appointment,
    'retry': pipeline_api.retry_node,
    'skip': pipeline_api.skip_node,
    'callback': pipeline_api.activity_callback,
    'skip_exg': pipeline_api.skip_exclusive_gateway,
    'pause': pipeline_api.pause_node_appointment,
    'resume': pipeline_api.resume_node_appointment,
    'pause_subproc': pipeline_api.pause_pipeline,
    'resume_subproc': pipeline_api.resume_node_appointment,
}
GROUP_BY_DICT = {
    'instance_details': 'instance_details'
}


class TaskFlowInstanceManager(models.Manager, managermixins.ClassificationCountMixin):
    @staticmethod
    def create_pipeline_instance(template, **kwargs):
        pipeline_tree = kwargs['pipeline_tree']
        replace_template_id(template.__class__, pipeline_tree)
        pipeline_template_data = {
            'name': kwargs['name'],
            'creator': kwargs['creator'],
            'description': kwargs.get('description', ''),
        }

        PipelineTemplateWebWrapper.unfold_subprocess(pipeline_tree)

        pipeline_instance = PipelineInstance.objects.create_instance(
            template.pipeline_template,
            pipeline_tree,
            spread=True,
            **pipeline_template_data
        )
        return pipeline_instance

    @staticmethod
    def create_pipeline_instance_exclude_task_nodes(template, task_info, constants=None, exclude_task_nodes_id=None):
        """
        @param template:
        @param task_info: {
            'name': '',
            'creator': '',
            'description': '',
        }
        @param constants: 覆盖参数，如 {'${a}': '1', '${b}': 2}
        @param exclude_task_nodes_id: 取消执行的可选节点
        @return:
        """
        if constants is None:
            constants = {}
        pipeline_tree = template.pipeline_tree

        try:
            TaskFlowInstanceManager.preview_pipeline_tree_exclude_task_nodes(pipeline_tree, exclude_task_nodes_id)
        except Exception as e:
            return False, e.message

        # change constants
        for key, value in constants.items():
            if key in pipeline_tree[PE.constants]:
                pipeline_tree[PE.constants][key]['value'] = value

        task_info['pipeline_tree'] = pipeline_tree
        pipeline_inst = TaskFlowInstanceManager.create_pipeline_instance(template, **task_info)

        return True, pipeline_inst

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

        next_node = \
            pipeline_tree[PE.activities].get(target_id) or \
            pipeline_tree[PE.gateways].get(target_id) or \
            pipeline_tree[PE.end_event]

        TaskFlowInstanceManager._replace_node_incoming(next_node=next_node,
                                                       replaced_incoming=outgoing_id,
                                                       new_incoming=incoming_id_list)

        for incoming_id in incoming_id_list:
            incoming_flow = pipeline_tree[PE.flows][incoming_id]
            incoming_flow[PE.target] = next_node['id']

        pipeline_tree[PE.flows].pop(outgoing_id)

        # web location data
        try:
            locations.pop(act['id'])
            lines.pop(outgoing_id)

            for incoming_id in incoming_id_list:
                lines[incoming_id][PE.target]['id'] = next_node['id']
        except Exception as e:
            logger.exception('create_pipeline_instance_exclude_task_nodes adjust web data error:%s' % e)

    @staticmethod
    def _remove_useless_constants(exclude_task_nodes_id, pipeline_tree):
        # pop unreferenced constant
        data = {}
        for act_id, act in pipeline_tree[PE.activities].items():
            if act['type'] == PE.ServiceActivity:
                node_data = {('%s_%s' % (act_id, key)): value
                             for key, value in act['component']['data'].items()}
            # PE.SubProcess
            else:
                node_data = {('%s_%s' % (act_id, key)): value
                             for key, value in act['constants'].items() if value['show_type'] == 'show'}
            data.update(node_data)

        for gw_id, gw in pipeline_tree[PE.gateways].items():
            if gw['type'] == PE.ExclusiveGateway:
                gw_data = {('%s_%s' % (gw_id, key)): {'value': value['evaluate']}
                           for key, value in gw['conditions'].items()}
                data.update(gw_data)

        # get all referenced constants in flow
        constants = pipeline_tree[PE.constants]
        referenced_keys = []
        while True:
            last_count = len(referenced_keys)
            cons_pool = ConstantPool(data, lazy=True)
            refs = cons_pool.get_reference_info(strict=False)
            for keys in refs.values():
                for key in keys:
                    # ad d outputs keys later
                    if key in constants and key not in referenced_keys:
                        referenced_keys.append(key)
                        data.update({key: constants[key]})
            if len(referenced_keys) == last_count:
                break

        # keep outputs constants
        def is_outputs(value):
            check_type = value['source_type'] == 'component_outputs'
            if not check_type:
                return False
            return value['source_info'].keys()[0] not in exclude_task_nodes_id

        outputs_keys = [key for key, value in constants.items() if is_outputs(value)]
        referenced_keys = list(set(referenced_keys + outputs_keys))
        pipeline_tree[PE.outputs] = [key for key in pipeline_tree[PE.outputs] if key in referenced_keys]

        # rebuild constants index
        referenced_keys.sort(key=lambda x: constants[x]['index'])
        new_constants = {}
        for index, key in enumerate(referenced_keys):
            value = constants[key]
            value['index'] = index
            # delete constant reference info to task node
            for act_id in exclude_task_nodes_id:
                if act_id in value['source_info']:
                    value['source_info'].pop(act_id)
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
        next_node_of_converge = \
            pipeline_tree[PE.activities].get(target_of_converge) or \
            pipeline_tree[PE.gateways].get(target_of_converge) or \
            pipeline_tree[PE.end_event]

        # remove converge outgoing
        lines.pop(converge[PE.outgoing])
        pipeline_tree[PE.flows].pop(converge[PE.outgoing])

        # sequences not come from parallel to be removed
        new_incoming_list = []
        # redirect converge rerun incoming
        for incoming in converge[PE.incoming]:
            pipeline_tree[PE.flows][incoming][PE.target] = target_of_converge
            lines[incoming][PE.target]['id'] = target_of_converge
            new_incoming_list.append(incoming)

        # redirect parallel rerun incoming
        gateway_incoming = parallel[PE.incoming]
        gateway_incoming = gateway_incoming if isinstance(gateway_incoming, list) \
            else [gateway_incoming]
        for incoming in gateway_incoming:
            pipeline_tree[PE.flows][incoming][PE.target] = target_of_converge
            lines[incoming][PE.target]['id'] = target_of_converge
            new_incoming_list.append(incoming)

        # process next node's incoming
        TaskFlowInstanceManager._replace_node_incoming(next_node=next_node_of_converge,
                                                       replaced_incoming=converge[PE.outgoing],
                                                       new_incoming=new_incoming_list)

        # remove parallel and converge
        pipeline_tree[PE.gateways].pop(parallel['id'])
        pipeline_tree[PE.gateways].pop(converge['id'])
        locations.pop(parallel['id'])
        locations.pop(converge['id'])

    @staticmethod
    def _remove_useless_parallel(pipeline_tree, lines, locations):
        copy_tree = deepcopy(pipeline_tree)

        for act in copy_tree['activities'].values():
            format_node_io_to_list(act, o=False)

        for gateway in copy_tree['gateways'].values():
            format_node_io_to_list(gateway, o=False)

        format_node_io_to_list(copy_tree['end_event'], o=False)

        converges = validate_gateways(copy_tree)

        while True:

            gateway_count = len(pipeline_tree[PE.gateways])

            for converge_id, converged_list in converges.items():

                for converged in converged_list:

                    gateway = pipeline_tree[PE.gateways].get(converged)

                    if not gateway:  # had been removed
                        continue

                    is_parallel = gateway[PE.type] in {PE.ParallelGateway, PE.ConditionalParallelGateway}

                    # only process parallel gateway
                    if not is_parallel:
                        continue

                    TaskFlowInstanceManager._try_to_ignore_parallel(parallel=gateway,
                                                                    converge_id=converge_id,
                                                                    lines=lines,
                                                                    locations=locations,
                                                                    pipeline_tree=pipeline_tree)

            if gateway_count == len(pipeline_tree[PE.gateways]):
                break

    @staticmethod
    def preview_pipeline_tree_exclude_task_nodes(pipeline_tree, exclude_task_nodes_id=None):
        if exclude_task_nodes_id is None:
            exclude_task_nodes_id = []

        locations = {item['id']: item for item in pipeline_tree.get(PE.location, [])}
        lines = {item['id']: item for item in pipeline_tree.get(PE.line, [])}

        for act_id in exclude_task_nodes_id:
            if act_id not in pipeline_tree[PE.activities]:
                error = 'task node[id=%s] is not in template pipeline tree' % act_id
                raise Exception(error)

            act = pipeline_tree[PE.activities].pop(act_id)

            if not act['optional']:
                error = 'task node[id=%s] is not optional' % act_id
                raise Exception(error)

            TaskFlowInstanceManager._ignore_act(act=act,
                                                locations=locations,
                                                lines=lines,
                                                pipeline_tree=pipeline_tree)

        TaskFlowInstanceManager._remove_useless_parallel(pipeline_tree, lines, locations)

        pipeline_tree[PE.line] = lines.values()
        pipeline_tree[PE.location] = locations.values()

        TaskFlowInstanceManager._remove_useless_constants(exclude_task_nodes_id=exclude_task_nodes_id,
                                                          pipeline_tree=pipeline_tree)

        return True

    def extend_classified_count(self, group_by, filters=None, page=None, limit=None):
        """
        @summary: 兼容按照任务状态分类的扩展
        @param group_by:
        @param filters:
        @param page:
        @param limit:
        @return:
        """
        # 获得所有类型的dict列表
        category_dict = dict(TASK_CATEGORY)

        if filters is None:
            filters = {}
        prefix_filters = {}
        for cond, value in filters.items():
            # 如果conditions内容为空或为空字符，不可加入查询条件中
            if value in ['None', ''] or cond in ['component_code', 'order_by', 'type']:
                continue
            if PIPELINE_REGEX.match(cond):
                filter_cond = 'pipeline_instance__%s' % cond
                # 时间需要大于小于
                if cond == 'create_time':
                    filter_cond = '%s__gte' % filter_cond
                    prefix_filters.update({filter_cond: timestamp_to_datetime(value)})
                    continue
                # 结束时间由创建时间来决定
                if cond == 'finish_time':
                    filter_cond = 'pipeline_instance__create_time__lt'
                    prefix_filters.update(
                        {filter_cond: timestamp_to_datetime(value) + datetime.timedelta(days=1)})
                    continue
            else:
                filter_cond = cond
            prefix_filters.update({filter_cond: value})

        try:
            taskflow = self.filter(**prefix_filters)
        except Exception as e:
            message = u"query_task_list params conditions[%s] have invalid key or value: %s" % (filters, e)
            return False, message
        if group_by == AE.state:
            total = taskflow.count()
            groups = [
                {
                    'code': 'CREATED',
                    'name': _(u"未执行"),
                    'value': taskflow.filter(pipeline_instance__is_started=False).count()
                },
                {
                    'code': 'EXECUTING',
                    'name': _(u"执行中"),
                    'value': taskflow.filter(pipeline_instance__is_started=True,
                                             pipeline_instance__is_finished=False).count()
                },
                {
                    'code': 'FINISHED',
                    'name': _(u"已完成"),
                    'value': taskflow.filter(pipeline_instance__is_finished=True).count()
                }
            ]
        elif group_by == AE.business__cc_id:
            # 获取所有数据
            total = taskflow.count()
            taskflow_list = taskflow.values(AE.business__cc_id, AE.business__cc_name).annotate(
                value=Count(group_by)).order_by()
            groups = []
            for data in taskflow_list:
                groups.append({
                    'code': data.get(AE.business__cc_id),
                    'name': data.get(AE.business__cc_name),
                    'value': data.get('value', 0)
                })
        elif group_by == AE.appmaker_instance:
            taskflow_values = taskflow.values("create_info")
            order_by = filters.get("order_by", "-templateId")
            business_id = filters.get("business__cc_id", '')
            category = filters.get("category", '')
            started_time = timestamp_to_datetime(filters["create_time"])
            end_time = timestamp_to_datetime(filters["finish_time"]) + datetime.timedelta(days=1)
            appmaker_data = AppMaker.objects.filter(is_deleted=False,
                                                    create_time__gte=started_time,
                                                    create_time__lte=end_time)
            if business_id != '':
                appmaker_data = appmaker_data.filter(business__cc_id=business_id)
            if category != '':
                appmaker_data = appmaker_data.filter(task_template__category=category)
            # 获取所有轻应用数据数量
            total = appmaker_data.count()
            # 获得每一个轻应用的实例数量并变为 dict 字典数据进行查询
            total_dict = {
                appmaker['create_info']: appmaker['instance_total']
                for appmaker in taskflow_values.annotate(instance_total=Count("create_info")).order_by()
            }
            id_list = appmaker_data.values_list("id")[:]

            id_list = sorted(id_list,
                             key=lambda tuples_id: -total_dict.get(str(tuples_id[0]), 0))
            id_list = id_list[(page - 1) * limit: page * limit]
            app_id_list = [tuples[0] for tuples in id_list]
            # 获得轻应用对象对应的模板和轻应用名称
            appmaker_data = appmaker_data.filter(id__in=app_id_list).values(
                "id",
                "task_template_id",
                "name",
                "create_time",
                "edit_time",
                "editor",
                "business__cc_id",
                "business__cc_name",
                "task_template__category"
            )
            groups = []

            for data in appmaker_data:
                code = data.get('task_template_id')
                appmaker_id = data.get("id")
                groups.append({
                    'templateId': code,
                    'createTime': format_datetime(data.get('create_time')),
                    'editTime': format_datetime(data.get('edit_time')),
                    'editor': data.get('editor'),
                    'templateName': data.get('name'),
                    'businessId': data.get('business__cc_id'),
                    'businessName': data.get('business__cc_name'),
                    'category': category_dict[data.get('task_template__category')],
                    # 需要将 code 转为字符型
                    'instanceTotal': total_dict.get(str(appmaker_id), 0)
                })
            if order_by[0] == "-":
                # 需要去除负号
                order_by = order_by[1:]
                groups = sorted(groups, key=lambda group: -group.get(order_by))
            else:
                groups = sorted(groups, key=lambda group: group.get(order_by))
        elif group_by == AE.atom_execute:
            # 查询各标准插件被执行次数、失败率、重试次数、平均耗时（不计算子流程）
            instance_id_list = taskflow.values_list("pipeline_instance__instance_id")
            # 获得标准插件
            component = ComponentExecuteData.objects.filter(instance_id__in=instance_id_list, is_sub=False)
            component_data = component.values('component_code').annotate(
                execute_times=Count('component_code'),
                avg_execute_time=Avg('elapsed_time')).order_by('component_code')
            # 统计次数
            total = component_data.count()
            component_success_data = component.filter(is_retry=False).values('component_code').annotate(
                success_times=Count('component_code')
            ).order_by('component_code')
            # 用于计算所有标准插件的成功列表
            success_component_dict = {}
            for data in component_success_data:
                success_component_dict[data['component_code']] = data['success_times']
            groups = []
            component_dict = {}
            for bundle in ComponentModel.objects.all():
                name = bundle.name.split('-')
                group_name = _(name[0])
                name = _(name[1])
                component_dict[bundle.code] = '%s-%s' % (group_name, name)
            for data in component_data[(page - 1) * limit: page * limit]:
                code = data.get('component_code')
                execute_times = data.get('execute_times')
                failed_times = execute_times - success_component_dict.get(code, 0)
                failed_times_percent = '%.2f %%' % (failed_times / 1.0 / execute_times * 100)
                groups.append({
                    'componentName': component_dict[code],
                    'executeTimes': execute_times,
                    'avgExecuteTime': '%.2f' % data.get('avg_execute_time', 0),
                    'failedTimes': failed_times,
                    'failedTimesPercent': failed_times_percent
                })
        elif group_by == AE.atom_instance:
            # 被引用的任务实例列表
            # 获得参数中的标准插件code
            component_code = filters.get("component_code")
            # 获取到组件code对应的instance_id_list
            instance_id_list = ComponentExecuteData.objects.filter(is_sub=False)
            # 对code进行二次查找
            instance_id_list = instance_id_list.filter(component_code=component_code).distinct().values_list(
                "instance_id")
            taskflow_list = taskflow.filter(pipeline_instance__instance_id__in=instance_id_list).values(
                'id',
                'business__cc_id',
                'business__cc_name',
                'pipeline_instance__name',
                'category',
                'pipeline_instance__create_time',
                'pipeline_instance__creator'
            )
            # 获得总数
            total = taskflow_list.count()
            taskflow_list = taskflow_list[(page - 1) * limit: page * limit]
            groups = []
            # 循环信息
            for data in taskflow_list:
                groups.append({
                    'instanceId': data.get("id"),
                    'businessId': data.get("business__cc_id"),
                    'businessName': data.get("business__cc_name"),
                    'instanceName': data.get("pipeline_instance__name"),
                    'category': category_dict[data.get("category")],  # 需要将code转为名称
                    "createTime": format_datetime(data.get("pipeline_instance__create_time")),
                    "creator": data.get("pipeline_instance__creator")
                })
        elif group_by == AE.instance_node:
            # 各任务实例执行的标准插件节点个数、子流程节点个数、网关节点数
            groups = []

            # 排序
            instance_id_list = taskflow.values("pipeline_instance__instance_id")
            instance_pipeline_data = InstanceInPipeline.objects.filter(instance_id__in=instance_id_list)
            # 总数
            total = instance_pipeline_data.count()
            order_by = filters.get("order_by", "-instanceId")
            # 使用驼峰转下划线进行转换order_by
            camel_order_by = camel_case_to_underscore_naming(order_by)
            # 排列获取分页后的数据
            pipeline_data = instance_pipeline_data.order_by(camel_order_by)[(page - 1) * limit:page * limit]
            instance_id_list = [tuples.instance_id for tuples in pipeline_data]
            taskflow = taskflow.filter(pipeline_instance__instance_id__in=instance_id_list)

            pipeline_dict = {}
            for pipeline in pipeline_data:
                pipeline_dict[pipeline.instance_id] = {"atom_total": pipeline.atom_total,
                                                       "subprocess_total": pipeline.subprocess_total,
                                                       "gateways_total": pipeline.gateways_total}
            # 需要循环执行计算相关节点
            for flow in taskflow:
                pipeline_instance = flow.pipeline_instance
                instance_id = flow.id
                pipeline_instance_id = pipeline_instance.instance_id
                # 插入信息
                groups.append({
                    'instanceId': instance_id,
                    'businessId': flow.business.cc_id,
                    'businessName': flow.business.cc_name,
                    'instanceName': pipeline_instance.name,
                    'category': category_dict[flow.category],
                    "createTime": format_datetime(pipeline_instance.create_time),
                    "creator": pipeline_instance.creator,
                    "atomTotal": pipeline_dict[pipeline_instance_id]["atom_total"],
                    "subprocessTotal": pipeline_dict[pipeline_instance_id]["subprocess_total"],
                    "gatewaysTotal": pipeline_dict[pipeline_instance_id]["gateways_total"]
                })
            if order_by[0] == "-":
                # 需要去除负号
                order_by = order_by[1:]
                groups = sorted(groups, key=lambda group: -group.get(order_by))
            else:
                groups = sorted(groups, key=lambda group: group.get(order_by))
        elif group_by == AE.instance_details:

            # 各任务执行耗时
            started_time = prefix_filters['pipeline_instance__create_time__gte']
            archived_time = prefix_filters['pipeline_instance__create_time__lt']
            prefix_filters.update(
                pipeline_instance__start_time__gte=prefix_filters.pop('pipeline_instance__create_time__gte'),
                pipeline_instance__start_time__lt=prefix_filters.pop('pipeline_instance__create_time__lt'),
                pipeline_instance__is_finished=True
            )
            taskflow = self.filter(**prefix_filters)
            # 需要distinct去除重复的
            instance_id_list = ComponentExecuteData.objects.filter(
                started_time__gte=started_time,
                archived_time__lte=archived_time).values_list(
                "instance_id").distinct().order_by()
            total = instance_id_list.count()

            # 排序
            order_by = filters.get("order_by", "instanceId")
            component_list = instance_id_list.annotate(execute_time=Sum('elapsed_time')).order_by()
            # 使用驼峰转下划线进行转换order_by
            component_list = component_list.order_by(camel_case_to_underscore_naming(order_by))
            # 分页
            component_list = component_list[(page - 1) * limit:page * limit]
            component_dict = {}
            instance_list = [tuples[0] for tuples in component_list]
            for component in component_list:
                component_dict[component[0]] = component[1]
            taskflow_list = taskflow.filter(pipeline_instance__instance_id__in=instance_list).values(
                'id',
                'pipeline_instance__instance_id',
                'business__cc_id',
                'business__cc_name',
                'pipeline_instance__name',
                'category',
                'pipeline_instance__create_time',
                'pipeline_instance__creator'
            )
            groups = []
            for data in taskflow_list:
                instance_id = data.get("pipeline_instance__instance_id")
                groups.append({
                    'instanceId': data.get("id"),
                    'businessId': data.get("business__cc_id"),
                    'businessName': data.get("business__cc_name"),
                    'instanceName': data.get("pipeline_instance__name"),
                    'category': category_dict[data.get("category")],  # 需要将code转为名称
                    "createTime": format_datetime(data.get("pipeline_instance__create_time")),
                    "creator": data.get("pipeline_instance__creator"),
                    "executeTime": component_dict[instance_id]
                })
            if order_by[0] == "-":
                # 需要去除负号
                order_by = order_by[1:]
                groups = sorted(groups, key=lambda group: -group.get(order_by))
            else:
                groups = sorted(groups, key=lambda group: group.get(order_by))
        elif group_by == AE.instance_time:
            #  按起始时间、业务（可选）、类型（可选）、图表类型（日视图，月视图），查询每一天或每一月的执行数量
            instance_create_time_list = taskflow.values('pipeline_instance__create_time')
            total = instance_create_time_list.count()
            group_type = filters.get('type', 'day')
            create_time = timestamp_to_datetime(filters['create_time'])
            end_time = timestamp_to_datetime(filters['finish_time']) + datetime.timedelta(days=1)

            groups = []
            date_list = []
            for instance in instance_create_time_list:
                instance_time = instance['pipeline_instance__create_time']
                date_key = ''
                # 添加在一个list中 之后使用count方法获取对应的数量
                if group_type == 'day':
                    date_key = instance_time.strftime('%Y-%m-%d')
                elif group_type == 'month':
                    date_key = instance_time.strftime('%Y-%m')
                date_list.append(date_key)
            if group_type == 'day':
                #  日视图
                for d in gen_day_dates(create_time, (end_time - create_time).days + 1):
                    date_key = d.strftime('%Y-%m-%d')
                    groups.append({'time': date_key, 'value': date_list.count(date_key)})
            elif group_type == 'month':
                # 月视图
                # 直接拿到对应的（年-月），不需要在字符串拼接
                for date_key in get_month_dates(create_time, end_time):
                    groups.append({'time': date_key, 'value': date_list.count(date_key)})
        elif group_by in [AE.category, AE.create_method, AE.flow_type]:
            try:
                total, groups = self.classified_count(prefix_filters, group_by)
            except Exception as e:
                message = u"query_task_list params conditions[%s] have invalid key or value: %s" % (filters, e)
                return False, message
        else:
            total, groups = 0, []
        data = {'total': total, 'groups': groups}
        return True, data

    def callback(self, act_id, data):
        try:
            result = pipeline_api.activity_callback(activity_id=act_id, callback_data=data)
        except Exception as e:
            return {
                'result': False,
                'message': e.message
            }

        return {
            'result': result.result,
            'message': result.message
        }


class TaskFlowInstance(models.Model):
    business = models.ForeignKey(Business,
                                 verbose_name=_(u"业务"),
                                 blank=True,
                                 null=True,
                                 on_delete=models.SET_NULL)
    pipeline_instance = models.ForeignKey(PipelineInstance,
                                          blank=True,
                                          null=True,
                                          on_delete=models.SET_NULL)
    category = models.CharField(_(u"任务类型，继承自模板"), choices=TASK_CATEGORY,
                                max_length=255, default='Other')
    template_id = models.CharField(_(u"创建任务所用的模板ID"), max_length=255)
    template_source = models.CharField(_(u"流程模板来源"), max_length=32,
                                       choices=TEMPLATE_SOURCE,
                                       default='business')
    create_method = models.CharField(_(u"创建方式"),
                                     max_length=30,
                                     choices=TASK_CREATE_METHOD,
                                     default='app')
    create_info = models.CharField(_(u"创建任务额外信息（App maker ID或者APP CODE）"),
                                   max_length=255, blank=True)
    flow_type = models.CharField(_(u"任务流程类型"),
                                 max_length=255,
                                 choices=TASK_FLOW_TYPE,
                                 default='common')
    current_flow = models.CharField(_(u"当前任务流程阶段"), max_length=255)
    is_deleted = models.BooleanField(_(u"是否删除"), default=False)

    objects = TaskFlowInstanceManager()

    def __unicode__(self):
        return u"%s_%s" % (self.business, self.pipeline_instance.name)

    class Meta:
        verbose_name = _(u"流程实例 TaskFlowInstance")
        verbose_name_plural = _(u"流程实例 TaskFlowInstance")
        ordering = ['-id']

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
        return self.pipeline_instance.execution_data

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
    def elapsed_time(self):
        return self.pipeline_instance.elapsed_time

    @property
    def template(self):
        if self.template_source == 'business':
            return TaskTemplate.objects.get(pk=self.template_id)
        else:
            return CommonTemplate.objects.get(pk=self.template_id)

    @property
    def url(self):
        if settings.RUN_MODE == 'PRODUCT':
            prefix = settings.APP_HOST
        else:
            prefix = settings.TEST_APP_HOST
        return '%staskflow/execute/%s/?instance_id=%s' % (prefix, self.business.cc_id, self.id)

    @property
    def subprocess_info(self):
        return self.pipeline_instance.template.subprocess_version_info

    @staticmethod
    def format_pipeline_status(status_tree):
        """
        @summary: 转换通过 pipeline api 获取的任务状态格式
        @return:
        """
        status_tree.setdefault('children', {})
        status_tree.pop('created_time', '')

        status_tree['start_time'] = strftime_with_timezone(status_tree.pop('started_time'))
        status_tree['finish_time'] = strftime_with_timezone(status_tree.pop('archived_time'))
        child_status = []
        for identifier_code, child_tree in status_tree['children'].iteritems():
            TaskFlowInstance.format_pipeline_status(child_tree)
            child_status.append(child_tree['state'])

        if status_tree['state'] == states.BLOCKED:
            if states.RUNNING in child_status:
                status_tree['state'] = states.RUNNING
            elif states.FAILED in child_status:
                status_tree['state'] = states.FAILED
            elif states.SUSPENDED in child_status or 'NODE_SUSPENDED' in child_status:
                status_tree['state'] = 'NODE_SUSPENDED'
            # 子流程 BLOCKED 状态表示子节点失败
            elif not child_status:
                status_tree['state'] = states.FAILED

    def get_status(self):
        if not self.pipeline_instance.is_started:
            return {
                "start_time": None,
                "state": "CREATED",
                "retry": 0,
                "skip": 0,
                "finish_time": None,
                "elapsed_time": 0,
                "children": {}
            }
        status_tree = pipeline_api.get_status_tree(self.pipeline_instance.instance_id, max_depth=99)
        TaskFlowInstance.format_pipeline_status(status_tree)
        return status_tree

    def get_node_data(self, node_id, component_code=None, subprocess_stack=None):
        if not self.has_node(node_id):
            message = 'node[node_id={node_id}] not found in task[task_id={task_id}]'.format(
                node_id=node_id,
                task_id=self.id
            )
            return {'result': False, 'message': message, 'data': {}}

        act_started = True
        result = True
        inputs = {}
        outputs = {}
        try:
            inputs = pipeline_api.get_inputs(node_id)
            outputs = pipeline_api.get_outputs(node_id)
        except Data.DoesNotExist:
            act_started = False

        instance_data = self.pipeline_instance.execution_data
        if not act_started:
            try:
                inputs = WebPipelineAdapter(instance_data).get_act_inputs(
                    act_id=node_id,
                    subprocess_stack=subprocess_stack,
                    root_pipeline_data=get_pipeline_context(self.pipeline_instance, 'instance')
                )
                outputs = {}
            except Exception as e:
                inputs = {}
                result = False
                message = 'parser pipeline tree error: %s' % e
                logger.exception(message)
                outputs = {'ex_data': message}

        if not isinstance(inputs, dict):
            inputs = {}
        if not isinstance(outputs, dict):
            outputs = {}

        if component_code:
            outputs_table = []
            try:
                component = library.ComponentLibrary.get_component_class(component_code)
                outputs_format = component.outputs_format()
            except Exception as e:
                result = False
                message = 'get component[component_code=%s] format error: %s' % (component_code, e)
                logger.exception(message)
                outputs = {'ex_data': message}
            else:
                outputs_data = outputs.get('outputs', {})
                # 在标准插件定义中的预设输出参数
                archived_keys = []
                for outputs_item in outputs_format:
                    value = outputs_data.get(outputs_item['key'], '')
                    outputs_table.append({
                        'name': outputs_item['name'],
                        'key': outputs_item['key'],
                        'value': value,
                        'preset': True,
                    })
                    archived_keys.append(outputs_item['key'])
                # 其他输出参数
                for out_key, out_value in outputs_data.items():
                    if out_key not in archived_keys:
                        outputs_table.append({
                            'name': out_key,
                            'key': out_key,
                            'value': out_value,
                            'preset': False,
                        })
        else:
            try:
                outputs_table = [{'key': key, 'value': val, 'preset': False}
                                 for key, val in outputs.get('outputs', {}).items()]
            except Exception:
                # for unexpected case
                logger.error(u"get outputs_table error, outputs: {outputs}, traceback: {traceback}".format(
                    outputs=outputs,
                    traceback=traceback.format_exc()
                ))
                outputs_table = []

        data = {
            'inputs': inputs,
            'outputs': outputs_table,
            'ex_data': outputs.pop('ex_data', '')
        }
        return {'result': result, 'data': data, 'message': '' if result else data['ex_data']}

    def get_node_detail(self, node_id, component_code=None, subprocess_stack=None):
        if not self.has_node(node_id):
            message = 'node[node_id={node_id}] not found in task[task_id={task_id}]'.format(
                node_id=node_id,
                task_id=self.id
            )
            return {'result': False, 'message': message, 'data': {}}

        ret_data = self.get_node_data(node_id, component_code, subprocess_stack)
        try:
            detail = pipeline_api.get_status_tree(node_id)
        except exceptions.InvalidOperationException as e:
            return {'result': False, 'message': e.message, 'data': {}}
        TaskFlowInstance.format_pipeline_status(detail)
        detail['histories'] = pipeline_api.get_activity_histories(node_id)
        for his in detail['histories']:
            his.setdefault('state', 'FAILED')
            TaskFlowInstance.format_pipeline_status(his)
        detail.update(ret_data['data'])
        return {'result': True, 'data': detail, 'message': ''}

    def user_has_perm(self, user, perm):
        """
        @summary: 判断用户是否有操作当前流程权限
        @param user:
        @param perm: create_task、fill_params、execute_task
        @return:
        """
        business = self.business
        if user.is_superuser or user.has_perm('manage_business', business):
            return True
        if self.template_source == 'business':
            template = TaskTemplate.objects.get(pk=self.template_id)
            return user.has_perm(perm, template)
        else:
            perm = 'common_%s' % perm
            template_perm, _ = CommonTmplPerm.objects.get_or_create(common_template_id=self.template_id,
                                                                    biz_cc_id=self.business.cc_id)
            return user.has_perm(perm, template_perm)

    def task_claim(self, username, constants, name):
        if self.flow_type != 'common_func':
            result = {
                'result': False,
                'message': 'task is not functional'
            }
        elif self.current_flow != 'func_claim':
            result = {
                'result': False,
                'message': 'task with current_flow:%s cannot be claimed' % self.current_flow
            }
        else:
            with transaction.atomic():
                self.reset_pipeline_instance_data(constants, name)
                result = self.function_task.get(task=self).claim_task(username)
                if result['result']:
                    self.current_flow = 'execute_task'
                    self.save()
        return result

    def task_action(self, action, username):
        if self.current_flow != 'execute_task':
            return {'result': False, 'message': 'task with current_flow:%s cannot be %sed' % (self.current_flow,
                                                                                              action)}
        if action not in INSTANCE_ACTIONS:
            return {'result': False, 'message': 'task action is invalid'}
        if action == 'start':
            try:
                action_result = self.pipeline_instance.start(username)
                if action_result.result:
                    taskflow_started.send(sender=self, username=username)
                return {'result': action_result.result, 'data': action_result.message, 'message': action_result.message}

            except ConvergeMatchError as e:
                message = u"task[id=%s] has invalid converge, message: %s, node_id: %s" % (self.id,
                                                                                           e.message,
                                                                                           e.gateway_id)
                logger.exception(message)
                return {'result': False, 'message': message}

            except StreamValidateError as e:
                message = u"task[id=%s] stream is invalid, message: %s, node_id: %s" % (self.id, e.message, e.node_id)
                logger.exception(message)
                return {'result': False, 'message': message}

            except IsolateNodeError as e:
                message = u"task[id=%s] has isolate structure, message: %s" % (self.id, e.message)
                logger.exception(message)
                return {'result': False, 'message': message}

            except ConnectionValidateError as e:
                message = u"task[id=%s] connection check failed, message: %s, nodes: %s" % (self.id,
                                                                                            e.detail,
                                                                                            e.failed_nodes)
                logger.exception(message)
                return {'result': False, 'message': message}

            except Exception as e:
                message = u"task[id=%s] action failed:%s" % (self.id, e)
                logger.exception(message)
                return {'result': False, 'message': message}
        try:
            action_result = INSTANCE_ACTIONS[action](self.pipeline_instance.instance_id)
            if action_result.result:
                return {'result': True, 'data': {}}
            else:
                return {'result': action_result.result, 'message': action_result.message}
        except Exception as e:
            message = u"task[id=%s] action failed:%s" % (self.id, e)
            logger.exception(message)
            return {'result': False, 'message': message}

    def nodes_action(self, action, node_id, username, **kwargs):
        if not self.has_node(node_id):
            message = 'node[node_id={node_id}] not found in task[task_id={task_id}]'.format(
                node_id=node_id,
                task_id=self.id
            )
            return {'result': False, 'message': message}
        if action not in NODE_ACTIONS:
            return {'result': False, 'message': 'task action is invalid'}
        try:
            if action == 'callback':
                action_result = NODE_ACTIONS[action](node_id, kwargs['data'])
            elif action == 'skip_exg':
                action_result = NODE_ACTIONS[action](node_id, kwargs['flow_id'])
            elif action == 'retry':
                action_result = NODE_ACTIONS[action](node_id, kwargs['inputs'])
            else:
                action_result = NODE_ACTIONS[action](node_id)
        except Exception as e:
            message = u"task[id=%s] node[id=%s] action failed:%s" % (self.id, node_id, e)
            logger.exception(message)
            return {'result': False, 'message': message}
        if action_result.result:
            return {'result': True, 'data': 'success'}
        else:
            return {'result': action_result.result, 'message': action_result.message}

    def clone(self, username, **kwargs):
        clone_pipeline = self.pipeline_instance.clone(username, **kwargs)
        self.pk = None
        self.pipeline_instance = clone_pipeline
        if 'create_method' in kwargs:
            self.create_method = kwargs['create_method']
            self.create_info = kwargs.get('create_info', '')
        if self.flow_type == 'common_func':
            self.current_flow = 'func_claim'
        else:
            self.current_flow = 'execute_task'
        self.is_deleted = False
        self.save()
        return self.pk

    def reset_pipeline_instance_data(self, constants, name):
        exec_data = self.pipeline_tree
        try:
            for key, value in constants.iteritems():
                if key in exec_data['constants']:
                    exec_data['constants'][key]['value'] = value
            self.pipeline_instance.set_execution_data(exec_data)
            if name:
                self.pipeline_instance.name = name
                self.pipeline_instance.save()
        except Exception as e:
            logger.exception('TaskFlow reset_pipeline_instance_data error:id=%s, constants=%s, error=%s' % (
                self.pk, json.dumps(constants), e))
            return {'result': False, 'message': 'constants is not valid'}
        return {'result': True, 'data': 'success'}

    def spec_nodes_timer_reset(self, node_id, username, inputs):
        if not self.has_node(node_id):
            message = 'node[node_id={node_id}] not found in task[task_id={task_id}]'.format(
                node_id=node_id,
                task_id=self.id
            )
            return {'result': False, 'message': message}
        action_result = pipeline_api.forced_fail(node_id)
        if not action_result.result:
            return {'result': False, 'message': 'timer node not exits or is finished'}
        action_result = pipeline_api.retry_node(node_id, inputs)
        if not action_result.result:
            return {'result': False, 'message': 'reset timer failed, please try again later'}
        return {'result': True, 'data': 'success'}

    def get_act_web_info(self, act_id):

        def get_act_of_pipeline(pipeline_tree):
            for node_id, node_info in pipeline_tree['activities'].items():
                if node_id == act_id:
                    return node_info
                elif node_info['type'] == 'SubProcess':
                    return get_act_of_pipeline(node_info['pipeline'])

        return get_act_of_pipeline(self.pipeline_tree)

    def log_for_node(self, node_id, history_id=None):
        if not history_id:
            history_id = -1

        if not self.has_node(node_id):
            message = 'node[node_id={node_id}] not found in task[task_id={task_id}]'.format(
                node_id=node_id,
                task_id=self.id
            )
            return {
                'result': False,
                'data': None,
                'message': message
            }

        plain_log = LogEntry.objects.plain_log_for_node(node_id, history_id)
        return {
            'result': True if plain_log else False,
            'data': plain_log,
            'message': 'node with history_id(%s) does not exist or log already expired' % history_id if not plain_log
            else ''
        }

    def has_node(self, node_id):
        return node_id in self.pipeline_instance.node_id_set

    def get_task_detail(self):
        data = {
            'id': self.id,
            'business_id': int(self.business.cc_id),
            'business_name': self.business.cc_name,
            'name': self.name,
            'create_time': format_datetime(self.create_time),
            'creator': self.creator,
            'create_method': self.create_method,
            'template_id': int(self.template_id),
            'start_time': format_datetime(self.start_time),
            'finish_time': format_datetime(self.finish_time),
            'executor': self.executor,
            'elapsed_time': self.elapsed_time,
            'pipeline_tree': self.pipeline_tree,
            'task_url': self.url
        }
        exec_data = self.pipeline_instance.execution_data
        # inputs data
        constants = exec_data['constants']
        data['constants'] = constants
        # outputs data, if task has not executed, outputs is empty list
        instance_id = self.pipeline_instance.instance_id
        try:
            outputs = pipeline_api.get_outputs(instance_id)
        except Data.DoesNotExist:
            outputs = {}
        outputs_table = [{'key': key, 'value': val} for key, val in outputs.get('outputs', {}).items()]
        for out in outputs_table:
            out['name'] = constants[out['key']]['name']
        data.update({
            'outputs': outputs_table,
            'ex_data': outputs.get('ex_data', '')
        })
        return data

    def callback(self, act_id, data):
        if not self.has_node(act_id):
            return {
                'result': False,
                'message': 'task[{tid}] does not have node[{nid}]'.format(tid=self.id, nid=act_id)
            }

        return TaskFlowInstance.objects.callback(act_id, data)
