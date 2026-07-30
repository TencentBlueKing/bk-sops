# -*- coding: utf-8 -*-
from unittest import skipUnless

from django.test import TransactionTestCase

try:
    import pipeline.contrib.diagnostics  # noqa: F401

    DIAGNOSTICS_AVAILABLE = True
except ImportError:
    DIAGNOSTICS_AVAILABLE = False


@skipUnless(DIAGNOSTICS_AVAILABLE, "pipeline.contrib.diagnostics unavailable (requires bamboo-pipeline>=3.24.13)")
class SetCaseStatusTest(TransactionTestCase):
    def setUp(self):
        from pipeline.contrib.diagnostics.models import DiagnosticCase

        self.DiagnosticCase = DiagnosticCase

    def _make(self, status, hit_count=1):
        return self.DiagnosticCase.objects.create(
            root_pipeline_id="root-1",
            node_id="n1",
            stuck_type="stalled_no_progress",
            severity=self.DiagnosticCase.SEVERITY_WARNING,
            status=status,
            hit_count=hit_count,
        )

    def test_open_to_resolved_normal(self):
        from pipeline.contrib.diagnostics.models import DiagnosticOperationAudit

        from gcloud.contrib.admin.diagnostics.cases_admin import set_case_status

        case = self._make(self.DiagnosticCase.STATUS_OPEN)
        res = set_case_status(case.id, self.DiagnosticCase.STATUS_RESOLVED, "admin")

        self.assertTrue(res["result"])
        self.assertFalse(res["data"]["merged"])
        case.refresh_from_db()
        self.assertEqual(case.status, self.DiagnosticCase.STATUS_RESOLVED)
        self.assertEqual(DiagnosticOperationAudit.objects.filter(case_id=case.id).count(), 1)

    def test_merge_when_twin_exists_no_integrity_error(self):
        from datetime import timedelta

        from django.utils import timezone
        from pipeline.contrib.diagnostics.models import DiagnosticOperationAudit

        from gcloud.contrib.admin.diagnostics.cases_admin import set_case_status

        twin = self._make(self.DiagnosticCase.STATUS_RESOLVED, hit_count=2)
        open_case = self._make(self.DiagnosticCase.STATUS_OPEN, hit_count=5)

        newer = timezone.now()
        older = newer - timedelta(hours=1)
        twin.last_seen_at = older
        twin.save(update_fields=["last_seen_at"])
        open_case.last_seen_at = newer
        open_case.save(update_fields=["last_seen_at"])

        res = set_case_status(open_case.id, self.DiagnosticCase.STATUS_RESOLVED, "admin")

        self.assertTrue(res["result"])
        self.assertTrue(res["data"]["merged"])
        self.assertEqual(res["data"]["id"], twin.id)
        # 原 open case 已删除,孪生 case 命中数取较大值
        self.assertFalse(self.DiagnosticCase.objects.filter(id=open_case.id).exists())
        twin.refresh_from_db()
        self.assertEqual(twin.hit_count, 5)
        # last_seen_at 合并取较新的值(open_case 的值),而不是保留孪生自身旧值
        self.assertGreater(twin.last_seen_at, older)
        # 审计记录挂在存活的孪生 case 上,不悬挂在已删除的 open_case 上
        self.assertEqual(DiagnosticOperationAudit.objects.filter(case_id=twin.id).count(), 1)
        self.assertEqual(DiagnosticOperationAudit.objects.filter(case_id=open_case.id).count(), 0)

    def test_noop_when_same_status(self):
        from pipeline.contrib.diagnostics.models import DiagnosticOperationAudit

        from gcloud.contrib.admin.diagnostics.cases_admin import set_case_status

        case = self._make(self.DiagnosticCase.STATUS_OPEN)
        res = set_case_status(case.id, self.DiagnosticCase.STATUS_OPEN, "admin")
        self.assertTrue(res["result"])
        self.assertFalse(res["data"]["merged"])
        # no-op 不应写入多余审计
        self.assertEqual(DiagnosticOperationAudit.objects.count(), 0)

    def test_invalid_status_rejected(self):
        from gcloud.contrib.admin.diagnostics.cases_admin import set_case_status

        case = self._make(self.DiagnosticCase.STATUS_OPEN)
        res = set_case_status(case.id, "bogus", "admin")
        self.assertFalse(res["result"])

    def test_missing_case(self):
        from gcloud.contrib.admin.diagnostics.cases_admin import set_case_status

        res = set_case_status(999999, self.DiagnosticCase.STATUS_RESOLVED, "admin")
        self.assertFalse(res["result"])
