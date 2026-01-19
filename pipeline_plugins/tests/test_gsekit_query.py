# -*- coding: utf-8 -*-
import json
from unittest.mock import MagicMock, patch

from django.test import RequestFactory, TestCase

from pipeline_plugins.components.query.sites.open.gsekit import gsekit_get_config_template_list


class GsekitQueryTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = MagicMock()
        self.user.username = "admin"
        self.user.tenant_id = "tenant"

    @patch("pipeline_plugins.components.query.sites.open.gsekit.get_client_by_username")
    def test_gsekit_get_config_template_list(self, mock_get_client):
        request = self.factory.get("/")
        request.user = self.user

        client = MagicMock()
        mock_get_client.return_value = client

        client.api.config_template_list.return_value = [{"template_name": "t1", "config_template_id": 1}]

        response = gsekit_get_config_template_list(request, "1")

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertTrue(content["result"])
        self.assertEqual(content["data"][0]["text"], "t1")
        self.assertEqual(content["data"][0]["value"], 1)
