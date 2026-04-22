# -*- coding: utf-8 -*-
from django.test import SimpleTestCase

from pipeline_plugins.components.collections.subprocess_plugin.v1_0_0 import SubprocessPluginService


class SubprocessPluginServiceTestCase(SimpleTestCase):
    def test_callback_lock_retryable_only_for_success_callback(self):
        service = SubprocessPluginService()

        self.assertFalse(service.callback_lock_retryable(None))
        self.assertFalse(service.callback_lock_retryable({}))
        self.assertFalse(service.callback_lock_retryable({"task_success": False}))
        self.assertTrue(service.callback_lock_retryable({"task_success": True}))
