# -*- coding: utf-8 -*-
import mock
from django.test import TestCase

from pipeline_plugins.components.collections.sites.open.job.fast_execute_script import v1_2


class JobFastExecuteScriptServiceSupplementTestCase(TestCase):
    def setUp(self):
        self.service = v1_2.JobFastExecuteScriptService()
        self.service.logger = mock.MagicMock()
        self.service.root_pipeline_id = "root_id"
        self.service.id = "node_id"
        self.data = mock.MagicMock()
        self.parent_data = mock.MagicMock()

        self.data.get_one_of_inputs.return_value = "val"
        self.parent_data.get_one_of_inputs.return_value = "val"
        self.parent_data.inputs.biz_cc_id = 1
        self.parent_data.inputs.tenant_id = "tenant"

    def test_execute__job_success_id(self):
        self.data.get_one_of_inputs = mock.MagicMock(
            side_effect=lambda key, *args: "success_id" if key == "job_success_id" else None
        )
        with mock.patch.object(self.service, "get_job_history_result", return_value=True):
            res = self.service.execute(self.data, self.parent_data)
            self.assertTrue(res)

    @mock.patch(
        "pipeline_plugins.components.collections.sites.open.job.fast_execute_script.v1_2.get_client_by_username"
    )
    def test_execute__get_target_server_fail(self, mock_client):
        # Handle job_rolling_config get None issue
        def input_side_effect(key, *args):
            if key == "job_rolling_config":
                return {}
            if key == "job_success_id":
                return None
            return "val"

        self.data.get_one_of_inputs.side_effect = input_side_effect

        with mock.patch.object(self.service, "get_target_server_hybrid", return_value=(False, None)):
            res = self.service.execute(self.data, self.parent_data)
            self.assertFalse(res)

    @mock.patch(
        "pipeline_plugins.components.collections.sites.open.job.fast_execute_script.v1_2.get_client_by_username"
    )
    def test_execute__script_source_general_fail(self, mock_client):
        def input_side_effect(key, *args):
            if key == "job_script_source":
                return "general"
            if key == "job_success_id":
                return None
            if key == "job_rolling_config":
                return {}
            return "val"

        self.data.get_one_of_inputs.side_effect = input_side_effect

        with mock.patch.object(self.service, "get_target_server_hybrid", return_value=(True, {})):
            with mock.patch(
                "pipeline_plugins.components.collections.sites.open.job.fast_execute_script.v1_2.batch_request",
                side_effect=v1_2.ApiRequestError("err"),
            ):
                res = self.service.execute(self.data, self.parent_data)
                self.assertFalse(res)
                self.service.logger.error.assert_called()

    # Patch base.py's get_client_by_username for get_job_history_result (mixin)
    @mock.patch("pipeline_plugins.components.collections.sites.open.job.base.get_client_by_username")
    @mock.patch(
        "pipeline_plugins.components.collections.sites.open.job.fast_execute_script.v1_2.get_client_by_username"
    )
    def test_execute__script_not_found(self, mock_client, mock_base_client):
        # If job_success_id is returned, it calls get_job_history_result.
        # Ensure job_success_id is None to reach script logic.
        def input_side_effect(key, *args):
            if key == "job_success_id":
                return None
            if key == "job_script_source":
                return "general"
            if key == "job_rolling_config":
                return {}
            return "val"

        self.data.get_one_of_inputs.side_effect = input_side_effect

        with mock.patch.object(self.service, "get_target_server_hybrid", return_value=(True, {})):
            with mock.patch(
                "pipeline_plugins.components.collections.sites.open.job.fast_execute_script.v1_2.batch_request",
                return_value=[],
            ):
                res = self.service.execute(self.data, self.parent_data)
                self.assertFalse(res)
                self.assertTrue(self.data.outputs.ex_data)

    @mock.patch(
        "pipeline_plugins.components.collections.sites.open.job.fast_execute_script.v1_2.get_client_by_username"
    )
    def test_execute__rolling_execute(self, mock_client):
        def input_side_effect(key, *args):
            if key == "job_rolling_config":
                return {"job_rolling_execute": True}
            if key == "job_script_source":
                return "manual"
            if key == "job_success_id":
                return None
            return "val"

        self.data.get_one_of_inputs = mock.MagicMock(side_effect=input_side_effect)
        mock_client.return_value.api.fast_execute_script.return_value = {
            "result": True,
            "data": {"job_instance_id": 1, "job_instance_name": "name"},
        }

        with mock.patch.object(self.service, "get_target_server_hybrid", return_value=(True, {})):
            res = self.service.execute(self.data, self.parent_data)
            self.assertTrue(res)
            # Verify kwargs has rolling config
            args, kwargs = mock_client.return_value.api.fast_execute_script.call_args
            self.assertIn("rolling_config", args[0])

    @mock.patch(
        "pipeline_plugins.components.collections.sites.open.job.fast_execute_script.v1_2.get_client_by_username"
    )
    def test_execute__api_fail(self, mock_client):
        def input_side_effect(key, *args):
            if key == "job_script_source":
                return "manual"
            if key == "job_success_id":
                return None
            if key == "job_rolling_config":
                return {}
            return "val"

        self.data.get_one_of_inputs = mock.MagicMock(side_effect=input_side_effect)

        mock_client.return_value.api.fast_execute_script.return_value = {"result": False, "message": "err"}

        with mock.patch.object(self.service, "get_target_server_hybrid", return_value=(True, {})):
            res = self.service.execute(self.data, self.parent_data)
            self.assertFalse(res)
            self.assertTrue(self.data.outputs.ex_data)
