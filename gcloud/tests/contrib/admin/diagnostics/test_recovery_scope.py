# -*- coding: utf-8 -*-
from unittest import mock

from django.test import TestCase, override_settings

from gcloud.contrib.admin.diagnostics import recovery_scope


class RecoveryScopeTest(TestCase):
    def resolve(self, project_id):
        with mock.patch.object(recovery_scope, "TaskFlowInstance") as m_tf:
            m_tf.objects.filter.return_value.values_list.return_value.first.return_value = project_id
            return recovery_scope.in_recovery_scope("root-1"), m_tf

    @override_settings(DIAGNOSTICS_RECOVERY_PROJECT_IDS=[])
    def test_empty_whitelist_denies_without_query(self):
        allowed, m_tf = self.resolve(1)
        self.assertFalse(allowed)
        m_tf.objects.filter.assert_not_called()

    @override_settings(DIAGNOSTICS_RECOVERY_PROJECT_IDS=["1", "2"])
    def test_only_whitelisted_projects_are_allowed(self):
        allowed, m_tf = self.resolve(2)
        self.assertTrue(allowed)
        m_tf.objects.filter.assert_called_once_with(pipeline_instance__instance_id="root-1")
        m_tf.objects.filter.return_value.values_list.assert_called_once_with("project_id", flat=True)
        self.assertFalse(self.resolve(3)[0])

    @override_settings(DIAGNOSTICS_RECOVERY_PROJECT_IDS=["*"])
    def test_star_allows_tasks_of_any_project(self):
        self.assertTrue(self.resolve(9)[0])
        self.assertFalse(self.resolve(None)[0])

    @override_settings(DIAGNOSTICS_RECOVERY_PROJECT_IDS="1, 2")
    def test_string_whitelist_is_parsed(self):
        self.assertTrue(self.resolve(1)[0])

    @override_settings(DIAGNOSTICS_RECOVERY_PROJECT_IDS=["*"])
    def test_unknown_root_is_denied(self):
        self.assertFalse(recovery_scope.in_recovery_scope("no-such-root"))
