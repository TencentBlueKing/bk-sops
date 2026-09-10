from unittest import mock

from django.test import SimpleTestCase

from gcloud.apigw.management.commands import sync_saas_apigw


class SyncSaaSApiGatewayTest(SimpleTestCase):
    @mock.patch.object(sync_saas_apigw.env, "IS_PAAS_V3", True)
    @mock.patch.object(sync_saas_apigw, "call_command")
    def test_syncs_only_current_api_gateway(self, call_command):
        sync_saas_apigw.Command().handle()

        command_names = [call.args[0] for call in call_command.call_args_list]
        self.assertEqual(
            command_names,
            [
                "sync_apigw_config",
                "sync_apigw_stage",
                "sync_apigw_resources",
                "sync_resource_docs_by_archive",
                "create_version_and_release_apigw",
                "grant_apigw_permissions",
                "fetch_apigw_public_key",
            ],
        )
        self.assertNotIn("fetch_esb_public_key", command_names)

    @mock.patch.object(sync_saas_apigw.env, "IS_PAAS_V3", False)
    @mock.patch.object(sync_saas_apigw, "call_command")
    def test_non_paas_v3_does_not_sync_gateway(self, call_command):
        sync_saas_apigw.Command().handle()

        call_command.assert_not_called()
