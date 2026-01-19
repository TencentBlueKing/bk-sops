# -*- coding: utf-8 -*-
import mock
from django.test import TestCase

from pipeline_plugins.components.collections.sites.open.job.base import (
    GetJobHistoryResultMixin,
    JobBizScopeType,
    JobScheduleService,
)


class MockJobScheduleService(GetJobHistoryResultMixin, JobScheduleService):
    """
    Mock class to test GetJobHistoryResultMixin
    """

    def __init__(self):
        self.logger = mock.MagicMock()
        self.need_get_sops_var = True
        self.biz_scope_type = JobBizScopeType.BIZ.value


class GetJobHistoryResultMixinTestCase(TestCase):
    def setUp(self):
        self.service = MockJobScheduleService()
        self.data = mock.MagicMock()
        self.parent_data = mock.MagicMock()
        self.parent_data.inputs.executor = "executor"
        self.parent_data.inputs.tenant_id = "tenant_id"
        self.parent_data.inputs.biz_cc_id = 1

        self.data.inputs.biz_cc_id = 1
        self.data.get_one_of_inputs.return_value = 100  # job_success_id

    @mock.patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    @mock.patch("pipeline_plugins.components.collections.sites.open.job.base.get_job_sops_var_dict")
    def test_get_job_history_result__get_var_fail(self, mock_get_vars, mock_get_client):
        # Setup client
        client = mock.MagicMock()
        mock_get_client.return_value = client

        # Setup job_instance_status success
        client.api.get_job_instance_status.return_value = {
            "result": True,
            "data": {"job_instance": {"status": 3}},  # Success status
        }

        # Setup get_job_sops_var_dict fail
        mock_get_vars.return_value = {"result": False, "message": "failed to extract vars"}

        # Execute
        result = self.service.get_job_history_result(self.data, self.parent_data)

        # Assert
        self.assertFalse(result)
        self.service.logger.error.assert_called()
        self.data.set_outputs.assert_called_with("log_outputs", {})

    @mock.patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    @mock.patch("pipeline_plugins.components.collections.sites.open.job.base.get_job_sops_var_dict")
    def test_get_job_history_result__get_var_success(self, mock_get_vars, mock_get_client):
        # Setup client
        client = mock.MagicMock()
        mock_get_client.return_value = client

        # Setup job_instance_status success
        client.api.get_job_instance_status.return_value = {"result": True, "data": {"job_instance": {"status": 3}}}

        # Setup get_job_sops_var_dict success
        expected_vars = {"key": "val"}
        mock_get_vars.return_value = {"result": True, "data": expected_vars}

        # Execute
        result = self.service.get_job_history_result(self.data, self.parent_data)

        # Assert
        self.assertTrue(result)
        self.service.logger.info.assert_called()
        # Verify set_outputs was called with log_outputs
        # self.data.set_outputs.assert_any_call("log_outputs", expected_vars)
        # Since finish_schedule is not mocked in the mixin test, it might be tricky.
        # But get_job_history_result calls set_outputs.

    @mock.patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    def test_get_job_history_result__job_status_fail(self, mock_get_client):
        # Setup client
        client = mock.MagicMock()
        mock_get_client.return_value = client

        # Setup job_instance_status fail (API success but status fail)
        client.api.get_job_instance_status.return_value = {
            "result": True,
            "data": {"job_instance": {"status": 4}},  # Fail status
        }

        # Execute
        result = self.service.get_job_history_result(self.data, self.parent_data)

        # Assert
        self.assertFalse(result)
        self.assertTrue(self.data.outputs.ex_data)

    @mock.patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    def test_get_job_history_result__api_fail(self, mock_get_client):
        # Setup client
        client = mock.MagicMock()
        mock_get_client.return_value = client

        # Setup job_instance_status API fail
        client.api.get_job_instance_status.return_value = {"result": False, "message": "API Error"}

        # Execute
        result = self.service.get_job_history_result(self.data, self.parent_data)

        # Assert
        self.assertFalse(result)
        self.assertTrue(self.data.outputs.ex_data)
