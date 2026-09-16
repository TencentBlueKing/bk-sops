# -*- coding: utf-8 -*-
import csv
import datetime
import io
import tempfile
from pathlib import Path

import factory
from django.core.management import CommandError
from django.db.models import signals
from django.test import TestCase
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule
from django_celery_beat.models import PeriodicTask as CeleryPeriodicTask
from pipeline.contrib.periodic_task.models import PeriodicTask as PipelinePeriodicTask
from pipeline.models import PipelineInstance, PipelineTemplate, Snapshot, TemplateRelationship
from pipeline.utils.uniqid import uniqid

from gcloud.analysis_statistics.management.commands.export_mako_expression_inventory import Command
from gcloud.clocked_task.models import ClockedTask
from gcloud.common_template.models import CommonTemplate
from gcloud.constants import COMMON, PROJECT
from gcloud.core.models import Business, Project
from gcloud.periodictask.models import PeriodicTask
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.tasktmpl3.models import TaskTemplate


class ExportMakoExpressionInventoryTenantTestCase(TestCase):
    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def setUp(self):
        self.business = Business.objects.create(
            cc_id=1001, cc_name="业务 A", cc_owner="0", cc_company="0", tenant_id="tenant-a"
        )
        self.project_a = Project.objects.create(name="项目 A", bk_biz_id=1001, tenant_id="tenant-a")
        # A CMDB ID is not a tenant boundary; project ownership must still be checked.
        self.project_b = Project.objects.create(name="项目 B", bk_biz_id=1001, tenant_id="tenant-b")
        self.template_a = self._template(self.project_a)
        self.template_b = self._template(self.project_b)
        self.common_a = self._template(tenant_id="tenant-a")
        self.common_b = self._template(tenant_id="tenant-b")

    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def _template(self, project=None, tenant_id=None):
        snapshot = Snapshot.objects.create_snapshot(
            {"constants": {"${value}": {"value": "${value}"}}, "activities": {}, "gateways": {}}
        )
        pipeline = PipelineTemplate.objects.create(
            template_id=uniqid(), name="template", creator="tester", snapshot=snapshot
        )
        if project is not None:
            return TaskTemplate.objects.create(project=project, pipeline_template=pipeline)
        return CommonTemplate.objects.create(tenant_id=tenant_id, pipeline_template=pipeline)

    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def _task(self, template, project, age_days=0, tree=None):
        snapshot = template.pipeline_template.snapshot if tree is None else Snapshot.objects.create_snapshot(tree)
        instance = PipelineInstance.objects.create(
            instance_id=uniqid(),
            name=project.name,
            creator="tester",
            snapshot=snapshot,
            execution_snapshot=snapshot,
            is_started=True,
            start_time=timezone.now() - datetime.timedelta(days=age_days),
        )
        return TaskFlowInstance.objects.create(
            project=project,
            pipeline_instance=instance,
            template_id=str(template.id),
            template_source=COMMON if isinstance(template, CommonTemplate) else PROJECT,
            current_flow="task_execute",
        )

    def _options(self, output, **overrides):
        options = {
            "output": str(output),
            "source": "all",
            "tenant_id": "tenant-a",
            "hits_only": False,
            "include_deleted": False,
            "skip_subprocess_exec": False,
            "verify_subprocess_exec": False,
            "max_templates": 0,
            "progress_every": 50,
            "query_chunk_size": 100,
        }
        options.update(overrides)
        return options

    def _export(self, **options):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "mako.csv"
            Command(stdout=io.StringIO()).handle(**self._options(output, **options))
            with output.open(encoding="utf-8-sig") as fh:
                return list(csv.DictReader(fh))

    def _common_row(self, **options):
        return self._export(source="common", **options)[0]

    def test_missing_or_blank_tenant_does_not_write_export(self):
        for tenant in (None, "", " "):
            with self.subTest(tenant=tenant), tempfile.TemporaryDirectory() as tmp:
                output = Path(tmp) / "mako.csv"
                with self.assertRaises(CommandError):
                    Command(stdout=io.StringIO()).handle(**self._options(output, tenant_id=tenant))
                self.assertFalse(output.exists())

    def test_all_sources_only_export_selected_tenant(self):
        rows = self._export()
        self.assertEqual(
            {(row["流程来源"], row["流程模板ID"]) for row in rows},
            {(PROJECT, str(self.template_a.id)), (COMMON, str(self.common_a.id))},
        )
        self.assertEqual({row["租户ID"] for row in rows}, {"tenant-a"})

    def test_biz_filter_cannot_select_other_tenant_project(self):
        rows = self._export(source="project", bk_biz_id="1001")
        self.assertEqual({row["项目ID"] for row in rows}, {str(self.project_a.id)})

    def test_foreign_project_filter_does_not_fall_back_to_all_projects(self):
        with self.assertRaises(CommandError):
            self._export(source="project", project_id=str(self.project_b.id))

    def test_unknown_tenant_does_not_fall_back_to_all_templates(self):
        with self.assertRaises(CommandError):
            self._export(tenant_id="unknown")

    def test_tenant_without_projects_can_export_its_common_template(self):
        common = self._template(tenant_id="tenant-c")
        rows = self._export(tenant_id="tenant-c")
        self.assertEqual([(row["流程来源"], row["流程模板ID"]) for row in rows], [(COMMON, str(common.id))])

    def test_business_name_must_belong_to_selected_tenant(self):
        Business.objects.filter(pk=self.business.pk).update(tenant_id="tenant-b")
        rows = self._export(source="project")
        self.assertEqual(rows[0]["业务名称"], "")

    def test_common_execution_count_and_latest_task_stay_in_tenant(self):
        own_task = self._task(self.common_a, self.project_a, age_days=2)
        self._task(self.common_a, self.project_b)
        row = self._common_row()
        self.assertEqual(row["直接执行次数"], "1")
        self.assertEqual(row["最近执行任务ID"], str(own_task.id))
        self.assertEqual(row["最近执行任务名称"], "项目 A")

    def test_foreign_execution_does_not_mark_common_template_as_executed(self):
        self._task(self.common_a, self.project_b)
        row = self._common_row()
        self.assertEqual(row["直接执行次数"], "0")
        self.assertEqual(row["最近执行任务ID"], "")

    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def test_periodic_and_clocked_flags_only_include_selected_tenant_projects(self):
        clocked = ClockedTask.objects.create(
            project_id=self.project_b.id,
            task_name="foreign",
            template_id=self.common_a.id,
            template_name="common",
            template_source=COMMON,
            creator="tester",
            plan_start_time=timezone.now(),
        )
        celery_task = CeleryPeriodicTask.objects.create(
            name=uniqid(), task="test", enabled=True, crontab=CrontabSchedule.objects.create()
        )
        pipeline_task = PipelinePeriodicTask.objects.create(
            name="periodic", cron="{}", snapshot=self.common_a.pipeline_template.snapshot, celery_task=celery_task
        )
        periodic = PeriodicTask(
            project=self.project_b, task=pipeline_task, template_id=str(self.common_a.id), template_source=COMMON
        )
        periodic.save()
        row = self._common_row()
        self.assertEqual(row["是否有启用周期任务"], "否")
        self.assertEqual(row["是否有未启动计划任务"], "否")

        PeriodicTask.objects.filter(id=periodic.id).update(project=self.project_a)
        ClockedTask.objects.filter(id=clocked.id).update(project_id=self.project_a.id)
        row = self._common_row()
        self.assertEqual(row["是否有启用周期任务"], "是")
        self.assertEqual(row["是否有未启动计划任务"], "是")

    def test_subprocess_execution_ignores_foreign_parent_templates_and_tasks(self):
        for parent in (self.template_a, self.template_b, self.common_b):
            TemplateRelationship.objects.create(
                ancestor_template_id=parent.pipeline_template_id,
                descendant_template_id=self.common_a.pipeline_template_id,
                subprocess_node_id=uniqid(),
                version="test",
            )
        tree = {
            "activities": {
                "sub": {"type": "SubProcess", "template_id": self.common_a.pipeline_template_id, "pipeline": {}}
            }
        }
        own_task = self._task(self.template_a, self.project_a, age_days=2, tree=tree)
        self._task(self.template_a, self.project_b, tree=tree)
        # Even a foreign template referenced by a task in the selected tenant is excluded.
        self._task(self.template_b, self.project_a, tree=tree)
        self._task(self.common_b, self.project_a, tree=tree)
        for verify in (False, True):
            with self.subTest(verify=verify):
                row = self._common_row(verify_subprocess_exec=verify)
                self.assertEqual(row["最近执行任务ID"], str(own_task.id))
                self.assertEqual(row["最近执行方式"], "作为子流程执行")
