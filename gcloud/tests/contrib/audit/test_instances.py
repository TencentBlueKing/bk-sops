# -*- coding: utf-8 -*-
from unittest import mock

from django.test import SimpleTestCase

from gcloud.contrib.audit.instances import BaseInstance


class AuditInstanceTestCase(SimpleTestCase):
    def test_deleted_instance_uses_explicit_snapshot_id(self):
        instance = BaseInstance(mock.Mock(id=None, name="deleted"), data={"id": 101, "is_deleted": True})

        self.assertEqual(instance.instance_id, 101)
