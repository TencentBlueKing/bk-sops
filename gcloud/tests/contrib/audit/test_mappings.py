# -*- coding: utf-8 -*-
from django.test import SimpleTestCase

from gcloud.common_template.models import CommonTemplate
from gcloud.constants import BUSINESS, COMMON, ONETIME, PROJECT
from gcloud.contrib.audit.mappings import (
    get_periodic_task_create_action,
    get_task_create_action,
    get_template_audit_meta,
)
from gcloud.iam_auth import IAMMeta
from gcloud.tasktmpl3.models import TaskTemplate


class AuditMappingsTestCase(SimpleTestCase):
    def test_task_create_actions_use_existing_actions(self):
        self.assertEqual(get_task_create_action(PROJECT), IAMMeta.FLOW_CREATE_TASK_ACTION)
        self.assertEqual(get_task_create_action(BUSINESS), IAMMeta.FLOW_CREATE_TASK_ACTION)
        self.assertEqual(get_task_create_action(COMMON), IAMMeta.COMMON_FLOW_CREATE_TASK_ACTION)
        self.assertEqual(get_task_create_action(ONETIME), IAMMeta.PROJECT_FAST_CREATE_TASK_ACTION)
        self.assertEqual(get_task_create_action(PROJECT, "app_maker"), IAMMeta.MINI_APP_CREATE_TASK_ACTION)
        self.assertIsNone(get_task_create_action("unknown"))

    def test_periodic_create_actions_distinguish_template_source(self):
        self.assertEqual(get_periodic_task_create_action(PROJECT), IAMMeta.FLOW_CREATE_PERIODIC_TASK_ACTION)
        self.assertEqual(get_periodic_task_create_action(COMMON), IAMMeta.COMMON_FLOW_CREATE_PERIODIC_TASK_ACTION)
        self.assertIsNone(get_periodic_task_create_action("unknown"))

    def test_template_meta_uses_existing_resources(self):
        self.assertEqual(
            get_template_audit_meta(TaskTemplate),
            (IAMMeta.FLOW_CREATE_ACTION, IAMMeta.FLOW_DELETE_ACTION, IAMMeta.FLOW_RESOURCE),
        )
        self.assertEqual(
            get_template_audit_meta(CommonTemplate),
            (
                IAMMeta.COMMON_FLOW_CREATE_ACTION,
                IAMMeta.COMMON_FLOW_DELETE_ACTION,
                IAMMeta.COMMON_FLOW_RESOURCE,
            ),
        )
