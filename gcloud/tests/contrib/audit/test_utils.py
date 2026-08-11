# -*- coding: utf-8 -*-
import json
from types import SimpleNamespace
from unittest import mock

from django.db import transaction
from django.test import SimpleTestCase, TestCase, override_settings

from gcloud.contrib.audit import utils


class DelegatedAuditUsernameTestCase(SimpleTestCase):
    def request(
        self,
        app_code="bk-sops-facade",
        app_verified=True,
        proxy="executor",
        operator=None,
        verified=True,
    ):
        meta = {}
        if operator is not None:
            meta["HTTP_X_BKSOPS_AUDIT_OPERATOR"] = operator
        return SimpleNamespace(
            user=SimpleNamespace(username=proxy),
            app=SimpleNamespace(bk_app_code=app_code, verified=app_verified),
            META=meta,
            _apigw_jwt_user_verified=verified,
            trace_id="trace-1",
        )

    @override_settings(BK_AUDIT_DELEGATED_OPERATOR_APPS={"bk-sops-facade"})
    def test_trusted_verified_request_uses_delegated_operator(self):
        self.assertEqual(utils.get_audit_username(self.request(operator="alice@tai")), "alice@tai")

    @override_settings(BK_AUDIT_DELEGATED_OPERATOR_APPS={"bk-sops-facade"})
    def test_untrusted_or_unverified_app_falls_back_to_proxy(self):
        self.assertEqual(
            utils.get_audit_username(self.request(app_code="other-app", operator="alice")),
            "executor",
        )
        self.assertEqual(
            utils.get_audit_username(self.request(operator="alice", app_verified=False)),
            "executor",
        )

    @override_settings(BK_AUDIT_DELEGATED_OPERATOR_APPS={"bk-sops-facade"})
    def test_trusted_app_uses_delegated_operator_for_unverified_gateway_user(self):
        self.assertEqual(
            utils.get_audit_username(self.request(operator="alice", verified=False)),
            "alice",
        )

    @override_settings(BK_AUDIT_DELEGATED_OPERATOR_APPS={"bk-sops-facade"})
    def test_event_kwargs_include_proxy_for_passwordless_trusted_delegation(self):
        self.assertEqual(
            utils.get_audit_event_kwargs(self.request(operator="alice", proxy="executor", verified=False)),
            {
                "username": "alice",
                "extend_data": {"proxy_username": "executor"},
            },
        )

    @override_settings(BK_AUDIT_DELEGATED_OPERATOR_APPS={"bk-sops-facade"})
    def test_event_kwargs_omit_proxy_without_effective_delegation(self):
        cases = (
            (
                self.request(operator=None, proxy="executor"),
                {"username": "executor", "extend_data": {}},
            ),
            (
                self.request(app_code="other-app", operator="alice", proxy="executor"),
                {"username": "executor", "extend_data": {}},
            ),
            (
                self.request(operator="executor", proxy="executor"),
                {"username": "executor", "extend_data": {}},
            ),
            (
                self.request(operator="alice", proxy=""),
                {"username": "alice", "extend_data": {}},
            ),
        )
        for request, expected in cases:
            with self.subTest(request=request):
                self.assertEqual(utils.get_audit_event_kwargs(request), expected)

    @override_settings(BK_AUDIT_DELEGATED_OPERATOR_APPS={"bk-sops-facade"})
    def test_missing_or_invalid_operator_falls_back_to_proxy(self):
        for operator in (None, "", "has space", "bad/value", "x" * 65):
            with self.subTest(operator=operator):
                self.assertEqual(utils.get_audit_username(self.request(operator=operator)), "executor")


class AuditUtilsTestCase(SimpleTestCase):
    @override_settings(ENABLE_BK_AUDIT=False)
    @mock.patch("gcloud.contrib.audit.utils.transaction.on_commit")
    def test_disabled_event_does_not_register_callback(self, on_commit):
        utils.bk_audit_add_event_on_commit(
            username="admin", action_id="task_edit", resource_id="task", instance=mock.Mock(id=1)
        )

        on_commit.assert_not_called()

    @override_settings(ENABLE_BK_AUDIT=True)
    @mock.patch("gcloud.contrib.audit.utils.transaction.on_commit")
    def test_enabled_event_registers_callback(self, on_commit):
        utils.bk_audit_add_event_on_commit(
            username="admin", action_id="task_edit", resource_id="task", instance=mock.Mock(id=1)
        )

        on_commit.assert_called_once()

    def test_sanitize_audit_data_removes_sensitive_and_large_fields(self):
        data = {
            "name": "task",
            "token": "secret-token",
            "nested": {"password": "secret-password", "safe": "value"},
            "pipeline_tree": {"activities": {"node": {}}},
            "constants": {"${password}": {"value": "secret-value"}},
            "headers": {"Authorization": "Bearer secret"},
        }

        sanitized = utils.sanitize_audit_data(data)

        self.assertEqual(sanitized["name"], "task")
        self.assertEqual(sanitized["token"], "******")
        self.assertEqual(sanitized["nested"]["password"], "******")
        self.assertEqual(sanitized["nested"]["safe"], "value")
        self.assertNotIn("pipeline_tree", sanitized)
        self.assertNotIn("constants", sanitized)
        self.assertNotIn("headers", sanitized)

    def test_sanitize_audit_data_redacts_nested_json_strings(self):
        data = {
            "notify_receivers": json.dumps(
                {
                    "receiver_group": ["Maintainers"],
                    "extra_info": {"token": "secret-token"},
                    "webhook_secret": "secret-value",
                }
            )
        }

        sanitized = json.loads(utils.sanitize_audit_data(data)["notify_receivers"])

        self.assertEqual(sanitized["receiver_group"], ["Maintainers"])
        self.assertNotIn("extra_info", sanitized)
        self.assertEqual(sanitized["webhook_secret"], "******")

    @override_settings(ENABLE_BK_AUDIT=True)
    @mock.patch("gcloud.contrib.audit.utils.build_instance", side_effect=RuntimeError("sdk failed"))
    def test_client_error_isolated_and_logged_without_instance_body(self, build_instance):
        instance = mock.Mock(id=1)
        instance.__str__ = mock.Mock(return_value="secret-instance-body")

        with self.assertLogs("root", level="ERROR") as logs:
            utils.bk_audit_add_event("admin", "task_edit", "task", instance)

        output = "\n".join(logs.output)
        self.assertIn("bk_audit_add_event_failed", output)
        self.assertIn("action_id=task_edit", output)
        self.assertIn("resource_id=task", output)
        self.assertIn("instance_id=1", output)
        self.assertNotIn("secret-instance-body", output)

    @override_settings(ENABLE_BK_AUDIT=True)
    def test_instance_id_error_isolated(self):
        class BrokenInstance(object):
            @property
            def id(self):
                raise RuntimeError("id unavailable")

        try:
            with self.assertLogs("root", level="ERROR") as logs:
                utils.bk_audit_add_event("admin", "task_edit", "task", BrokenInstance())
        except RuntimeError as error:
            self.fail("audit instance id error leaked to caller: {}".format(error))

        self.assertIn("bk_audit_add_event_failed", "\n".join(logs.output))

    @override_settings(ENABLE_BK_AUDIT=True)
    @mock.patch("gcloud.contrib.audit.utils.bk_audit_client.add_event")
    @mock.patch("gcloud.contrib.audit.utils.build_instance", return_value="audit-instance")
    def test_event_sanitizes_origin_and_current_data(self, build_instance, add_event):
        instance = mock.Mock(id=1)

        utils.bk_audit_add_event(
            "admin",
            "task_edit",
            "task",
            instance,
            origin_data={"password": "origin-secret", "name": "old"},
            data={"token": "current-secret", "name": "new", "pipeline_tree": {"activities": {}}},
        )

        origin_data = build_instance.call_args[0][2]
        current_data = build_instance.call_args[0][3]
        self.assertEqual(origin_data, {"password": "******", "name": "old"})
        self.assertEqual(current_data, {"token": "******", "name": "new"})
        add_event.assert_called_once()

    @override_settings(ENABLE_BK_AUDIT=True)
    @mock.patch("gcloud.contrib.audit.utils.bk_audit_client.add_event")
    @mock.patch("gcloud.contrib.audit.utils.build_instance", return_value="audit-instance")
    def test_event_sanitizes_and_forwards_extend_data(self, build_instance, add_event):
        utils.bk_audit_add_event(
            "alice",
            "task_operate",
            "task",
            mock.Mock(id=1),
            extend_data={
                "proxy_username": "executor",
                "access_token": "sensitive-value",
            },
        )

        self.assertEqual(
            add_event.call_args[1]["extend_data"],
            {
                "proxy_username": "executor",
                "access_token": "******",
            },
        )

    @override_settings(ENABLE_BK_AUDIT=True)
    def test_snapshot_accepts_lazy_data_builder(self):
        snapshot = utils.get_audit_snapshot(
            "periodic_task",
            mock.Mock(id=1),
            data=lambda: {"id": 1, "enabled": True},
        )

        self.assertEqual(snapshot, {"id": 1, "enabled": True})


class AuditTransactionTestCase(TestCase):
    @override_settings(ENABLE_BK_AUDIT=True)
    @mock.patch("gcloud.contrib.audit.utils.bk_audit_add_event")
    def test_commit_sends_once(self, add_event):
        with self.captureOnCommitCallbacks(execute=True):
            utils.bk_audit_add_event_on_commit(
                username="admin", action_id="task_edit", resource_id="task", instance=mock.Mock(id=1)
            )

        add_event.assert_called_once()

    @override_settings(ENABLE_BK_AUDIT=True)
    @mock.patch("gcloud.contrib.audit.utils.bk_audit_add_event")
    def test_commit_forwards_extend_data(self, add_event):
        with self.captureOnCommitCallbacks(execute=True):
            utils.bk_audit_add_event_on_commit(
                username="alice",
                action_id="task_operate",
                resource_id="task",
                instance=mock.Mock(id=1),
                extend_data={"proxy_username": "executor"},
            )

        self.assertEqual(
            add_event.call_args[1]["extend_data"],
            {"proxy_username": "executor"},
        )

    @override_settings(ENABLE_BK_AUDIT=True)
    @mock.patch("gcloud.contrib.audit.utils.bk_audit_add_event")
    def test_rollback_does_not_send(self, add_event):
        with self.captureOnCommitCallbacks(execute=True):
            try:
                with transaction.atomic():
                    utils.bk_audit_add_event_on_commit(
                        username="admin", action_id="task_edit", resource_id="task", instance=mock.Mock(id=1)
                    )
                    raise RuntimeError("rollback")
            except RuntimeError:
                pass

        add_event.assert_not_called()
