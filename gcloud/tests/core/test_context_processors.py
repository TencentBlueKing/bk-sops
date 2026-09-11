from django.test import SimpleTestCase, override_settings

from gcloud.core.context_processors import _cmdb_create_business_url


class CmdbCreateBusinessUrlTest(SimpleTestCase):
    @override_settings(BK_CC_HOST=None)
    def test_missing_cmdb_host_does_not_break_page_rendering(self):
        self.assertEqual(_cmdb_create_business_url(), "")

    @override_settings(BK_CC_HOST="https://cmdb.example.test/")
    def test_builds_current_cmdb_business_create_route(self):
        self.assertEqual(
            _cmdb_create_business_url(),
            "https://cmdb.example.test/#/resource/business?create=true",
        )
