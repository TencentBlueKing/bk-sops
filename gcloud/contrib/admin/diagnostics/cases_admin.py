# -*- coding: utf-8 -*-
"""
Admin-side write operations for diagnostic cases.

Status change must honor DiagnosticCase.unique_together
(root_pipeline_id, node_id, stuck_type, status): if a twin already holds the
target status, merge the recurrence into it and drop the duplicate row instead
of a naive update() that would raise IntegrityError.
"""

from django.db import transaction


def _models():
    from pipeline.contrib.diagnostics.models import DiagnosticCase, DiagnosticOperationAudit

    return DiagnosticCase, DiagnosticOperationAudit


def set_case_status(case_id, target_status, operator):
    try:
        DiagnosticCase, DiagnosticOperationAudit = _models()
    except ImportError as err:
        return {"result": False, "message": "pipeline diagnostics is unavailable: {}".format(err)}

    valid = {DiagnosticCase.STATUS_OPEN, DiagnosticCase.STATUS_RESOLVED, DiagnosticCase.STATUS_IGNORED}
    if target_status not in valid:
        return {"result": False, "message": "invalid status: {}".format(target_status)}

    with transaction.atomic():
        case = DiagnosticCase.objects.select_for_update().filter(id=case_id).first()
        if case is None:
            return {"result": False, "message": "case not found"}

        if case.status == target_status:
            return {"result": True, "data": {"id": case.id, "status": case.status, "merged": False}}

        twin = (
            DiagnosticCase.objects.select_for_update()
            .filter(
                root_pipeline_id=case.root_pipeline_id,
                node_id=case.node_id,
                stuck_type=case.stuck_type,
                status=target_status,
            )
            .exclude(id=case.id)
            .first()
        )

        if twin is not None:
            twin.hit_count = max(twin.hit_count, case.hit_count)
            if case.last_seen_at and (not twin.last_seen_at or case.last_seen_at > twin.last_seen_at):
                twin.last_seen_at = case.last_seen_at
            twin.save(update_fields=["hit_count", "last_seen_at", "updated_at"])
            surviving = twin
            case.delete()
            merged = True
        else:
            case.status = target_status
            case.save(update_fields=["status", "updated_at"])
            surviving = case
            merged = False

        DiagnosticOperationAudit.objects.create(
            case=surviving,
            operation_type="set_status:{}".format(target_status),
            operator=operator or "",
            mode=DiagnosticOperationAudit.MODE_APPLY,
            risk_level=DiagnosticOperationAudit.RISK_LEVEL_LOW,
            result={"status": target_status, "merged": merged},
        )

    return {"result": True, "data": {"id": surviving.id, "status": surviving.status, "merged": merged}}
