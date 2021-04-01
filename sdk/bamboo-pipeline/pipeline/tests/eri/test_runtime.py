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

import json

from django.test import TransactionTestCase

from bamboo_engine.eri import NodeType
from bamboo_engine import builder
from bamboo_engine import validator
from bamboo_engine.builder import *  # noqa

from pipeline.eri.models import Process, Node, Data, ContextValue, ContextOutputs
from pipeline.eri.runtime import BambooDjangoRuntime


class BambooDjangoRuntimeTestCase(TransactionTestCase):
    def setUp(self):
        self.maxDiff = None
        self.runtime = BambooDjangoRuntime()

    def test_node_rerun_limit(self):
        self.assertEqual(self.runtime.node_rerun_limit("1", "2"), 100)

    def test_prepare_run_pipeline_simple(self):

        # struct
        start = EmptyStartEvent(id="start")
        pg = ParallelGateway(id="pg")
        act1 = ServiceActivity(id="act1", component_code="debug_node")
        act2 = ServiceActivity(
            id="act2", component_code="debug_node", error_ignorable=True, timeout=5, skippable=True, retryable=True
        )
        cg1 = ConvergeGateway(id="cg1")
        eg = ExclusiveGateway(id="eg", conditions={0: "True == True", 1: "True == False"})
        act3 = ServiceActivity(id="act3", component_code="debug_node")
        act4 = ServiceActivity(id="act4", component_code="debug_node")
        cg2 = ConvergeGateway(id="cg2")
        cpg = ConditionalParallelGateway(id="cpg", conditions={0: "True == True", 1: "True == True"})
        act5 = ServiceActivity(id="act5", component_code="debug_node")
        act6 = ServiceActivity(id="act6", component_code="debug_node")
        cg3 = ConvergeGateway(id="cg3")

        sub_start = EmptyStartEvent(id="sub_start")
        sub_act1 = ServiceActivity(id="sub_act1", component_code="sub_debug_node")
        sub_act2 = ServiceActivity(id="sub_act2", component_code="sub_debug_node")
        sub_act3 = ServiceActivity(id="sub_act3", component_code="sub_debug_node")
        sub_end = EmptyEndEvent(id="sub_end")
        sub_start.extend(sub_act1).extend(sub_act2).extend(sub_act3).extend(sub_end)

        subproc = SubProcess(id="subproc", start=sub_start)
        end = EmptyEndEvent(id="end")

        start.extend(pg).connect(act1, act2).converge(cg1).extend(eg).connect(act3, act4).converge(cg2).extend(
            cpg
        ).connect(act5, act6).converge(cg3).extend(subproc).extend(end)

        # data
        act1.component.inputs.key1 = Var(type=Var.SPLICE, value="${a}")
        act1.component.inputs.key2 = Var(type=Var.SPLICE, value="${b}")
        act1.component.inputs.key3 = Var(type=Var.LAZY, value="${a}-${b}", custom_type="ip")

        act2.component.inputs.key2 = Var(type=Var.SPLICE, value="${a}")
        act2.component.inputs.key3 = Var(type=Var.SPLICE, value="${b}")

        act3.component.inputs.key3 = Var(type=Var.SPLICE, value="${a}")
        act3.component.inputs.key4 = Var(type=Var.SPLICE, value="${b}")

        act4.component.inputs.key4 = Var(type=Var.SPLICE, value="${a}")
        act4.component.inputs.key5 = Var(type=Var.SPLICE, value="${b}")

        act5.component.inputs.key5 = Var(type=Var.SPLICE, value="${a}")
        act5.component.inputs.key6 = Var(type=Var.SPLICE, value="${b}")

        act6.component.inputs.key6 = Var(type=Var.SPLICE, value="${a}")
        act6.component.inputs.key7 = Var(type=Var.SPLICE, value="${b}")

        sub_act1.component.inputs.key7 = Var(type=Var.SPLICE, value="${c}")
        sub_act1.component.inputs.key8 = Var(type=Var.SPLICE, value="${d}")

        sub_act2.component.inputs.key8 = Var(type=Var.SPLICE, value="${c}")
        sub_act2.component.inputs.key9 = Var(type=Var.SPLICE, value="${d}")

        sub_act3.component.inputs.key9 = Var(type=Var.SPLICE, value="${c}")
        sub_act3.component.inputs.key10 = Var(type=Var.SPLICE, value="${d}")

        sub_data = builder.Data()
        sub_data.inputs["${sub_a}"] = Var(type=Var.LAZY, value={"a": "${b}"}, custom_type="ip")
        sub_data.inputs["${sub_b}"] = Var(type=Var.SPLICE, value="${c}")
        sub_data.inputs["${sub_c}"] = Var(type=Var.PLAIN, value="c")
        sub_data.inputs["${sub_d}"] = Var(type=Var.PLAIN, value="")
        sub_data.inputs["${sub_e}"] = Var(type=Var.PLAIN, value="")
        sub_data.inputs["${sub_output1}"] = NodeOutput(
            source_act=sub_act1.id, source_key="key7", type=Var.PLAIN, value=""
        )
        sub_data.inputs["${sub_output2}"] = NodeOutput(
            source_act=sub_act2.id, source_key="key8", type=Var.PLAIN, value=""
        )
        sub_data.outputs = ["${sub_a}", "${sub_b}"]
        sub_params = Params(
            {"${sub_d}": Var(type=Var.SPLICE, value="${a}"), "${sub_e}": Var(type=Var.SPLICE, value="${b}")}
        )

        pipeline_data = builder.Data()
        pipeline_data.inputs["${a}"] = Var(type=Var.LAZY, value=["${b}", "${c}_${d}"], custom_type="ip")
        pipeline_data.inputs["${b}"] = Var(type=Var.SPLICE, value="${e}_2")
        pipeline_data.inputs["${c}"] = Var(type=Var.SPLICE, value="${e}_${f}")
        pipeline_data.inputs["${d}"] = Var(type=Var.PLAIN, value="ab")
        pipeline_data.inputs["${e}"] = Var(type=Var.PLAIN, value="cd")
        pipeline_data.inputs["${f}"] = Var(type=Var.PLAIN, value="ef")
        pipeline_data.inputs["${g}"] = Var(type=Var.SPLICE, value="1 + ${h}")
        pipeline_data.inputs["${h}"] = Var(type=Var.SPLICE, value="${f}-${f}")
        pipeline_data.inputs["${output1}"] = NodeOutput(source_act=act1.id, source_key="key1", type=Var.PLAIN, value="")
        pipeline_data.inputs["${output2}"] = NodeOutput(source_act=act2.id, source_key="key2", type=Var.PLAIN, value="")
        pipeline_data.outputs = ["${a}", "${d}", "${g}"]

        subproc.data = sub_data
        subproc.params = sub_params
        pipeline = build_tree(start, id="pipeline", data=pipeline_data)
        validator.validate_and_process_pipeline(pipeline)

        # assertion
        process_id = self.runtime.prepare_run_pipeline(pipeline, {"k": "v"})
        process = Process.objects.get(id=process_id)
        self.assertEqual(process.root_pipeline_id, pipeline["id"])
        self.assertEqual(process.queue, "")
        self.assertEqual(process.priority, 100)

        nodes = {node.node_id: node for node in Node.objects.all()}
        datas = {data.node_id: data for data in Data.objects.all()}
        context_values = {}
        for cv in ContextValue.objects.all():
            context_values.setdefault(cv.pipeline_id, {})[cv.key] = cv
        context_outputs = {co.pipeline_id: co for co in ContextOutputs.objects.all()}

        self.assertEqual(len(nodes), 20)
        self.assertEqual(len(datas), 11)
        self.assertEqual(len(context_values["pipeline"]), 9)
        self.assertEqual(len(context_values["subproc"]), 5)
        self.assertEqual(len(context_outputs), 2)

        # node
        self.assertEqual(
            json.loads(nodes["start"].detail),
            {
                "id": "start",
                "type": NodeType.EmptyStartEvent.value,
                "targets": {pipeline["start_event"]["outgoing"]: "pg"},
                "root_pipeline_id": "pipeline",
                "parent_pipeline_id": "pipeline",
                "can_skip": True,
                "can_retry": True,
            },
        )
        self.assertEqual(
            json.loads(nodes["pg"].detail),
            {
                "id": "pg",
                "type": NodeType.ParallelGateway.value,
                "targets": {
                    flow_id: pipeline["flows"][flow_id]["target"] for flow_id in pipeline["gateways"]["pg"]["outgoing"]
                },
                "root_pipeline_id": "pipeline",
                "parent_pipeline_id": "pipeline",
                "converge_gateway_id": "cg1",
                "can_skip": False,
                "can_retry": True,
            },
        )
        self.assertEqual(
            json.loads(nodes["act1"].detail),
            {
                "id": "act1",
                "type": NodeType.ServiceActivity.value,
                "targets": {pipeline["activities"]["act1"]["outgoing"]: "cg1"},
                "root_pipeline_id": "pipeline",
                "parent_pipeline_id": "pipeline",
                "can_skip": True,
                "can_retry": True,
                "code": "debug_node",
                "version": "legacy",
                "timeout": None,
                "error_ignorable": False,
            },
        )
        self.assertEqual(
            json.loads(nodes["act2"].detail),
            {
                "id": "act2",
                "type": NodeType.ServiceActivity.value,
                "targets": {pipeline["activities"]["act2"]["outgoing"]: "cg1"},
                "root_pipeline_id": "pipeline",
                "parent_pipeline_id": "pipeline",
                "can_skip": True,
                "can_retry": True,
                "code": "debug_node",
                "version": "legacy",
                "timeout": 5,
                "error_ignorable": True,
            },
        )
        self.assertEqual(
            json.loads(nodes["cg1"].detail),
            {
                "id": "cg1",
                "type": NodeType.ConvergeGateway.value,
                "targets": {pipeline["gateways"]["cg1"]["outgoing"]: "eg"},
                "root_pipeline_id": "pipeline",
                "parent_pipeline_id": "pipeline",
                "can_skip": False,
                "can_retry": True,
            },
        )
        self.assertEqual(
            json.loads(nodes["eg"].detail),
            {
                "id": "eg",
                "type": NodeType.ExclusiveGateway.value,
                "targets": {
                    flow_id: pipeline["flows"][flow_id]["target"] for flow_id in pipeline["gateways"]["eg"]["outgoing"]
                },
                "root_pipeline_id": "pipeline",
                "parent_pipeline_id": "pipeline",
                "can_skip": True,
                "can_retry": True,
                "conditions": [
                    {
                        "name": flow_id,
                        "evaluation": cond["evaluate"],
                        "target_id": pipeline["flows"][flow_id]["target"],
                        "flow_id": flow_id,
                    }
                    for flow_id, cond in pipeline["gateways"]["eg"]["conditions"].items()
                ],
            },
        )
        self.assertEqual(
            json.loads(nodes["act3"].detail),
            {
                "id": "act3",
                "type": NodeType.ServiceActivity.value,
                "targets": {pipeline["activities"]["act3"]["outgoing"]: "cg2"},
                "root_pipeline_id": "pipeline",
                "parent_pipeline_id": "pipeline",
                "can_skip": True,
                "can_retry": True,
                "code": "debug_node",
                "version": "legacy",
                "timeout": None,
                "error_ignorable": False,
            },
        )
        self.assertEqual(
            json.loads(nodes["act4"].detail),
            {
                "id": "act4",
                "type": NodeType.ServiceActivity.value,
                "targets": {pipeline["activities"]["act4"]["outgoing"]: "cg2"},
                "root_pipeline_id": "pipeline",
                "parent_pipeline_id": "pipeline",
                "can_skip": True,
                "can_retry": True,
                "code": "debug_node",
                "version": "legacy",
                "timeout": None,
                "error_ignorable": False,
            },
        )
        self.assertEqual(
            json.loads(nodes["cg2"].detail),
            {
                "id": "cg2",
                "type": NodeType.ConvergeGateway.value,
                "targets": {pipeline["gateways"]["cg2"]["outgoing"]: "cpg"},
                "root_pipeline_id": "pipeline",
                "parent_pipeline_id": "pipeline",
                "can_skip": False,
                "can_retry": True,
            },
        )
        self.assertEqual(
            json.loads(nodes["cpg"].detail),
            {
                "id": "cpg",
                "type": NodeType.ConditionalParallelGateway.value,
                "targets": {
                    flow_id: pipeline["flows"][flow_id]["target"] for flow_id in pipeline["gateways"]["cpg"]["outgoing"]
                },
                "root_pipeline_id": "pipeline",
                "parent_pipeline_id": "pipeline",
                "can_skip": False,
                "can_retry": True,
                "conditions": [
                    {
                        "name": flow_id,
                        "evaluation": cond["evaluate"],
                        "target_id": pipeline["flows"][flow_id]["target"],
                        "flow_id": flow_id,
                    }
                    for flow_id, cond in pipeline["gateways"]["cpg"]["conditions"].items()
                ],
                "converge_gateway_id": "cg3",
            },
        )
        self.assertEqual(
            json.loads(nodes["act5"].detail),
            {
                "id": "act5",
                "type": NodeType.ServiceActivity.value,
                "targets": {pipeline["activities"]["act5"]["outgoing"]: "cg3"},
                "root_pipeline_id": "pipeline",
                "parent_pipeline_id": "pipeline",
                "can_skip": True,
                "can_retry": True,
                "code": "debug_node",
                "version": "legacy",
                "timeout": None,
                "error_ignorable": False,
            },
        )
        self.assertEqual(
            json.loads(nodes["act6"].detail),
            {
                "id": "act6",
                "type": NodeType.ServiceActivity.value,
                "targets": {pipeline["activities"]["act6"]["outgoing"]: "cg3"},
                "root_pipeline_id": "pipeline",
                "parent_pipeline_id": "pipeline",
                "can_skip": True,
                "can_retry": True,
                "code": "debug_node",
                "version": "legacy",
                "timeout": None,
                "error_ignorable": False,
            },
        )
        self.assertEqual(
            json.loads(nodes["cg3"].detail),
            {
                "id": "cg3",
                "type": NodeType.ConvergeGateway.value,
                "targets": {pipeline["gateways"]["cg3"]["outgoing"]: "subproc"},
                "root_pipeline_id": "pipeline",
                "parent_pipeline_id": "pipeline",
                "can_skip": False,
                "can_retry": True,
            },
        )
        self.assertEqual(
            json.loads(nodes["subproc"].detail),
            {
                "id": "subproc",
                "type": NodeType.SubProcess.value,
                "targets": {pipeline["activities"]["subproc"]["outgoing"]: "end"},
                "root_pipeline_id": "pipeline",
                "parent_pipeline_id": "pipeline",
                "can_skip": False,
                "can_retry": True,
                "start_event_id": "sub_start",
            },
        )
        self.assertEqual(
            json.loads(nodes["sub_start"].detail),
            {
                "id": "sub_start",
                "type": NodeType.EmptyStartEvent.value,
                "targets": {pipeline["activities"]["subproc"]["pipeline"]["start_event"]["outgoing"]: "sub_act1"},
                "root_pipeline_id": "pipeline",
                "parent_pipeline_id": "subproc",
                "can_skip": True,
                "can_retry": True,
            },
        )
        self.assertEqual(
            json.loads(nodes["sub_act1"].detail),
            {
                "id": "sub_act1",
                "type": NodeType.ServiceActivity.value,
                "targets": {
                    pipeline["activities"]["subproc"]["pipeline"]["activities"]["sub_act1"]["outgoing"]: "sub_act2"
                },
                "root_pipeline_id": "pipeline",
                "parent_pipeline_id": "subproc",
                "can_skip": True,
                "can_retry": True,
                "code": "sub_debug_node",
                "version": "legacy",
                "timeout": None,
                "error_ignorable": False,
            },
        )
        self.assertEqual(
            json.loads(nodes["sub_act2"].detail),
            {
                "id": "sub_act2",
                "type": NodeType.ServiceActivity.value,
                "targets": {
                    pipeline["activities"]["subproc"]["pipeline"]["activities"]["sub_act2"]["outgoing"]: "sub_act3"
                },
                "root_pipeline_id": "pipeline",
                "parent_pipeline_id": "subproc",
                "can_skip": True,
                "can_retry": True,
                "code": "sub_debug_node",
                "version": "legacy",
                "timeout": None,
                "error_ignorable": False,
            },
        )
        self.assertEqual(
            json.loads(nodes["sub_act3"].detail),
            {
                "id": "sub_act3",
                "type": NodeType.ServiceActivity.value,
                "targets": {
                    pipeline["activities"]["subproc"]["pipeline"]["activities"]["sub_act3"]["outgoing"]: "sub_end"
                },
                "root_pipeline_id": "pipeline",
                "parent_pipeline_id": "subproc",
                "can_skip": True,
                "can_retry": True,
                "code": "sub_debug_node",
                "version": "legacy",
                "timeout": None,
                "error_ignorable": False,
            },
        )
        self.assertEqual(
            json.loads(nodes["sub_end"].detail),
            {
                "id": "sub_end",
                "type": NodeType.EmptyEndEvent.value,
                "targets": {},
                "root_pipeline_id": "pipeline",
                "parent_pipeline_id": "subproc",
                "can_skip": False,
                "can_retry": True,
            },
        )
        self.assertEqual(
            json.loads(nodes["end"].detail),
            {
                "id": "end",
                "type": NodeType.EmptyEndEvent.value,
                "targets": {},
                "root_pipeline_id": "pipeline",
                "parent_pipeline_id": "pipeline",
                "can_skip": False,
                "can_retry": True,
            },
        )

        # data
        self.assertEqual(json.loads(datas["pipeline"].inputs), {"k": {"need_render": False, "value": "v"}})

        self.assertEqual(
            json.loads(datas["act1"].inputs),
            {
                "key1": {"need_render": True, "value": "${a}"},
                "key2": {"need_render": True, "value": "${b}"},
                "key3": {"need_render": True, "value": "${key3_act1}"},
            },
        )
        self.assertEqual(json.loads(datas["act1"].outputs), {"key1": "${output1}"})

        self.assertEqual(
            json.loads(datas["act2"].inputs),
            {"key2": {"need_render": True, "value": "${a}"}, "key3": {"need_render": True, "value": "${b}"}},
        )
        self.assertEqual(json.loads(datas["act2"].outputs), {"key2": "${output2}"})

        self.assertEqual(
            json.loads(datas["act3"].inputs),
            {"key3": {"need_render": True, "value": "${a}"}, "key4": {"need_render": True, "value": "${b}"}},
        )

        self.assertEqual(
            json.loads(datas["act4"].inputs),
            {"key4": {"need_render": True, "value": "${a}"}, "key5": {"need_render": True, "value": "${b}"}},
        )

        self.assertEqual(
            json.loads(datas["act5"].inputs),
            {"key5": {"need_render": True, "value": "${a}"}, "key6": {"need_render": True, "value": "${b}"}},
        )

        self.assertEqual(
            json.loads(datas["act6"].inputs),
            {"key6": {"need_render": True, "value": "${a}"}, "key7": {"need_render": True, "value": "${b}"}},
        )

        self.assertEqual(
            json.loads(datas["sub_act1"].inputs),
            {"key7": {"need_render": True, "value": "${c}"}, "key8": {"need_render": True, "value": "${d}"}},
        )
        self.assertEqual(json.loads(datas["sub_act1"].outputs), {"key7": "${sub_output1}"})

        self.assertEqual(
            json.loads(datas["sub_act2"].inputs),
            {"key8": {"need_render": True, "value": "${c}"}, "key9": {"need_render": True, "value": "${d}"}},
        )
        self.assertEqual(json.loads(datas["sub_act2"].outputs), {"key8": "${sub_output2}"})

        self.assertEqual(
            json.loads(datas["sub_act3"].inputs),
            {"key9": {"need_render": True, "value": "${c}"}, "key10": {"need_render": True, "value": "${d}"}},
        )

        self.assertEqual(
            json.loads(datas["subproc"].inputs),
            {"${sub_d}": {"need_render": True, "value": "${a}"}, "${sub_e}": {"need_render": True, "value": "${b}"}},
        )
        self.assertEqual(json.loads(datas["subproc"].outputs), {})

        # context outputs
        self.assertEqual(json.loads(context_outputs["pipeline"].outputs), ["${a}", "${d}", "${g}"])
        self.assertEqual(json.loads(context_outputs["subproc"].outputs), ["${sub_a}", "${sub_b}"])

        # context values
        key = "${a}"
        self.assertEqual(
            {
                "pipeline_id": "pipeline",
                "key": context_values["pipeline"][key].key,
                "type": context_values["pipeline"][key].type,
                "serializer": context_values["pipeline"][key].serializer,
                "value": json.loads(context_values["pipeline"][key].value),
                "references": set(json.loads(context_values["pipeline"][key].references)),
            },
            {
                "pipeline_id": "pipeline",
                "key": key,
                "type": 3,
                "serializer": "json",
                "value": ["${b}", "${c}_${d}"],
                "references": {"${b}", "${c}", "${d}", "${e}", "${f}"},
            },
        )

        key = "${b}"
        self.assertEqual(
            {
                "pipeline_id": "pipeline",
                "key": context_values["pipeline"][key].key,
                "type": context_values["pipeline"][key].type,
                "serializer": context_values["pipeline"][key].serializer,
                "value": json.loads(context_values["pipeline"][key].value),
                "references": set(json.loads(context_values["pipeline"][key].references)),
            },
            {
                "pipeline_id": "pipeline",
                "key": key,
                "type": 2,
                "serializer": "json",
                "value": "${e}_2",
                "references": {"${e}"},
            },
        )

        key = "${c}"
        self.assertEqual(
            {
                "pipeline_id": "pipeline",
                "key": context_values["pipeline"][key].key,
                "type": context_values["pipeline"][key].type,
                "serializer": context_values["pipeline"][key].serializer,
                "value": json.loads(context_values["pipeline"][key].value),
                "references": set(json.loads(context_values["pipeline"][key].references)),
            },
            {
                "pipeline_id": "pipeline",
                "key": key,
                "type": 2,
                "serializer": "json",
                "value": "${e}_${f}",
                "references": {"${e}", "${f}"},
            },
        )

        key = "${d}"
        self.assertEqual(
            {
                "pipeline_id": "pipeline",
                "key": context_values["pipeline"][key].key,
                "type": context_values["pipeline"][key].type,
                "serializer": context_values["pipeline"][key].serializer,
                "value": json.loads(context_values["pipeline"][key].value),
                "references": set(json.loads(context_values["pipeline"][key].references)),
            },
            {
                "pipeline_id": "pipeline",
                "key": key,
                "type": 1,
                "serializer": "json",
                "value": "ab",
                "references": set(),
            },
        )

        key = "${e}"
        self.assertEqual(
            {
                "pipeline_id": "pipeline",
                "key": context_values["pipeline"][key].key,
                "type": context_values["pipeline"][key].type,
                "serializer": context_values["pipeline"][key].serializer,
                "value": json.loads(context_values["pipeline"][key].value),
                "references": set(json.loads(context_values["pipeline"][key].references)),
            },
            {
                "pipeline_id": "pipeline",
                "key": key,
                "type": 1,
                "serializer": "json",
                "value": "cd",
                "references": set(),
            },
        )

        key = "${f}"
        self.assertEqual(
            {
                "pipeline_id": "pipeline",
                "key": context_values["pipeline"][key].key,
                "type": context_values["pipeline"][key].type,
                "serializer": context_values["pipeline"][key].serializer,
                "value": json.loads(context_values["pipeline"][key].value),
                "references": set(json.loads(context_values["pipeline"][key].references)),
            },
            {
                "pipeline_id": "pipeline",
                "key": key,
                "type": 1,
                "serializer": "json",
                "value": "ef",
                "references": set(),
            },
        )

        key = "${g}"
        self.assertEqual(
            {
                "pipeline_id": "pipeline",
                "key": context_values["pipeline"][key].key,
                "type": context_values["pipeline"][key].type,
                "serializer": context_values["pipeline"][key].serializer,
                "value": json.loads(context_values["pipeline"][key].value),
                "references": set(json.loads(context_values["pipeline"][key].references)),
            },
            {
                "pipeline_id": "pipeline",
                "key": key,
                "type": 2,
                "serializer": "json",
                "value": "1 + ${h}",
                "references": {"${h}", "${f}"},
            },
        )

        key = "${h}"
        self.assertEqual(
            {
                "pipeline_id": "pipeline",
                "key": context_values["pipeline"][key].key,
                "type": context_values["pipeline"][key].type,
                "serializer": context_values["pipeline"][key].serializer,
                "value": json.loads(context_values["pipeline"][key].value),
                "references": set(json.loads(context_values["pipeline"][key].references)),
            },
            {
                "pipeline_id": "pipeline",
                "key": key,
                "type": 2,
                "serializer": "json",
                "value": "${f}-${f}",
                "references": {"${f}"},
            },
        )

        key = "${key3_act1}"
        self.assertEqual(
            {
                "pipeline_id": "pipeline",
                "key": context_values["pipeline"][key].key,
                "type": context_values["pipeline"][key].type,
                "serializer": context_values["pipeline"][key].serializer,
                "value": json.loads(context_values["pipeline"][key].value),
                "references": set(json.loads(context_values["pipeline"][key].references)),
            },
            {
                "pipeline_id": "pipeline",
                "key": key,
                "type": 3,
                "serializer": "json",
                "value": "${a}-${b}",
                "references": {"${b}", "${f}", "${a}", "${d}", "${c}", "${e}"},
            },
        )

        key = "${sub_a}"
        self.assertEqual(
            {
                "pipeline_id": "subproc",
                "key": context_values["subproc"][key].key,
                "type": context_values["subproc"][key].type,
                "serializer": context_values["subproc"][key].serializer,
                "value": json.loads(context_values["subproc"][key].value),
                "references": set(json.loads(context_values["subproc"][key].references)),
            },
            {
                "pipeline_id": "subproc",
                "key": key,
                "type": 3,
                "serializer": "json",
                "value": {"a": "${b}"},
                "references": {"${b}"},
            },
        )

        key = "${sub_b}"
        self.assertEqual(
            {
                "pipeline_id": "subproc",
                "key": context_values["subproc"][key].key,
                "type": context_values["subproc"][key].type,
                "serializer": context_values["subproc"][key].serializer,
                "value": json.loads(context_values["subproc"][key].value),
                "references": set(json.loads(context_values["subproc"][key].references)),
            },
            {
                "pipeline_id": "subproc",
                "key": key,
                "type": 2,
                "serializer": "json",
                "value": "${c}",
                "references": {"${c}"},
            },
        )

        key = "${sub_c}"
        self.assertEqual(
            {
                "pipeline_id": "subproc",
                "key": context_values["subproc"][key].key,
                "type": context_values["subproc"][key].type,
                "serializer": context_values["subproc"][key].serializer,
                "value": json.loads(context_values["subproc"][key].value),
                "references": set(json.loads(context_values["subproc"][key].references)),
            },
            {"pipeline_id": "subproc", "key": key, "type": 1, "serializer": "json", "value": "c", "references": set()},
        )

        key = "${sub_d}"
        self.assertEqual(
            {
                "pipeline_id": "subproc",
                "key": context_values["subproc"][key].key,
                "type": context_values["subproc"][key].type,
                "serializer": context_values["subproc"][key].serializer,
                "value": json.loads(context_values["subproc"][key].value),
                "references": set(json.loads(context_values["subproc"][key].references)),
            },
            {"pipeline_id": "subproc", "key": key, "type": 1, "serializer": "json", "value": "", "references": set()},
        )

        key = "${sub_e}"
        self.assertEqual(
            {
                "pipeline_id": "subproc",
                "key": context_values["subproc"][key].key,
                "type": context_values["subproc"][key].type,
                "serializer": context_values["subproc"][key].serializer,
                "value": json.loads(context_values["subproc"][key].value),
                "references": set(json.loads(context_values["subproc"][key].references)),
            },
            {"pipeline_id": "subproc", "key": key, "type": 1, "serializer": "json", "value": "", "references": set()},
        )
