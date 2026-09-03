# -*- coding: utf-8 -*-
import csv
import tempfile
from pathlib import Path

import factory
from django.core.management import call_command
from django.db.models import signals
from django.test import TestCase, override_settings
from django.utils import timezone
from pipeline.models import PipelineInstance, PipelineTemplate, Snapshot
from pipeline.utils.uniqid import uniqid

from gcloud.common_template.models import CommonTemplate
from gcloud.constants import PROJECT
from gcloud.core.models import Business, Project
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.models import TaskTemplate


@override_settings(
    MAKO_SANDBOX_IMPORT_MODULES={
        "os.path": "os.path",
        "datetime": "datetime",
        "datetime.datetime": "datetime.datetime",
    }
)
class ExportMakoExpressionInventoryCommandTestCase(TestCase):
    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def setUp(self):
        self.business = Business.objects.create(cc_id=1001, cc_name="中文业务", cc_owner="0", cc_company="0")
        self.project = Project.objects.create(name="中文项目", creator="tester", bk_biz_id=self.business.cc_id)
        tree = {
            "activities": {
                "n1": {
                    "id": "n1",
                    "name": "HTTP",
                    "type": "ServiceActivity",
                    "component": {
                        "code": "bk_http_request",
                        "data": {
                            "body": {
                                "value": (
                                    '${os.path.join(work_dir, "a")} '
                                    '${"x{}".format(name)} '
                                    "${res._module} ${self.module.x}"
                                )
                            }
                        },
                    },
                }
            },
            "gateways": {},
            "constants": {"${caller}": {"value": "${caller}"}},
            "outputs": [],
            "flows": {},
        }
        self.snapshot = Snapshot.objects.create_snapshot(tree)
        self.pipeline_template = PipelineTemplate.objects.create(
            template_id=uniqid(),
            name="开区流程",
            creator="alice",
            editor="bob",
            snapshot=self.snapshot,
        )
        self.task_template = TaskTemplate.objects.create(
            project=self.project,
            pipeline_template=self.pipeline_template,
            category="OpsTools",
        )
        instance_snapshot = Snapshot.objects.create_snapshot(tree)
        self.pipeline_instance = PipelineInstance.objects.create(
            instance_id=uniqid(),
            name="开区任务",
            creator="bob",
            snapshot=instance_snapshot,
            execution_snapshot=instance_snapshot,
            is_started=True,
            start_time=timezone.now(),
        )
        self.task = TaskFlowInstance.objects.create(
            project=self.project,
            pipeline_instance=self.pipeline_instance,
            template_id=str(self.task_template.id),
            template_source=PROJECT,
            current_flow="task_execute",
        )

    def test_export_all_expressions_with_business_and_last_exec(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "mako.csv"
            call_command(
                "export_mako_expression_inventory",
                output=str(output),
                source="project",
                skip_subprocess_exec=True,
                base_url="https://apps.example.com/o/bk_sops",
            )
            rows = list(csv.DictReader(output.open(encoding="utf-8-sig")))

        exprs = {row["表达式"]: row for row in rows}
        self.assertIn('${os.path.join(work_dir, "a")}', exprs)
        self.assertIn('${"x{}".format(name)}', exprs)
        self.assertIn("${res._module}", exprs)
        self.assertIn("${caller}", exprs)
        self.assertIn("${self.module.x}", exprs)

        sample = exprs['${os.path.join(work_dir, "a")}']
        self.assertEqual(sample["业务ID"], "1001")
        self.assertEqual(sample["业务名称"], "中文业务")
        self.assertEqual(sample["项目名称"], "中文项目")
        self.assertEqual(sample["最近更新者"], "bob")
        self.assertEqual(sample["使用注入模块"], "是")
        self.assertEqual(sample["有深层属性调用"], "是")
        self.assertEqual(sample["命中安全策略"], "否")
        self.assertIn("template/view/{}/?template_id={}".format(self.project.id, self.task_template.id), sample["流程链接"])
        self.assertEqual(sample["最近执行任务ID"], str(self.task.id))
        self.assertTrue(sample["最近执行时间"])
        self.assertEqual(sample["最近执行方式"], "直接执行")
        self.assertIn("taskflow/execute/{}/?instance_id={}".format(self.project.id, self.task.id), sample["最近执行任务链接"])

        self.assertEqual(exprs['${"x{}".format(name)}']["命中无条件策略"], "是")
        self.assertEqual(exprs['${"x{}".format(name)}']["风险档位"], "无条件阻断")
        self.assertEqual(exprs['${"x{}".format(name)}']["v2引擎能匹配"], "否")
        self.assertEqual(exprs["${res._module}"]["命中白名单策略"], "否")
        self.assertEqual(exprs["${caller}"]["命中白名单策略"], "否")
        self.assertEqual(exprs["${self.module.x}"]["命中白名单策略"], "是")

    def test_hits_only_filters_policy_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "hits.csv"
            call_command(
                "export_mako_expression_inventory",
                output=str(output),
                source="project",
                hits_only=True,
                skip_subprocess_exec=True,
            )
            rows = list(csv.DictReader(output.open(encoding="utf-8-sig")))

        exprs = {row["表达式"] for row in rows}
        self.assertIn('${"x{}".format(name)}', exprs)
        self.assertIn("${self.module.x}", exprs)
        self.assertNotIn("${res._module}", exprs)
        self.assertNotIn("${caller}", exprs)
        self.assertNotIn('${os.path.join(work_dir, "a")}', exprs)

    def test_common_template_is_included(self):
        snapshot = Snapshot.objects.create_snapshot(
            {
                "constants": {"${a}": {"value": "${datetime.datetime.now()}"}},
                "activities": {},
                "gateways": {},
                "outputs": [],
                "flows": {},
            }
        )
        pipeline = PipelineTemplate.objects.create(
            template_id=uniqid(),
            name="公共流程",
            creator="carol",
            editor="dave",
            snapshot=snapshot,
        )
        CommonTemplate.objects.create(pipeline_template=pipeline)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "common.csv"
            call_command(
                "export_mako_expression_inventory",
                output=str(output),
                source="common",
                skip_subprocess_exec=True,
            )
            rows = list(csv.DictReader(output.open(encoding="utf-8-sig")))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["流程来源"], "common")
        self.assertEqual(rows[0]["使用注入模块"], "是")
        self.assertEqual(rows[0]["有深层属性调用"], "是")
        self.assertEqual(rows[0]["命中安全策略"], "否")
