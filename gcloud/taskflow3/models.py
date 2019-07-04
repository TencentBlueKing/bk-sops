# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import datetime
import json
import logging
import re

from django.db import models, transaction
from django.db.models import Count, Avg, Sum
from django.utils.translation import ugettext_lazy as _

from blueapps.utils import managermixins
from gcloud.conf import settings
from gcloud.core.constant import TASK_FLOW_TYPE, TASK_CATEGORY, AE
from gcloud.core.models import Business
from gcloud.core.utils import (convert_readable_username,
                               strftime_with_timezone,
                               get_client_by_user_and_biz_id,
                               timestamp_to_datetime,
                               format_datetime)
from gcloud.tasktmpl3.models import TaskTemplate, replace_template_id
from gcloud.taskflow3.constants import TASK_CREATE_METHOD
from gcloud.taskflow3.signals import taskflow_started
from pipeline.component_framework.models import ComponentModel
from pipeline.contrib.statistics.models import ComponentExecuteData

from pipeline.core.constants import PE
from pipeline.component_framework import library
from pipeline.component_framework.constant import ConstantPool
from pipeline.models import PipelineInstance
from pipeline.engine import exceptions
from pipeline.engine import api as pipeline_api
from pipeline.engine.models import Data
from pipeline.parser import pipeline_parser
from pipeline.utils.context import get_pipeline_context
from pipeline.engine import states
from pipeline.log.models import LogEntry

logger = logging.getLogger("root")

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
        replace_template_id(pipeline_tree)
        pipeline_template_data = {
            'name': kwargs['name'],
            'creator': kwargs['creator'],
            'description': kwargs.get('description', ''),
        }
        pipeline_instance = PipelineInstance.objects.create_instance(
            template.pipeline_template,
            pipeline_tree,
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
    def preview_pipeline_tree_exclude_task_nodes(pipeline_tree, exclude_task_nodes_id=None):
        if exclude_task_nodes_id is None:
            exclude_task_nodes_id = []

        locations = {item['id']: item for item in pipeline_tree.get(PE.location, [])}
        lines = {item['id']: item for item in pipeline_tree.get(PE.line, [])}

        for task_node_id in exclude_task_nodes_id:
            if task_node_id not in pipeline_tree[PE.activities]:
                error = 'task node[id=%s] is not in template pipeline tree' % task_node_id
                raise Exception(error)

            task_node = pipeline_tree[PE.activities].pop(task_node_id)
            if not task_node['optional']:
                error = 'task node[id=%s] is not optional' % task_node_id
                raise Exception(error)

            # change next_node's incoming: task node、control node is different
            # change incoming_flow's target to next node
            # delete outgoing_flow
            incoming_id, outgoing_id = task_node[PE.incoming], task_node[PE.outgoing]
            incoming_flow = pipeline_tree[PE.flows][incoming_id]
            outgoing_flow = pipeline_tree[PE.flows][outgoing_id]
            target_id = outgoing_flow[PE.target]

            if target_id in pipeline_tree[PE.activities]:
                next_node = pipeline_tree[PE.activities][target_id]
                next_node[PE.incoming] = incoming_id
            elif target_id in pipeline_tree[PE.gateways]:
                next_node = pipeline_tree[PE.gateways][target_id]
                if next_node['type'] in [PE.ExclusiveGateway, PE.ParallelGateway]:
                    next_node[PE.incoming] = incoming_id
                # PE.ConvergeGateway
                else:
                    next_node[PE.incoming].pop(next_node[PE.incoming].index(outgoing_id))
                    next_node[PE.incoming].append(incoming_id)
            # PE.end_event
            else:
                next_node = pipeline_tree[PE.end_event]
                next_node[PE.incoming] = incoming_id

            incoming_flow[PE.target] = next_node['id']

            pipeline_tree[PE.flows].pop(outgoing_id)

            # web location data
            try:
                locations.pop(task_node_id)
                lines.pop(outgoing_id)
                lines[incoming_id][PE.target]['id'] = next_node['id']
            except Exception as e:
                logger.exception('create_pipeline_instance_exclude_task_nodes adjust web data error:%s' % e)

        pipeline_tree[PE.line] = lines.values()
        pipeline_tree[PE.location] = locations.values()

        # pop unreferenced constant
        data = {}
        for task_node_id, task_node in pipeline_tree[PE.activities].items():
            if task_node['type'] == PE.ServiceActivity:
                node_data = {('%s_%s' % (task_node_id, key)): value
                             for key, value in task_node['component']['data'].items()}
            # PE.SubProcess
            else:
                node_data = {('%s_%s' % (task_node_id, key)): value
                             for key, value in task_node['constants'].items() if value['show_type'] == 'show'}
            data.update(node_data)

        for gw_id, gw in pipeline_tree[PE.gateways].items():
            if gw['type'] == PE.ExclusiveGateway:
                gw_data = {('%s_%s' % (gw_id, key)): {'value': value['evaluate']}
                           for key, value in gw['conditions'].items()}
                data.update(gw_data)

        constants = pipeline_tree[PE.constants]
        referenced_keys = []
        while True:
            last_count = len(referenced_keys)
            cons_pool = ConstantPool(data, lazy=True)
            refs = cons_pool.get_reference_info(strict=False)
            for _, keys in refs.items():
                for key in keys:
                    if key in constants and key not in referenced_keys:
                        referenced_keys.append(key)
                        data.update({key: constants[key]})
            if len(referenced_keys) == last_count:
                break
            last_count = len(referenced_keys)

        # keep outputs constants
        outputs_keys = [key for key, value in constants.items()
                        if value['source_type'] == 'component_outputs'
                        and value['source_info'].keys()[0] not in exclude_task_nodes_id]
        referenced_keys = list(set(referenced_keys + outputs_keys))
        pipeline_tree[PE.outputs] = [key for key in pipeline_tree[PE.outputs] if key in referenced_keys]

        # rebuild constants index
        referenced_keys.sort(key=lambda x: constants[x]['index'])
        new_constants = {}
        for index, key in enumerate(referenced_keys):
            value = constants[key]
            value['index'] = index
            # delete constant reference info to task node
            for task_node_id in exclude_task_nodes_id:
                if task_node_id in value['source_info']:
                    value['source_info'].pop(task_node_id)
            new_constants[key] = value
        pipeline_tree[PE.constants] = new_constants

        return

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
        pipeline_inst_regex = re.compile(r'^name|create_time|creator|create_time|executor|'
                                         r'start_time|finish_time|is_started|is_finished')
        prefix_filters = {}
        for cond in filters:
            # 如果conditions内容为空或为空字符，不可加入查询条件中
            if filters[cond] == 'None' or filters[cond] == '' or cond == 'component_code':
                continue
            if pipeline_inst_regex.match(cond):
                filter_cond = 'pipeline_instance__%s' % cond
                # 时间需要大于小于
                if cond == 'create_time':
                    filter_cond = '%s__gte' % filter_cond
                    prefix_filters.update(
                        {filter_cond: timestamp_to_datetime(filters[cond])})
                    continue
                # 结束时间由创建时间来决定
                if cond == 'finish_time':
                    filter_cond = 'pipeline_instance__create_time__lt'
                    prefix_filters.update(
                        {filter_cond: timestamp_to_datetime(filters[cond]) + datetime.timedelta(days=1)})
                    continue
            else:
                filter_cond = cond
            prefix_filters.update({filter_cond: filters[cond]})

        if group_by == AE.state:
            try:
                taskflow = self.filter(**prefix_filters)
            except Exception as e:
                message = u"query_task_list params conditions[%s] have invalid key or value: %s" % (filters, e)
                return False, message
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
            cc_name = AE.business__cc_name
            try:
                taskflow = self.filter(**prefix_filters)
            except Exception as e:
                message = u"query_task_list params conditions[%s] have invalid key or value: %s" % (filters, e)
                return False, message
            # 获取所有数据
            total = taskflow.count()
            taskflow_list = taskflow.values(group_by, cc_name).annotate(value=Count(group_by)).order_by()
            groups = []
            for data in taskflow_list:
                groups.append({
                    'code': data.get(group_by),
                    'name': data.get(cc_name),
                    'value': data.get('value', 0)
                })
        elif group_by == AE.atom_execute:
            # 查询各原子被执行次数、失败率、重试次数、平均耗时（不计算子流程）
            try:
                instance_id_list = self.filter(**prefix_filters).values_list("pipeline_instance__instance_id")
            except Exception as e:
                message = u"query_task_list params conditions[%s] have invalid key or value: %s" % (filters, e)
                return False, message
            # 获得原子
            component = ComponentExecuteData.objects.filter(instance_id__in=instance_id_list, is_sub=False)
            component_data = component.values('component_code').annotate(
                execute_times=Count('component_code'),
                avg_execute_time=Avg('elapsed_time')).order_by('component_code')
            # 统计次数
            total = component_data.count()
            component_success_data = component.filter(is_retry=False).values('component_code').annotate(
                success_times=Count('component_code')
            ).order_by('component_code')
            # 用于计算所有原子的成功列表
            success_component_dict = {}
            for data in component_success_data:
                success_component_dict[data['component_code']] = data['success_times']
            groups = []
            component_dict = ComponentModel.objects.get_component_dict()
            for data in component_data:
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
            try:
                taskflow_list = self.filter(**prefix_filters)
            except Exception as e:
                message = u"query_task_list params conditions[%s] have invalid key or value: %s" % (filters, e)
                return False, message
            # 获取原子code
            # 获得参数中的原子code
            component_code = filters.get("component_code")
            # 获取到组件code对应的instance_id_list
            instance_id_list = ComponentExecuteData.objects.filter(is_sub=False)
            # 参数携带了原子code话，针对查询，不携带查询全部
            if component_code:
                instance_id_list = instance_id_list.filter(component_code=component_code).values_list(
                    "instance_id")
            taskflow_list = taskflow_list.filter(pipeline_instance__instance_id__in=instance_id_list).values(
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
            taskflow_list = taskflow_list[(page - 1) * limit:page * limit]
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
            # 各任务实例执行的原子节点个数、子流程节点个数、网关节点数
            try:
                taskflow_list = self.filter(**prefix_filters)
            except Exception as e:
                message = u"query_task_list params conditions[%s] have invalid key or value: %s" % (filters, e)
                return False, message
            # 总数
            total = taskflow_list.count()
            groups = []
            for taskflow in taskflow_list[(page - 1) * limit:page * limit]:
                atom_total = 0
                subprocess_total = 0
                pipeline_tree = taskflow.pipeline_tree
                tree_activities = pipeline_tree["activities"]
                gateways_total = len(pipeline_tree["gateways"])
                for activity in tree_activities:
                    activity_type = tree_activities[activity]["type"]
                    if activity_type == "ServiceActivity":
                        atom_total += 1
                    elif activity_type == "SubProcess":
                        subprocess_total += 1
                pipeline_instance = taskflow.pipeline_instance
                # 插入信息
                groups.append({
                    'instanceId': taskflow.id,
                    'businessId': taskflow.business.cc_id,
                    'businessName': taskflow.business.cc_name,
                    'instanceName': pipeline_instance.name,
                    'category': category_dict[taskflow.category],
                    "createTime": format_datetime(pipeline_instance.create_time),
                    "creator": pipeline_instance.creator,
                    "atomTotal": atom_total,
                    "subprocessTotal": subprocess_total,
                    "gatewaysTotal": gateways_total
                })
            pass
        elif group_by == AE.instance_details:
            # 各任务实例详情和执行耗时
            try:
                taskflow_list = self.filter(**prefix_filters)
            except Exception as e:
                message = u"query_task_list params conditions[%s] have invalid key or value: %s" % (filters, e)
                return False, message
            started_time = timestamp_to_datetime(filters["create_time"])
            end_time = timestamp_to_datetime(filters["finish_time"])
            # 需要去除重复的
            instance_id_list = ComponentExecuteData.objects.filter(
                started_time__gte=started_time,
                started_time__lte=end_time).values_list(
                "instance_id").distinct().order_by()
            # 总数
            total = instance_id_list.count()
            # 获得所有的任务实例的执行耗时
            component_list = instance_id_list.annotate(execute_times=Sum('elapsed_time'))
            component_dict = {}
            for component in component_list:
                component_dict[component[0]] = component[1]
            taskflow_list = taskflow_list.filter(pipeline_instance__instance_id__in=instance_id_list).values(
                'id',
                'pipeline_instance__instance_id',
                'business__cc_id',
                'business__cc_name',
                'pipeline_instance__name',
                'category',
                'pipeline_instance__create_time',
                'pipeline_instance__creator'
            )[(page - 1) * limit:page * limit]
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
        return TaskTemplate.objects.get(pk=self.template_id)

    @property
    def url(self):
        if settings.RUN_MODE == 'PRODUCT':
            prefix = settings.APP_HOST
        else:
            prefix = settings.TEST_APP_HOST
        return '%s/taskflow/detail/%s/?instance_id=%s' % (prefix, self.business.cc_id, self.id)

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
        act_started = True
        result = True
        try:
            inputs = pipeline_api.get_inputs(node_id)
            outputs = pipeline_api.get_outputs(node_id)
        except Data.DoesNotExist:
            act_started = False

        if component_code:
            if not act_started:
                try:
                    instance_data = self.pipeline_instance.execution_data
                    inputs = pipeline_parser.WebPipelineAdapter(instance_data).get_act_inputs(
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
                for outputs_item in outputs_format:
                    value = outputs.get('outputs', {}).get(outputs_item['key'], '')
                    outputs_table.append({
                        'name': outputs_item['name'],
                        'value': value
                    })
        else:
            inputs = {}
            outputs = {}
            outputs_table = []

        data = {
            'inputs': inputs,
            'outputs': outputs_table,
            'ex_data': outputs.pop('ex_data', '')
        }
        return {'result': result, 'data': data, 'message': '' if result else data['ex_data']}

    def get_node_detail(self, node_id, component_code=None, subprocess_stack=None):
        try:
            detail = pipeline_api.get_status_tree(node_id)
        except exceptions.InvalidOperationException as e:
            return {'result': False, 'message': e.message}
        TaskFlowInstance.format_pipeline_status(detail)
        data = self.get_node_data(node_id, component_code, subprocess_stack)
        if not data['result']:
            return data
        detail['histories'] = pipeline_api.get_activity_histories(node_id)
        for his in detail['histories']:
            his.setdefault('state', 'FAILED')
            TaskFlowInstance.format_pipeline_status(his)
        detail.update(data['data'])
        return {'result': True, 'data': detail}

    def user_has_perm(self, user, flow_list):
        """
        @summary: 判断用户是否有操作当前流程权限
        @param user:
        @param flow_list:['fill_params', 'execute_task']
        @return:
        """
        user_has_right = False
        try:
            business = self.business
            template = TaskTemplate.objects.get(pk=self.template_id)
            if user.is_superuser or user.has_perm('manage_business', business):
                user_has_right = True
            else:
                for flow in flow_list:
                    perm_name = flow
                    if user.has_perm(perm_name, template):
                        user_has_right = True
                        break
        except Exception as e:
            logger.exception(u"TaskFlowInstance user_has_perm exception, error=%s" % e)
        return user_has_right

    def task_claim(self, username, constants, name):
        if self.flow_type != 'common_func':
            result = {
                'result': False,
                'messgae': 'task is not functional'
            }
        elif self.current_flow != 'func_claim':
            result = {
                'result': False,
                'messgae': 'task with current_flow:%s cannot be claimed' % self.current_flow
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
                success, data = self.pipeline_instance.start(username)
                if success:
                    taskflow_started.send(sender=self, username=username)
                return {'result': success, 'data': data, 'message': data}
            except Exception as e:
                message = u"task[id=%s] action failed:%s" % (self.id, e)
                logger.exception(message)
                return {'result': False, 'message': message}
        try:
            success = INSTANCE_ACTIONS[action](self.pipeline_instance.instance_id)
            if success:
                return {'result': True, 'data': {}}
            else:
                return {'result': False, 'message': 'operate failed, please try again later'}
        except Exception as e:
            message = u"task[id=%s] action failed:%s" % (self.id, e)
            logger.exception(message)
            return {'result': False, 'message': message}

    def nodes_action(self, action, node_id, username, **kwargs):
        if not self.has_node(node_id):
            return {'result': False, 'message': 'node which be operated is not in this flow'}
        if action not in NODE_ACTIONS:
            return {'result': False, 'message': 'task action is invalid'}
        try:
            if action == 'callback':
                success = NODE_ACTIONS[action](node_id, kwargs['data'])
            elif action == 'skip_exg':
                success = NODE_ACTIONS[action](node_id, kwargs['flow_id'])
            elif action == 'retry':
                success = NODE_ACTIONS[action](node_id, kwargs['inputs'])
            else:
                success = NODE_ACTIONS[action](node_id)
        except Exception as e:
            message = u"task[id=%s] node[id=%s] action failed:%s" % (self.id, node_id, e)
            logger.exception(message)
            return {'result': False, 'message': message}
        if success:
            return {'result': True, 'data': 'success'}
        else:
            return {'result': False, 'message': 'operate failed, please try again later'}

    def clone(self, username, **kwargs):
        clone_pipeline = self.pipeline_instance.clone(username)
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
            return {'result': False, 'message': 'timer which be operated is not in this flow'}
        success = pipeline_api.forced_fail(node_id)
        if not success:
            return {'result': False, 'message': 'timer node not exits or is finished'}
        success = pipeline_api.retry_node(node_id, inputs)
        if not success:
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

    def send_message(self, msg_type, atom_node_name=''):
        template = self.template
        pipeline_inst = self.pipeline_instance
        executor = pipeline_inst.executor

        notify_type = json.loads(template.notify_type)
        receivers_list = template.get_notify_receivers_list(executor)
        receivers = ','.join(receivers_list)

        if msg_type == 'atom_failed':
            title = _(u"【标准运维APP通知】执行失败")
            content = _(u"您在【{cc_name}】业务中的任务【{task_name}】执行失败，当前失败节点是【{node_name}】，"
                        u"操作员是【{executor}】，请前往标准运维APP({url})查看详情！").format(
                cc_name=self.business.cc_name,
                task_name=pipeline_inst.name,
                node_name=atom_node_name,
                executor=executor,
                url=self.url
            )
        elif msg_type == 'task_finished':
            title = _(u"【标准运维APP通知】执行完成")
            content = _(u"您在【{cc_name}】业务中的任务【{task_name}】执行成功，操作员是【{executor}】，"
                        u"请前往标准运维APP({url})查看详情！").format(
                cc_name=self.business.cc_name,
                task_name=pipeline_inst.name,
                executor=executor,
                url=self.url
            )
        else:
            return False

        client = get_client_by_user_and_biz_id(executor, self.business.cc_id)
        if 'weixin' in notify_type:
            kwargs = {
                'receiver__username': receivers,
                'data': {
                    'heading': title,
                    'message': content,
                }
            }
            result = client.cmsi.send_weixin(kwargs)
            if not result['result']:
                logger.error('taskflow send weixin, kwargs=%s, result=%s' % (json.dumps(kwargs),
                                                                             json.dumps(result)))
        if 'sms' in notify_type:
            kwargs = {
                'receiver__username': receivers,
                'content': u"%s\n%s" % (title, content),
            }
            result = client.cmsi.send_sms(kwargs)
            if not result['result']:
                logger.error('taskflow send sms, kwargs=%s, result=%s' % (json.dumps(kwargs),
                                                                          json.dumps(result)))

        if 'mail' in notify_type:
            kwargs = {
                'receiver__username': receivers,
                'title': title,
                'content': content,
            }
            result = client.cmsi.send_mail(kwargs)
            if not result['result']:
                logger.error('taskflow send mail, kwargs=%s, result=%s' % (json.dumps(kwargs),
                                                                           json.dumps(result)))

        if 'voice' in notify_type:
            kwargs = {
                'receiver__username': receivers,
                'auto_read_message': u"%s\n%s" % (title, content),
            }
            result = client.cmsi.send_voice_msg(kwargs)
            if not result['result']:
                logger.error('taskflow send voice, kwargs=%s, result=%s' % (json.dumps(kwargs),
                                                                            json.dumps(result)))

        return True

    def log_for_node(self, node_id, history_id=None):
        if not history_id:
            history_id = -1

        if not self.has_node(node_id):
            return {
                'result': False,
                'data': None,
                'message': 'node which be operated is not in this flow'
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
