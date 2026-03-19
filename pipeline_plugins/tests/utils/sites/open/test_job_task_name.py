# -*- coding: utf-8 -*-
"""get_job_task_name 单元测试"""
from unittest.mock import MagicMock, patch

from pipeline_plugins.components.utils.sites.open.utils import get_job_task_name


class TestGetJobTaskName:
    """测试 get_job_task_name"""

    def test_returns_task_name_when_node_exists(self):
        """节点存在且有名时返回 节点名_时间戳"""
        mock_pipeline = MagicMock()
        mock_pipeline.execution_data = {
            "activities": {
                "node_1": {"name": "执行脚本", "type": "ServiceActivity"},
            }
        }
        with patch("pipeline_plugins.components.utils.sites.open.utils.PipelineInstance") as MockPI:
            MockPI.objects.filter.return_value.first.return_value = mock_pipeline
            with patch("time.time", return_value=1521100521.303):
                result = get_job_task_name("test_root_123", "node_1")
        assert result == "执行脚本_1521100521303"

    def test_returns_none_when_pipeline_not_found(self):
        """PipelineInstance 不存在时返回 None"""
        with patch("pipeline_plugins.components.utils.sites.open.utils.PipelineInstance") as MockPI:
            MockPI.objects.filter.return_value.first.return_value = None
            result = get_job_task_name("nonexistent_pipeline", "node_1")
        assert result is None

    def test_returns_none_when_node_name_empty(self):
        """节点名为空时返回 None"""
        mock_pipeline = MagicMock()
        mock_pipeline.execution_data = {
            "activities": {
                "node_2": {"name": "", "type": "ServiceActivity"},
            }
        }
        with patch("pipeline_plugins.components.utils.sites.open.utils.PipelineInstance") as MockPI:
            MockPI.objects.filter.return_value.first.return_value = mock_pipeline
            result = get_job_task_name("test_root_456", "node_2")
        assert result is None

    def test_sanitizes_special_chars(self):
        """节点名包含非法字符时被去除"""
        mock_pipeline = MagicMock()
        mock_pipeline.execution_data = {
            "activities": {
                "node_3": {"name": "脚本<>$&'\"", "type": "ServiceActivity"},
            }
        }
        with patch("pipeline_plugins.components.utils.sites.open.utils.PipelineInstance") as MockPI:
            MockPI.objects.filter.return_value.first.return_value = mock_pipeline
            with patch("time.time", return_value=1521100521.303):
                result = get_job_task_name("test_root_789", "node_3")
        assert "<" not in result and ">" not in result
        assert result.endswith("_1521100521303")  # int(1521100521.303 * 1000)
