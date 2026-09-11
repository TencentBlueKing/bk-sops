from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from gcloud.utils.webhook import get_webhook_configs


class GetWebhookConfigsTestCase(SimpleTestCase):
    @patch("gcloud.utils.webhook.WebhookModel.objects.filter")
    def test_no_config_means_disabled(self, webhook_filter):
        webhook_filter.return_value.first.return_value = None

        self.assertEqual(get_webhook_configs("1"), {})

    @patch("gcloud.utils.webhook.process_sensitive_info", return_value={"token": "decrypted"})
    @patch("gcloud.utils.webhook.WebhookModel.objects.filter")
    def test_existing_config_means_enabled(self, webhook_filter, process_sensitive_info):
        webhook_filter.return_value.first.return_value = SimpleNamespace(
            method="POST",
            endpoint="https://example.com/webhook",
            extra_info={"token": "encrypted"},
        )

        result = get_webhook_configs("1")

        self.assertTrue(result["enable_webhook"])
        self.assertEqual(result["method"], "POST")
        self.assertEqual(result["endpoint"], "https://example.com/webhook")
        self.assertEqual(result["extra_info"], {"token": "decrypted"})
        process_sensitive_info.assert_called_once_with({"token": "encrypted"}, is_decrypt=True)
