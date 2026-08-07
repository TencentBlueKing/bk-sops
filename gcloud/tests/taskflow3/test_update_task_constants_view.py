# -*- coding: utf-8 -*-
from types import SimpleNamespace
from unittest import mock

import factory
from django.db.models import signals
from django.test import TestCase, override_settings
from pipeline.models import PipelineInstance, PipelineTemplate, Snapshot

from gcloud.taskflow3.apis.drf.viewsets.update_task_constants import UpdateTaskConstantsView
from gcloud.taskflow3.models import TaskFlowInstance


class UpdateTaskConstantsViewTestCase(TestCase):
    @factory.django.mute_signals(signals.pre_save, signals.post_save)
    def setUp(self):
        snapshot = Snapshot.objects.create_snapshot({})
        template = PipelineTemplate.objects.create(template_id="template", creator="admin", snapshot=snapshot)
        pipeline_instance = PipelineInstance.objects.create(
            instance_id="instance",
            creator="admin",
            executor="admin",
            snapshot=snapshot,
            template=template,
        )
        self.task = TaskFlowInstance.objects.create(
            pipeline_instance=pipeline_instance,
            template_id=template.id,
            current_flow="execute_task",
        )

    @override_settings(ENABLE_BK_AUDIT=True)
    @mock.patch.object(
        TaskFlowInstance,
        "set_task_constants",
        return_value={"result": False, "message": "not changed", "data": ""},
    )
    @mock.patch("gcloud.taskflow3.apis.drf.viewsets.update_task_constants.get_audit_snapshot")
    def test_audit_snapshot_receives_fully_loaded_task(self, get_audit_snapshot, set_task_constants):
        request = SimpleNamespace(data={"constants": {}, "meta_constants": {}}, user=SimpleNamespace(username="admin"))

        UpdateTaskConstantsView().post(request, self.task.id)

        audit_task = get_audit_snapshot.call_args[0][1]
        self.assertEqual(audit_task.get_deferred_fields(), set())
        self.assertIn("pipeline_instance", audit_task._state.fields_cache)
