# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock, patch

from gcloud.constants import GseAgentStatus
from pipeline_plugins.variables.collections.sites.open.ip_filter_base import (
    GseAgentStatusIpFilter,
    GseAgentStatusIpV6Filter,
)


class GseAgentStatusIpFilterTest(TestCase):
    def setUp(self):
        self.tenant_id = "tenant"
        self.origin_ip_list = [{"bk_cloud_id": 0, "ip": "1.1.1.1"}]
        self.data = {"gse_agent_status": GseAgentStatus.ONlINE.value, "executor": "admin", "project_id": 1}

    @patch("pipeline_plugins.variables.collections.sites.open.ip_filter_base.Project.objects.get")
    @patch("pipeline_plugins.variables.collections.sites.open.ip_filter_base.settings")
    @patch("pipeline_plugins.variables.collections.sites.open.ip_filter_base.cmdb.get_business_host")
    @patch("pipeline_plugins.variables.collections.sites.open.ip_filter_base.get_gse_agent_status_ipv6")
    def test_get_match_ip_v2_online(self, mock_get_status, mock_get_hosts, mock_settings, mock_project_get):
        mock_settings.ENABLE_GSE_V2 = True
        mock_project = MagicMock()
        mock_project.bk_biz_id = 2
        mock_project.from_cmdb = True
        mock_project_get.return_value = mock_project

        mock_get_hosts.return_value = [{"bk_cloud_id": 0, "bk_host_innerip": "1.1.1.1", "bk_agent_id": "agent1"}]
        mock_get_status.return_value = {"agent1": GseAgentStatus.ONlINE.value}

        ip_filter = GseAgentStatusIpFilter(self.tenant_id, self.origin_ip_list, self.data)
        match_ip = ip_filter.get_match_ip()

        self.assertEqual(len(match_ip), 1)
        self.assertEqual(match_ip[0]["ip"], "1.1.1.1")

    @patch("pipeline_plugins.variables.collections.sites.open.ip_filter_base.Project.objects.get")
    @patch("pipeline_plugins.variables.collections.sites.open.ip_filter_base.settings")
    @patch("pipeline_plugins.variables.collections.sites.open.ip_filter_base.cmdb.get_business_host")
    @patch("pipeline_plugins.variables.collections.sites.open.ip_filter_base.get_gse_agent_status_ipv6")
    def test_get_match_ip_v2_offline(self, mock_get_status, mock_get_hosts, mock_settings, mock_project_get):
        mock_settings.ENABLE_GSE_V2 = True
        mock_project = MagicMock()
        mock_project.bk_biz_id = 2
        mock_project.from_cmdb = True
        mock_project_get.return_value = mock_project

        self.data["gse_agent_status"] = GseAgentStatus.OFFLINE.value

        mock_get_hosts.return_value = [{"bk_cloud_id": 0, "bk_host_innerip": "1.1.1.1", "bk_agent_id": "agent1"}]
        mock_get_status.return_value = {"agent1": GseAgentStatus.ONlINE.value}  # Online, but we want offline

        ip_filter = GseAgentStatusIpFilter(self.tenant_id, self.origin_ip_list, self.data)
        match_ip = ip_filter.get_match_ip()

        self.assertEqual(len(match_ip), 0)

    @patch("pipeline_plugins.variables.collections.sites.open.ip_filter_base.Project.objects.get")
    @patch("pipeline_plugins.variables.collections.sites.open.ip_filter_base.settings")
    @patch("pipeline_plugins.variables.collections.sites.open.ip_filter_base.get_client_by_username")
    @patch("pipeline_plugins.variables.collections.sites.open.ip_filter_base.batch_execute_func")
    @patch("pipeline_plugins.variables.collections.sites.open.ip_filter_base.format_agent_data")
    def test_get_match_ip_v1(self, mock_format, mock_batch, mock_get_client, mock_settings, mock_project_get):
        mock_settings.ENABLE_GSE_V2 = False
        mock_project = MagicMock()
        mock_project.bk_biz_id = 2
        mock_project.from_cmdb = True
        mock_project_get.return_value = mock_project

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_batch.return_value = [{"result": {"result": True, "data": []}}]

        mock_format.return_value = {
            "0:1.1.1.1": {"bk_cloud_id": 0, "ip": "1.1.1.1", "bk_agent_alive": GseAgentStatus.ONlINE.value}
        }

        ip_filter = GseAgentStatusIpFilter(self.tenant_id, self.origin_ip_list, self.data)
        match_ip = ip_filter.get_match_ip()

        self.assertEqual(len(match_ip), 1)
        self.assertEqual(match_ip[0]["ip"], "1.1.1.1")

    @patch("pipeline_plugins.variables.collections.sites.open.ip_filter_base.Project.objects.get")
    def test_get_match_ip_empty(self, mock_project_get):
        mock_project = MagicMock()
        mock_project.bk_biz_id = 2
        mock_project.from_cmdb = True
        mock_project_get.return_value = mock_project

        ip_filter = GseAgentStatusIpFilter(self.tenant_id, [], self.data)
        match_ip = ip_filter.get_match_ip()
        self.assertEqual(match_ip, [])


class GseAgentStatusIpV6FilterTest(TestCase):
    def setUp(self):
        self.tenant_id = "tenant"
        self.ip_str = "1.1.1.1\n0:2.2.2.2"
        self.data = {"gse_agent_status": GseAgentStatus.ONlINE.value, "executor": "admin", "project_id": 1}

    @patch("pipeline_plugins.variables.collections.sites.open.ip_filter_base.Project.objects.get")
    @patch("pipeline_plugins.variables.collections.sites.open.ip_filter_base.cc_get_host_by_innerip_with_ipv6")
    @patch("pipeline_plugins.variables.collections.sites.open.ip_filter_base.get_gse_agent_status_ipv6")
    def test_get_match_ip_mixed(self, mock_get_status, mock_cc_get_host, mock_project_get):
        mock_project = MagicMock()
        mock_project.bk_biz_id = 2
        mock_project.from_cmdb = True
        mock_project_get.return_value = mock_project

        mock_cc_get_host.return_value = {
            "result": True,
            "data": [
                {"bk_cloud_id": 0, "bk_host_innerip": "1.1.1.1", "bk_host_innerip_v6": "::1", "bk_agent_id": "agent1"},
                {"bk_cloud_id": 0, "bk_host_innerip": "2.2.2.2", "bk_host_innerip_v6": "", "bk_agent_id": "agent2"},
            ],
        }

        # agent1 online, agent2 offline
        mock_get_status.return_value = {"agent1": 1, "agent2": 0}

        ip_filter = GseAgentStatusIpV6Filter(self.tenant_id, self.ip_str, self.data)
        match_host = ip_filter.get_match_ip()

        # Expect only agent1
        self.assertEqual(len(match_host), 1)
        self.assertEqual(match_host[0]["ip"], "1.1.1.1")
