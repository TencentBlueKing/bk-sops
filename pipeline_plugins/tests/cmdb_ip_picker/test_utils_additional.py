# -*- coding: utf-8 -*-
"""
补充测试，用于提高coverage
"""

from django.test import TestCase
from mock import patch

from pipeline_plugins.cmdb_ip_picker.utils import IPPickerHandler


class AdditionalIPPickerHandlerTestCase(TestCase):
    """补充测试用例"""

    def setUp(self):
        self.tenant_id = "system"
        self.username = "test_user"
        self.bk_biz_id = 2

    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_cmdb_topo_tree")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_dynamic_group_list")
    def test_group_picker_handler_with_filters(self, mock_get_group_list, mock_cmdb, mock_get_topo):
        """测试动态分组选择器带过滤条件"""
        # Mock 拓扑树
        mock_get_topo.return_value = {
            "result": True,
            "data": [{"bk_inst_id": 2, "bk_inst_name": "业务1", "bk_obj_id": "biz", "child": []}],
        }

        mock_get_group_list.return_value = [{"id": "group1", "name": "分组1"}]

        # get_dynamic_group_host_list 返回3个主机
        mock_cmdb.get_dynamic_group_host_list.return_value = (
            True,
            {
                "data": [
                    {"bk_host_id": 1, "bk_host_innerip": "10.0.0.1", "bk_cloud_id": 0},
                    {"bk_host_id": 2, "bk_host_innerip": "10.0.0.2", "bk_cloud_id": 0},
                    {"bk_host_id": 3, "bk_host_innerip": "10.0.0.3", "bk_cloud_id": 0},
                ]
            },
        )

        # get_business_host_topo 只返回2个主机（过滤后）
        mock_cmdb.get_business_host_topo.return_value = [
            {"host": {"bk_host_id": 1, "bk_host_innerip": "10.0.0.1", "bk_cloud_id": 0}},
            {"host": {"bk_host_id": 2, "bk_host_innerip": "10.0.0.2", "bk_cloud_id": 0}},
        ]

        filters = [{"field": "host", "value": ["10.0.0.1", "10.0.0.2"]}]

        with patch("pipeline_plugins.cmdb_ip_picker.utils.settings") as mock_settings:
            mock_settings.ENABLE_IPV6 = False

            handler = IPPickerHandler(self.tenant_id, "group", self.username, self.bk_biz_id, filters=filters)

            inputted_group = [{"id": "group1", "name": "分组1"}]
            result = handler.group_picker_handler(inputted_group)

            self.assertTrue(result["result"])
            # 应该只返回过滤后的2个主机
            self.assertEqual(len(result["data"]), 2)

    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_cmdb_topo_tree")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.cmdb")
    @patch("pipeline_plugins.cmdb_ip_picker.utils.get_dynamic_group_list")
    def test_group_picker_handler_fetch_host_failed(self, mock_get_group_list, mock_cmdb, mock_get_topo):
        """测试动态分组获取主机后过滤失败"""
        # Mock 拓扑树
        mock_get_topo.return_value = {
            "result": True,
            "data": [{"bk_inst_id": 2, "bk_inst_name": "业务1", "bk_obj_id": "biz", "child": []}],
        }

        mock_get_group_list.return_value = [{"id": "group1", "name": "分组1"}]

        mock_cmdb.get_dynamic_group_host_list.return_value = (
            True,
            {"data": [{"bk_host_id": 1, "bk_host_innerip": "10.0.0.1", "bk_cloud_id": 0}]},
        )

        # 模拟get_business_host_topo抛出异常
        def side_effect_func(*args, **kwargs):
            raise Exception("获取主机失败")

        mock_cmdb.get_business_host_topo = side_effect_func

        filters = [{"field": "host", "value": ["10.0.0.1"]}]

        with patch("pipeline_plugins.cmdb_ip_picker.utils.settings") as mock_settings:
            mock_settings.ENABLE_IPV6 = False

            handler = IPPickerHandler(self.tenant_id, "group", self.username, self.bk_biz_id, filters=filters)

            inputted_group = [{"id": "group1", "name": "分组1"}]

            with self.assertRaises(Exception):
                handler.group_picker_handler(inputted_group)
