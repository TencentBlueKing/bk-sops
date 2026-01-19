# -*- coding: utf-8 -*-
"""
完整覆盖测试，针对utils.py中未覆盖的代码分支
"""

from django.test import TestCase
from mock import MagicMock, patch

from pipeline_plugins.cmdb_ip_picker.utils import (
    format_agent_data,
    get_bk_cloud_id_for_host,
    get_cmdb_topo_tree,
    get_gse_agent_status_ipv6,
    get_ip_picker_result,
)


class GetIpPickerResultTestCase(TestCase):
    """测试 get_ip_picker_result 函数"""

    @patch("pipeline_plugins.cmdb_ip_picker.utils.IPPickerHandler")
    def test_get_ip_picker_result_with_handler_error(self, mock_handler_class):
        """测试IPPickerHandler初始化错误的情况"""
        mock_handler = MagicMock()
        mock_handler.error = {"result": False, "message": "初始化错误"}
        mock_handler_class.return_value = mock_handler

        kwargs = {"selectors": ["ip"], "filters": [], "excludes": [], "ip": []}
        result = get_ip_picker_result(tenant_id="system", username="test_user", bk_biz_id=2, kwargs=kwargs)

        self.assertFalse(result["result"])
        self.assertEqual(result["message"], "初始化错误")

    @patch("pipeline_plugins.cmdb_ip_picker.utils.IPPickerDataGenerator")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.IPPickerHandler")
    def test_get_ip_picker_result_with_manual_input_success(self, mock_handler_class, mock_generator_class):
        """测试手动输入模式成功的情况"""
        # Mock handler
        mock_handler = MagicMock()
        mock_handler.error = None
        mock_handler.biz_topo_tree = {"bk_inst_id": 2}
        mock_handler.dispatch.return_value = {
            "result": True,
            "data": [{"bk_host_id": 1, "bk_host_innerip": "10.0.0.1"}],
        }
        mock_handler_class.return_value = mock_handler

        # Mock generator
        mock_generator = MagicMock()
        mock_generator.generate.return_value = {"result": True, "data": [{"bk_host_id": 1}]}
        mock_generator_class.return_value = mock_generator

        kwargs = {
            "selectors": ["manual"],
            "manual_input": {"value": "10.0.0.1", "type": "ip"},
            "filters": [],
            "excludes": [],
        }
        result = get_ip_picker_result(tenant_id="system", username="test_user", bk_biz_id=2, kwargs=kwargs)

        self.assertTrue(result["result"])
        mock_generator.generate.assert_called_once()
        mock_handler.dispatch.assert_called_once()

    @patch("pipeline_plugins.cmdb_ip_picker.utils.IPPickerDataGenerator")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.IPPickerHandler")
    def test_get_ip_picker_result_with_manual_input_generate_failed(self, mock_handler_class, mock_generator_class):
        """测试手动输入模式生成数据失败的情况"""
        # Mock handler
        mock_handler = MagicMock()
        mock_handler.error = None
        mock_handler.biz_topo_tree = {"bk_inst_id": 2}
        mock_handler_class.return_value = mock_handler

        # Mock generator返回失败
        mock_generator = MagicMock()
        mock_generator.generate.return_value = {"result": False, "message": "生成数据失败"}
        mock_generator_class.return_value = mock_generator

        kwargs = {
            "selectors": ["manual"],
            "manual_input": {"value": "invalid_ip", "type": "ip"},
            "filters": [],
            "excludes": [],
        }
        result = get_ip_picker_result(tenant_id="system", username="test_user", bk_biz_id=2, kwargs=kwargs)

        self.assertFalse(result["result"])
        self.assertEqual(result["message"], "生成数据失败")


class GetCmdbTopoTreeTestCase(TestCase):
    """测试 get_cmdb_topo_tree 函数"""

    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_client_by_username")
    def test_get_cmdb_topo_tree_search_topo_failed(self, mock_get_client):
        """测试search_biz_inst_topo调用失败的情况"""
        mock_client = MagicMock()
        mock_client.api.search_biz_inst_topo.return_value = {"result": False, "message": "查询拓扑树失败"}
        mock_get_client.return_value = mock_client

        result = get_cmdb_topo_tree("system", "test_user", 2)

        self.assertFalse(result["result"])
        self.assertIn("message", result)

    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_client_by_username")
    def test_get_cmdb_topo_tree_get_internal_module_failed(self, mock_get_client):
        """测试get_biz_internal_module调用失败的情况"""
        mock_client = MagicMock()
        mock_client.api.search_biz_inst_topo.return_value = {"result": True, "data": [{"bk_inst_id": 2}]}
        mock_client.api.get_biz_internal_module.return_value = {"result": False, "message": "查询内部模块失败"}
        mock_get_client.return_value = mock_client

        with patch("pipeline_plugins.cmdb_ip_picker.utils.EnvironmentVariables") as mock_env:
            mock_env.objects.get_var.return_value = 0
            result = get_cmdb_topo_tree("system", "test_user", 2)

        self.assertFalse(result["result"])
        self.assertIn("message", result)


class GetGseAgentStatusIpv6TestCase(TestCase):
    """测试 get_gse_agent_status_ipv6 函数"""

    def test_get_gse_agent_status_ipv6_empty_list(self):
        """测试空的agent_id列表"""
        result = get_gse_agent_status_ipv6([], "system")
        self.assertEqual(result, {})

    @patch("pipeline_plugins.cmdb_ip_picker.utils.requests")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.settings")
    def test_get_gse_agent_status_ipv6_success(self, mock_settings, mock_requests):
        """测试成功获取agent状态"""
        mock_settings.BK_API_URL_TMPL = "http://api/{api_name}"
        mock_settings.RUN_MODE = "PRODUCT"
        mock_settings.APP_CODE = "test_app"
        mock_settings.SECRET_KEY = "test_secret"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "data": [
                {"bk_agent_id": "agent1", "status_code": 2},  # 运行中
                {"bk_agent_id": "agent2", "status_code": -1},  # 未知
                {"bk_agent_id": "agent3", "status_code": 0},  # 初始安装
            ],
        }
        mock_requests.post.return_value = mock_response

        result = get_gse_agent_status_ipv6(["agent1", "agent2", "agent3"], "system")

        self.assertEqual(result["agent1"], 1)  # 2 -> 1
        self.assertEqual(result["agent2"], -1)  # -1 -> -1
        self.assertEqual(result["agent3"], 0)  # 0 -> 0

    @patch("pipeline_plugins.cmdb_ip_picker.utils.requests")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.settings")
    def test_get_gse_agent_status_ipv6_http_error(self, mock_settings, mock_requests):
        """测试HTTP状态码错误"""
        mock_settings.BK_API_URL_TMPL = "http://api/{api_name}"
        mock_settings.RUN_MODE = "STAGING"
        mock_settings.APP_CODE = "test_app"
        mock_settings.SECRET_KEY = "test_secret"

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.content = "Internal Server Error"
        mock_requests.post.return_value = mock_response

        with self.assertRaises(Exception) as context:
            get_gse_agent_status_ipv6(["agent1"], "system")

        self.assertIn("返回值非200", str(context.exception))

    @patch("pipeline_plugins.cmdb_ip_picker.utils.requests")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.settings")
    def test_get_gse_agent_status_ipv6_json_error(self, mock_settings, mock_requests):
        """测试响应不是JSON格式"""
        mock_settings.BK_API_URL_TMPL = "http://api/{api_name}"
        mock_settings.RUN_MODE = "PRODUCT"
        mock_settings.APP_CODE = "test_app"
        mock_settings.SECRET_KEY = "test_secret"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = Exception("Invalid JSON")
        mock_requests.post.return_value = mock_response

        with self.assertRaises(Exception) as context:
            get_gse_agent_status_ipv6(["agent1"], "system")

        self.assertIn("返回值非Json", str(context.exception))

    @patch("pipeline_plugins.cmdb_ip_picker.utils.requests")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.settings")
    def test_get_gse_agent_status_ipv6_code_error(self, mock_settings, mock_requests):
        """测试返回code非0"""
        mock_settings.BK_API_URL_TMPL = "http://api/{api_name}"
        mock_settings.RUN_MODE = "PRODUCT"
        mock_settings.APP_CODE = "test_app"
        mock_settings.SECRET_KEY = "test_secret"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": 1, "message": "查询失败"}
        mock_requests.post.return_value = mock_response

        with self.assertRaises(Exception) as context:
            get_gse_agent_status_ipv6(["agent1"], "system")

        self.assertIn("code非0", str(context.exception))

    @patch("pipeline_plugins.cmdb_ip_picker.utils.requests")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.settings")
    def test_get_gse_agent_status_ipv6_large_list(self, mock_settings, mock_requests):
        """测试大量agent_id（超过1000个）的分批处理"""
        mock_settings.BK_API_URL_TMPL = "http://api/{api_name}"
        mock_settings.RUN_MODE = "PRODUCT"
        mock_settings.APP_CODE = "test_app"
        mock_settings.SECRET_KEY = "test_secret"

        # 创建1500个agent_id
        agent_ids = [f"agent{i}" for i in range(1500)]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "data": [{"bk_agent_id": f"agent{i}", "status_code": 2} for i in range(1500)],
        }
        mock_requests.post.return_value = mock_response

        result = get_gse_agent_status_ipv6(agent_ids, "system")

        # 应该分成两批请求（1000 + 500）
        self.assertEqual(mock_requests.post.call_count, 2)
        self.assertEqual(len(result), 1500)


class FormatAgentDataTestCase(TestCase):
    """测试 format_agent_data 函数"""

    def test_format_agent_data_success(self):
        """测试格式化agent数据"""
        agents = [
            {"ip": "10.0.0.1", "cloud_area": {"id": 0}, "alive": 1},
            {"ip": "10.0.0.2", "cloud_area": {"id": 1}, "alive": 0},
        ]

        result = format_agent_data(agents)

        self.assertIn("0:10.0.0.1", result)
        self.assertIn("1:10.0.0.2", result)
        self.assertEqual(result["0:10.0.0.1"]["bk_cloud_id"], 0)
        self.assertEqual(result["0:10.0.0.1"]["bk_agent_alive"], 1)
        self.assertEqual(result["1:10.0.0.2"]["bk_cloud_id"], 1)
        self.assertEqual(result["1:10.0.0.2"]["bk_agent_alive"], 0)


class GetBkCloudIdForHostTestCase(TestCase):
    """测试 get_bk_cloud_id_for_host 函数"""

    def test_get_bk_cloud_id_with_empty_cloud_info(self):
        """测试主机没有云区域信息的情况"""
        host_info = {"cloud": []}
        result = get_bk_cloud_id_for_host(host_info)
        self.assertEqual(result, "-1")  # DEFAULT_BK_CLOUD_ID

    def test_get_bk_cloud_id_with_cloud_info(self):
        """测试主机有云区域信息的情况"""
        host_info = {"cloud": [{"id": 5}]}
        result = get_bk_cloud_id_for_host(host_info)
        self.assertEqual(result, 5)  # 返回云区域ID

    def test_get_bk_cloud_id_with_bk_cloud_id_key(self):
        """测试使用bk_cloud_id作为key的情况"""
        host_info = {"bk_cloud_id": [{"id": 3}]}
        result = get_bk_cloud_id_for_host(host_info, cloud_key="bk_cloud_id")
        self.assertEqual(result, 3)

    def test_get_bk_cloud_id_with_cloud_key(self):
        """测试使用cloud作为key的情况"""
        host_info = {"cloud": [{"id": 3}]}
        result = get_bk_cloud_id_for_host(host_info, cloud_key="cloud")
        self.assertEqual(result, 3)

    def test_get_bk_cloud_id_with_empty_cloud_key(self):
        """测试使用cloud作为key但为空的情况"""
        host_info = {"cloud": []}
        result = get_bk_cloud_id_for_host(host_info, cloud_key="cloud")
        self.assertEqual(result, "-1")
