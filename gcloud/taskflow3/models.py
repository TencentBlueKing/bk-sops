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
import traceback
from copy import deepcopy

import ujson as json
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

from pipeline.core.constants import PE
from pipeline.component_framework.constant import ConstantPool
from pipeline.models import PipelineInstance
from pipeline.engine import states
from pipeline.validators.gateway import validate_gateways
from pipeline.validators.utils import format_node_io_to_list
from pipeline_web.core.abstract import NodeAttr

from pipeline_web.core.models import NodeInInstance
from pipeline_web.parser.clean import PipelineWebTreeCleaner
from pipeline_web.wrapper import PipelineTemplateWebWrapper

from gcloud import err_code
from gcloud.conf import settings
from gcloud.core.constant import TASK_FLOW_TYPE, TASK_CATEGORY
from gcloud.core.models import Project, EngineConfig
from gcloud.core.utils import convert_readable_username
from gcloud.utils.dates import format_datetime
from gcloud.commons.template.models import CommonTemplate
from gcloud.commons.template.utils import replace_template_id
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tasktmpl3.constants import NON_COMMON_TEMPLATE_TYPES
from gcloud.taskflow3.context import TaskContext
from gcloud.taskflow3.mixins import TaskFlowStatisticsMixin
from gcloud.taskflow3.constants import TASK_CREATE_METHOD, TEMPLATE_SOURCE, PROJECT, ONETIME
from gcloud.taskflow3.dispatchers import TaskCommandDispatcher, NodeCommandDispatcher
from gcloud.shortcuts.cmdb import get_business_group_members

logger = logging.getLogger("root")

MANUAL_INTERVENTION_EXEMPT_STATES = frozenset([states.CREATED, states.FINISHED, states.REVOKED])

MANUAL_INTERVENTION_REQUIRED_STATES = frozenset([states.FAILED, states.SUSPENDED])

MANUAL_INTERVENTION_COMP_CODES = frozenset(["pause_node"])


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

        TaskFlowInstanceManager.preview_pipeline_tree_exclude_task_nodes(pipeline_tree, exclude_task_nodes_id)

        # change constants
        for key, value in list(constants.items()):
            if key in pipeline_tree[PE.constants]:
                pipeline_tree[PE.constants][key]["value"] = value

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
            engine_ver=self.engine_ver, taskflow_id=self.id, pipeline_instance=self.pipeline_instance
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
            engine_ver=self.engine_ver, taskflow_id=self.id, pipeline_instance=self.pipeline_instance
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
            group_members = get_business_group_members(self.project.bk_biz_id, receiver_group)

            receivers.extend(group_members)

        return receivers

    def get_notify_type(self):
        return json.loads(self.template.notify_type)


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
        return TaskContext(taskflow, username).context()


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
