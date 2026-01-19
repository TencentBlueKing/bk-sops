import mock
from django.test import TestCase

from pipeline_plugins.variables.collections.sites.open import ip_filter_base


class IpFilterBaseSupplementTestCase(TestCase):
    def setUp(self):
        self.tenant_id = "tenant"
        self.ip_str = "1.1.1.1"
        self.data = {"executor": "user", "project_id": 1}
        self.project = mock.MagicMock()
        self.project.bk_biz_id = 1
        self.project.from_cmdb = True

    @mock.patch("pipeline_plugins.variables.collections.sites.open.ip_filter_base.Project")
    def test_GseAgentStatusIpV6Filter(self, MockProject):
        MockProject.objects.get.return_value = self.project
        filter_obj = ip_filter_base.GseAgentStatusIpV6Filter(self.tenant_id, self.ip_str, self.data)

        # Case 1: cc_get_host_by_innerip_with_ipv6 fail
        with mock.patch(
            "pipeline_plugins.variables.collections.sites.open.ip_filter_base.cc_get_host_by_innerip_with_ipv6"
        ) as mock_get_host:
            mock_get_host.return_value = {"result": False, "message": "err"}
            with self.assertRaisesRegex(ip_filter_base.ApiRequestError, "err"):
                filter_obj.get_match_ip()

            # Case 2: get_gse_agent_status_ipv6 exception
            mock_get_host.return_value = {
                "result": True,
                "data": [
                    {"bk_host_innerip": "1.1.1.1", "bk_cloud_id": 0, "bk_agent_id": "aid", "bk_host_innerip_v6": "::1"}
                ],
            }
            with mock.patch(
                "pipeline_plugins.variables.collections.sites.open.ip_filter_base.get_gse_agent_status_ipv6",
                side_effect=Exception("err"),
            ):
                with self.assertRaisesRegex(ip_filter_base.ApiRequestError, "err"):
                    filter_obj.get_match_ip()

            # Case 3: No agent_id and no ipv4
            mock_get_host.return_value = {
                "result": True,
                "data": [{"bk_host_innerip": "", "bk_cloud_id": 0, "bk_agent_id": "", "bk_host_innerip_v6": "::1"}],
            }
            with mock.patch(
                "pipeline_plugins.variables.collections.sites.open.ip_filter_base.get_gse_agent_status_ipv6",
                return_value={},
            ):
                # Should not raise, just continue/append to offline
                filter_obj.get_match_ip()

    @mock.patch("pipeline_plugins.variables.collections.sites.open.ip_filter_base.Project")
    def test_GseAgentStatusIpFilter_v1(self, MockProject):
        MockProject.objects.get.return_value = self.project
        data = self.data.copy()
        data["gse_agent_status"] = ip_filter_base.GseAgentStatus.ONlINE.value
        filter_obj = ip_filter_base.GseAgentStatusIpFilter(self.tenant_id, [{"ip": "1.1.1.1", "bk_cloud_id": 0}], data)

        with mock.patch("pipeline_plugins.variables.collections.sites.open.ip_filter_base.get_client_by_username") as _:
            with mock.patch(
                "pipeline_plugins.variables.collections.sites.open.ip_filter_base.batch_execute_func"
            ) as mock_batch:
                mock_batch.return_value = [{"result": {"result": False, "message": "err"}}]

                # Directly patch the attribute on the settings object in the module
                with mock.patch(
                    "pipeline_plugins.variables.collections.sites.open.ip_filter_base.settings.ENABLE_GSE_V2", False
                ):
                    with self.assertRaises(ip_filter_base.ApiRequestError):
                        filter_obj.get_match_ip()
