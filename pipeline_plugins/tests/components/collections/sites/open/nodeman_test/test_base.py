# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import ANY, MagicMock, patch

from gcloud.conf import settings
from pipeline_plugins.components.collections.sites.open.nodeman.base import (
    NodeManAsymmetricInterceptor,
    NodeManNewBaseService,
    get_host_id_by_inner_ip,
    get_host_id_by_inner_ipv6,
    get_nodeman_public_key,
)


class NodeManUtilsTestCase(TestCase):
    def test_interceptor(self):
        self.assertTrue(NodeManAsymmetricInterceptor.after_encrypt("test").startswith("REVGQVVMVA=="))

    @patch("pipeline_plugins.components.collections.sites.open.nodeman.base.get_client_by_username")
    def test_get_host_id_by_inner_ip(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client

        # Empty list
        self.assertEqual(get_host_id_by_inner_ip("t", "u", None, 0, 1, []), {})

        # Success
        client.api.search_host_plugin.return_value = {
            "result": True,
            "data": {"list": [{"inner_ip": "1.1.1.1", "bk_host_id": 100}]},
        }
        res = get_host_id_by_inner_ip("t", "u", None, 0, 1, ["1.1.1.1"])
        self.assertEqual(res, {"1.1.1.1": 100})

        # Fail
        client.api.search_host_plugin.return_value = {"result": False, "message": "err", "code": 1}
        logger = MagicMock()
        res = get_host_id_by_inner_ip("t", "u", logger, 0, 1, ["1.1.1.1"])
        self.assertEqual(res, {})
        logger.error.assert_called()

    @patch("pipeline_plugins.components.collections.sites.open.nodeman.base.get_client_by_username")
    def test_get_host_id_by_inner_ipv6(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client

        # Empty list
        self.assertEqual(get_host_id_by_inner_ipv6("t", "u", None, 0, 1, []), {})

        # Success
        client.api.search_host_plugin.return_value = {
            "result": True,
            "data": {"list": [{"inner_ipv6": "::1", "bk_host_id": 100}]},
        }
        res = get_host_id_by_inner_ipv6("t", "u", None, 0, 1, ["::1"])
        self.assertEqual(res, {"::1": 100})

    @patch("pipeline_plugins.components.collections.sites.open.nodeman.base.get_client_by_username")
    def test_get_nodeman_public_key(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client
        logger = MagicMock()

        # Fail
        client.api.fetch_public_keys.return_value = {"result": False, "message": "err", "code": 1}
        res = get_nodeman_public_key("t", "u", logger)
        self.assertEqual(res, (False, None))

        # Empty data
        client.api.fetch_public_keys.return_value = {"result": True, "data": []}
        res = get_nodeman_public_key("t", "u", logger)
        self.assertEqual(res, (False, None))

        # Success
        client.api.fetch_public_keys.return_value = {
            "result": True,
            "data": [{"name": "DEFAULT", "content": "key", "cipher_type": "RSA"}],
        }
        res = get_nodeman_public_key("t", "u", logger)
        self.assertTrue(res[0])
        self.assertEqual(res[1]["content"], "key")


class ConcreteNodeManNewBaseService(NodeManNewBaseService):
    def execute(self, data, parent_data):
        pass


class NodeManBaseServiceTestCase(TestCase):
    def setUp(self):
        self.service = ConcreteNodeManNewBaseService()
        self.service.logger = MagicMock()

    def test_get_ip_list(self):
        settings.ENABLE_IPV6 = False
        res = self.service.get_ip_list("1.1.1.1")
        self.assertEqual(res, ["1.1.1.1"])

        settings.ENABLE_IPV6 = True
        res = self.service.get_ip_list("1.1.1.1")
        self.assertEqual(res, ["1.1.1.1"])  # extract_ip_from_ip_str returns tuple of lists

    @patch("pipeline_plugins.components.collections.sites.open.nodeman.base.get_host_id_by_inner_ip")
    @patch("pipeline_plugins.components.collections.sites.open.nodeman.base.get_host_id_by_inner_ipv6")
    def test_get_host_id_list(self, mock_ipv6, mock_ip):
        mock_ip.return_value = {"1.1.1.1": 100}
        mock_ipv6.return_value = {"::1": 101}

        settings.ENABLE_IPV6 = True
        res = self.service.get_host_id_list("t", "ip", "u", 0, 1)
        self.assertTrue(100 in res)
        self.assertTrue(101 in res)

        settings.ENABLE_IPV6 = False
        res = self.service.get_host_id_list("t", "ip", "u", 0, 1)
        self.assertEqual(res, [100])

    @patch("pipeline_plugins.components.collections.sites.open.nodeman.base.get_nodeman_public_key")
    @patch("pipeline_plugins.components.collections.sites.open.nodeman.base.get_asymmetric_cipher")
    def test_parse2nodeman_ciphertext(self, mock_cipher, mock_get_key):
        data = MagicMock()
        mock_get_key.return_value = (False, None)
        with self.assertRaises(ValueError):
            self.service.parse2nodeman_ciphertext("t", data, "u", "p")
        data.set_outputs.assert_called()

        mock_get_key.return_value = (True, {"cipher_type": "RSA", "content": "k"})
        mock_cipher.return_value.encrypt.return_value = "encrypted"
        res = self.service.parse2nodeman_ciphertext("t", data, "u", "p")
        self.assertEqual(res, "encrypted")

    @patch("pipeline_plugins.components.collections.sites.open.nodeman.base.get_client_by_username")
    def test_schedule(self, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client
        data = MagicMock()
        parent_data = MagicMock()

        # No job id
        data.get_one_of_outputs.return_value = None
        self.assertTrue(self.service.schedule(data, parent_data))

        # Success
        data.get_one_of_outputs.return_value = 100
        client.api.job_details.return_value = {
            "result": True,
            "data": {"status": "SUCCESS", "statistics": {"success_count": 1, "failed_count": 0}, "list": []},
        }
        self.assertTrue(self.service.schedule(data, parent_data))

        # Failed with logs
        client.api.job_details.return_value = {
            "result": True,
            "data": {
                "status": "FAILED",
                "statistics": {"success_count": 0, "failed_count": 1},
                "list": [{"inner_ip": "1.1.1.1", "instance_id": 1, "status": "FAILED"}],
            },
        }
        client.api.get_job_log.return_value = {"result": True, "data": [{"status": "FAILED", "step": "s", "log": "l"}]}
        self.assertFalse(self.service.schedule(data, parent_data))
        data.set_outputs.assert_any_call("ex_data", ANY)

    @patch("pipeline_plugins.components.collections.sites.open.nodeman.base.get_client_by_username")
    @patch("pipeline_plugins.components.collections.sites.open.nodeman.base.get_nodeman_job_url")
    def test_execute_operate(self, mock_get_url, mock_get_client):
        client = MagicMock()
        mock_get_client.return_value = client
        data = MagicMock()
        data.inputs.nodeman_plugin_operate = {
            "nodeman_op_type": "MAIN_INSTALL_PLUGIN",
            "nodeman_plugin": "plugin",
            "install_config": ["keep_config"],
        }
        mock_get_url.return_value = "url"

        # Success
        client.api.operate_plugin.return_value = {"result": True, "data": {"plugin": 123}}

        self.service.execute_operate("t", data, [1], "user", 1)
        self.assertEqual(data.outputs.job_url, ["url"])

        # Fail
        client.api.operate_plugin.return_value = {"result": False, "message": "err", "code": 1}
        self.assertFalse(self.service.execute_operate("t", data, [1], "user", 1))

    def test_formats(self):
        self.assertTrue(len(self.service.outputs_format()) > 0)
        s = ConcreteNodeManNewBaseService()
        self.assertTrue(len(s.inputs_format()) > 0)
