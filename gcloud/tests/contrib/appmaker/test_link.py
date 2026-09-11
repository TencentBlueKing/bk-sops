from unittest import mock

from django.test import SimpleTestCase

from gcloud.contrib.appmaker.api import get_appmaker_link_prefix
from gcloud.contrib.appmaker.models import AppMakerManager
from gcloud.core.apis.drf.serilaziers.appmaker import AppmakerSerializer


class AppMakerLinkTestCase(SimpleTestCase):
    @mock.patch("gcloud.contrib.appmaker.api.settings.IS_LOCAL", True)
    def test_local_link_prefix_contains_request_scheme_and_host(self):
        request = mock.Mock()
        request.build_absolute_uri.return_value = "http://dev.example.com:8000/appmaker/"

        prefix = get_appmaker_link_prefix(request)

        self.assertEqual(prefix, "http://dev.example.com:8000/appmaker/")
        request.build_absolute_uri.assert_called_once_with("/appmaker/")

    @mock.patch("gcloud.contrib.appmaker.api.settings.APP_HOST", "https://apps.example.com/bk--sops/")
    @mock.patch("gcloud.contrib.appmaker.api.settings.IS_LOCAL", False)
    def test_deployed_link_prefix_preserves_application_subpath(self):
        prefix = get_appmaker_link_prefix(mock.Mock())

        self.assertEqual(prefix, "https://apps.example.com/bk--sops/appmaker/")

    def test_build_app_link_replaces_old_route_values(self):
        link = AppMakerManager.build_app_link("https://new.example.com/bk--sops/appmaker/", 8, 10, 20)

        self.assertEqual(
            link,
            "https://new.example.com/bk--sops/appmaker/8/newtask/10/selectnode/?template_id=20",
        )

    @mock.patch("gcloud.core.apis.drf.serilaziers.appmaker.settings.IS_LOCAL", True)
    def test_serializer_rebuilds_stored_link_from_current_request(self):
        request = mock.Mock()
        request.build_absolute_uri.return_value = "http://dev.example.com:8000/appmaker/"
        app = mock.Mock(id=8, project_id=10, task_template_id=20)

        link = AppmakerSerializer(context={"request": request}).get_link(app)

        self.assertEqual(
            link,
            "http://dev.example.com:8000/appmaker/8/newtask/10/selectnode/?template_id=20",
        )
