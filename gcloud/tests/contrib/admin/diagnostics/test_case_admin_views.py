# -*- coding: utf-8 -*-
import json
from unittest import mock, skipUnless

from django.test import RequestFactory, TestCase

try:
    import pipeline.contrib.diagnostics  # noqa: F401

    DIAGNOSTICS_AVAILABLE = True
except ImportError:
    DIAGNOSTICS_AVAILABLE = False

_VIEW_INTERCEPTOR = "gcloud.iam_auth.view_interceptors.admin.AdminViewViewInterceptor.process"
_EDIT_INTERCEPTOR = "gcloud.iam_auth.view_interceptors.admin.AdminEditViewInterceptor.process"


def _superuser_get(path, **params):
    request = RequestFactory().get(path, data=params)
    request.user = mock.MagicMock(is_superuser=True, username="admin")
    request.session = {}
    return request


def _superuser_post(path, body):
    request = RequestFactory().post(path, data=json.dumps(body), content_type="application/json")
    request.user = mock.MagicMock(is_superuser=True, username="admin")
    return request


@skipUnless(DIAGNOSTICS_AVAILABLE, "pipeline.contrib.diagnostics unavailable (requires bamboo-pipeline>=3.24.13)")
class CaseListEnrichmentTest(TestCase):
    def setUp(self):
        from pipeline.contrib.diagnostics.models import DiagnosticCase

        self.DiagnosticCase = DiagnosticCase
        self.case = DiagnosticCase.objects.create(
            root_pipeline_id="root-1",
            node_id="n1",
            stuck_type="stalled_no_progress",
            severity=DiagnosticCase.SEVERITY_WARNING,
            status=DiagnosticCase.STATUS_OPEN,
            evidence={"stall_seconds": 120},
        )

    def test_list_items_carry_task_summary(self):
        from gcloud.contrib.admin.views import diagnostics

        summaries = {"root-1": {"task_id": 9, "task_name": "任务A", "task_url": "u", "project_name": "业务X"}}
        with mock.patch(_VIEW_INTERCEPTOR), mock.patch(
            "gcloud.contrib.admin.views.diagnostics.resolve_task_summaries", return_value=summaries
        ):
            resp = diagnostics.diagnostic_case_list(_superuser_get("/admin/diagnostics/cases/"))

        item = json.loads(resp.content)["data"]["items"][0]
        self.assertEqual(item["task"]["task_id"], 9)
        self.assertEqual(item["task"]["task_name"], "任务A")

    def test_list_item_task_none_when_unmapped(self):
        from gcloud.contrib.admin.views import diagnostics

        with mock.patch(_VIEW_INTERCEPTOR), mock.patch(
            "gcloud.contrib.admin.views.diagnostics.resolve_task_summaries", return_value={}
        ):
            resp = diagnostics.diagnostic_case_list(_superuser_get("/admin/diagnostics/cases/"))

        item = json.loads(resp.content)["data"]["items"][0]
        self.assertIsNone(item["task"])


@skipUnless(DIAGNOSTICS_AVAILABLE, "pipeline.contrib.diagnostics unavailable (requires bamboo-pipeline>=3.24.13)")
class CaseDetailEnrichmentTest(TestCase):
    def setUp(self):
        from pipeline.contrib.diagnostics.models import DiagnosticCase, DiagnosticOperationAudit

        self.DiagnosticCase = DiagnosticCase
        self.case = DiagnosticCase.objects.create(
            root_pipeline_id="root-1",
            node_id="n1",
            stuck_type="stalled_no_progress",
            severity=DiagnosticCase.SEVERITY_WARNING,
            status=DiagnosticCase.STATUS_OPEN,
            evidence={"stall_seconds": 120},
        )
        DiagnosticOperationAudit.objects.create(case=self.case, operation_type="set_status:resolved", operator="admin")

    def test_detail_has_task_node_name_and_audit(self):
        from gcloud.contrib.admin.views import diagnostics

        with mock.patch(_VIEW_INTERCEPTOR), mock.patch(
            "gcloud.contrib.admin.views.diagnostics.resolve_task_summary",
            return_value={"task_id": 9, "task_name": "任务A"},
        ), mock.patch("gcloud.contrib.admin.views.diagnostics.resolve_node_name", return_value="HTTP 请求"):
            resp = diagnostics.diagnostic_case_detail(
                _superuser_get("/admin/diagnostics/cases/detail/", case_id=self.case.id)
            )

        data = json.loads(resp.content)["data"]
        self.assertEqual(data["task"]["task_id"], 9)
        self.assertEqual(data["node_name"], "HTTP 请求")
        self.assertEqual(len(data["audit_history"]), 1)
        self.assertEqual(data["audit_history"][0]["operation_type"], "set_status:resolved")
        self.assertFalse(data["replayable"])
        self.assertEqual(data["recovery_history"], [])

    def test_detail_lists_recoveries_of_replayable_case(self):
        from pipeline.contrib.diagnostics.models import DiagnosticRecovery

        from gcloud.contrib.admin.views import diagnostics

        case = self.DiagnosticCase.objects.create(
            root_pipeline_id="root-1", node_id="n2", stuck_type="execute_dispatch_lost", evidence={}
        )
        DiagnosticRecovery.objects.create(
            case=case,
            root_pipeline_id="root-1",
            node_id="n2",
            stuck_type="execute_dispatch_lost",
            fingerprint="execute_dispatch_lost:1:n2:v1",
            message={"kind": "execute"},
            trigger="manual",
            mode="apply",
            status="dispatched",
            operator="admin",
        )
        with mock.patch(_VIEW_INTERCEPTOR), mock.patch(
            "gcloud.contrib.admin.views.diagnostics.resolve_task_summary", return_value=None
        ), mock.patch("gcloud.contrib.admin.views.diagnostics.resolve_node_name", return_value=""):
            resp = diagnostics.diagnostic_case_detail(
                _superuser_get("/admin/diagnostics/cases/detail/", case_id=case.id)
            )

        data = json.loads(resp.content)["data"]
        self.assertTrue(data["replayable"])
        [recovery] = data["recovery_history"]
        self.assertEqual(
            (recovery["trigger"], recovery["mode"], recovery["status"], recovery["operator"]),
            ("manual", "apply", "dispatched", "admin"),
        )
        self.assertIsNone(recovery["settled_at"])


@skipUnless(DIAGNOSTICS_AVAILABLE, "pipeline.contrib.diagnostics unavailable (requires bamboo-pipeline>=3.24.13)")
class CaseActionViewTest(TestCase):
    def setUp(self):
        from pipeline.contrib.diagnostics.models import DiagnosticCase

        self.case = DiagnosticCase.objects.create(
            root_pipeline_id="root-1",
            node_id="n1",
            stuck_type="ack_not_converged",
            severity=DiagnosticCase.SEVERITY_WARNING,
            status=DiagnosticCase.STATUS_OPEN,
            evidence={"schedule_id": 555},
        )

    def test_action_dispatches_with_case_context(self):
        from gcloud.contrib.admin.views import diagnostics

        captured = {}

        def _fake_run(**kwargs):
            captured.update(kwargs)
            return {"result": True, "data": {"preview": "ok"}}

        with mock.patch(_EDIT_INTERCEPTOR), mock.patch(
            "gcloud.contrib.admin.views.diagnostics.run_task_action", side_effect=_fake_run
        ):
            resp = diagnostics.diagnostic_case_action(
                _superuser_post(
                    "/admin/diagnostics/cases/action/",
                    {"case_id": self.case.id, "action": "resend_schedule", "mode": "dry_run"},
                )
            )

        body = json.loads(resp.content)
        self.assertTrue(body["result"])
        self.assertEqual(captured["action"], "resend_schedule")
        self.assertEqual(captured["node_id"], "n1")
        self.assertEqual(captured["mode"], "dry_run")
        self.assertEqual(captured["operator"], "admin")
        # schedule_id 从 evidence 兜底
        self.assertEqual(captured["schedule_id"], 555)
        self.assertEqual(captured["root_pipeline_id"], "root-1")

    def test_replay_case_routes_to_case_replay(self):
        from gcloud.contrib.admin.views import diagnostics

        with mock.patch(_EDIT_INTERCEPTOR), mock.patch(
            "gcloud.contrib.admin.views.diagnostics.run_case_replay", return_value={"result": True}
        ) as m_replay, mock.patch("gcloud.contrib.admin.views.diagnostics.run_task_action") as m_task:
            resp = diagnostics.diagnostic_case_action(
                _superuser_post(
                    "/admin/diagnostics/cases/action/",
                    {"case_id": self.case.id, "action": "replay_case", "mode": "apply", "confirm_risk": True},
                )
            )

        self.assertTrue(json.loads(resp.content)["result"])
        m_replay.assert_called_once_with(self.case.id, "admin", mode="apply", confirm_risk=True)
        m_task.assert_not_called()

    def test_replay_case_reaches_engine(self):
        from pipeline.contrib.diagnostics.models import DiagnosticOperationAudit

        from gcloud.contrib.admin.views import diagnostics

        with mock.patch(_EDIT_INTERCEPTOR):
            resp = diagnostics.diagnostic_case_action(
                _superuser_post("/admin/diagnostics/cases/action/", {"case_id": self.case.id, "action": "replay_case"})
            )

        body = json.loads(resp.content)
        self.assertEqual((body["result"], body["blockers"]), (False, ["stuck type is not replayable"]))
        audit = DiagnosticOperationAudit.objects.get(case_id=self.case.id)
        self.assertEqual((audit.operation_type, audit.mode), ("replay_case", "dry_run"))

    def test_action_missing_case(self):
        from gcloud.contrib.admin.views import diagnostics

        with mock.patch(_EDIT_INTERCEPTOR):
            resp = diagnostics.diagnostic_case_action(
                _superuser_post("/admin/diagnostics/cases/action/", {"case_id": 999999, "action": "resend_schedule"})
            )
        self.assertFalse(json.loads(resp.content)["result"])

    def test_action_forbidden_for_non_superuser(self):
        from gcloud.contrib.admin.views import diagnostics

        req = _superuser_post(
            "/admin/diagnostics/cases/action/", {"case_id": self.case.id, "action": "resend_schedule"}
        )
        req.user = mock.MagicMock(is_superuser=False, username="normal")
        with mock.patch(_EDIT_INTERCEPTOR):
            resp = diagnostics.diagnostic_case_action(req)
        self.assertEqual(resp.status_code, 403)


class DiagnosticBoardViewTest(TestCase):
    def test_board_renders_for_superuser(self):
        from gcloud.contrib.admin.views import diagnostics

        with mock.patch(_VIEW_INTERCEPTOR):
            resp = diagnostics.diagnostic_board(_superuser_get("/admin/diagnostics/board/"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"diagnostics-board", resp.content)
        self.assertIn(b"replayCase", resp.content)

    def test_board_forbidden_for_non_superuser(self):
        from gcloud.contrib.admin.views import diagnostics

        req = _superuser_get("/admin/diagnostics/board/")
        req.user = mock.MagicMock(is_superuser=False, username="normal")
        with mock.patch(_VIEW_INTERCEPTOR):
            resp = diagnostics.diagnostic_board(req)
        self.assertEqual(resp.status_code, 403)
