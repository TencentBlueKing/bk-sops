# -*- coding: utf-8 -*-
"""
Admin views that expose bk-sops task context on top of bamboo-engine diagnostics.
"""

import json

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from gcloud.contrib.admin.diagnostics.actions import run_task_action
from gcloud.contrib.admin.diagnostics.context import get_task_context
from gcloud.contrib.admin.diagnostics.task_mapping import (
    resolve_node_name,
    resolve_task_summaries,
    resolve_task_summary,
)
from gcloud.core.decorators import check_is_superuser
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.admin import AdminEditViewInterceptor, AdminViewViewInterceptor

_CASE_FILTER_FIELDS = ("status", "stuck_type", "severity", "root_pipeline_id", "node_id")


def _diagnostic_case_model():
    try:
        from pipeline.contrib.diagnostics.models import DiagnosticCase

        return DiagnosticCase, ""
    except ImportError as err:
        return None, "pipeline diagnostics is unavailable: {}".format(err)


def _serialize_case(case):
    return {
        "id": case.id,
        "root_pipeline_id": case.root_pipeline_id,
        "node_id": case.node_id,
        "stuck_type": case.stuck_type,
        "severity": case.severity,
        "status": case.status,
        "confidence": case.confidence,
        "hit_count": case.hit_count,
        "first_seen_at": case.first_seen_at.isoformat() if case.first_seen_at else None,
        "last_seen_at": case.last_seen_at.isoformat() if case.last_seen_at else None,
        "stall_seconds": (case.evidence or {}).get("stall_seconds"),
        "message": case.message,
    }


def _audit_model():
    try:
        from pipeline.contrib.diagnostics.models import DiagnosticOperationAudit

        return DiagnosticOperationAudit
    except ImportError:
        return None


def _serialize_audit(audit):
    return {
        "id": audit.id,
        "operation_type": audit.operation_type,
        "operator": audit.operator,
        "mode": audit.mode,
        "risk_level": audit.risk_level,
        "result": audit.result,
        "created_at": audit.created_at.strftime("%Y-%m-%d %H:%M:%S") if audit.created_at else None,
    }


def _diagnose_pipeline(root_pipeline_id, node_id=""):
    try:
        from pipeline.contrib.diagnostics.scanner import diagnose_pipeline
    except ImportError as err:
        return None, "pipeline diagnostics is unavailable: {}".format(err)

    return diagnose_pipeline(root_pipeline_id, node_id=node_id), ""


@require_GET
@check_is_superuser()
@iam_intercept(AdminViewViewInterceptor())
def task_diagnostic_page(request):
    return render(request, "diagnostics/task_diagnostic.html")


@require_GET
@check_is_superuser()
@iam_intercept(AdminViewViewInterceptor())
def diagnostic_board(request):
    return render(request, "diagnostics/cases.html")


@require_GET
@check_is_superuser()
@iam_intercept(AdminViewViewInterceptor())
def task_diagnostic_detail(request):
    task_id = request.GET.get("task_id")
    if not task_id:
        return JsonResponse({"result": False, "message": "task_id is required", "data": None})

    node_id = request.GET.get("node_id", "")
    context = get_task_context(task_id)
    hits, message = _diagnose_pipeline(context["root_pipeline_id"], node_id=node_id)
    if hits is None:
        return JsonResponse({"result": False, "message": message, "data": {"context": context}})

    return JsonResponse(
        {
            "result": True,
            "data": {
                "context": context,
                "diagnostics": [hit._asdict() for hit in hits],
            },
        }
    )


@require_POST
@check_is_superuser()
@iam_intercept(AdminEditViewInterceptor())
def task_diagnostic_action(request):
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except ValueError:
        return JsonResponse({"result": False, "message": "invalid json body", "blockers": ["invalid json body"]})

    action_kwargs = dict(body)
    task_id = action_kwargs.pop("task_id", None)
    node_id = action_kwargs.pop("node_id", "")
    action = action_kwargs.pop("action", None)
    mode = action_kwargs.pop("mode", "dry_run")

    result = run_task_action(
        task_id=task_id, node_id=node_id, action=action, operator=request.user.username, mode=mode, **action_kwargs
    )
    return JsonResponse(result)


@require_GET
@check_is_superuser()
@iam_intercept(AdminViewViewInterceptor())
def diagnostic_case_list(request):
    model, message = _diagnostic_case_model()
    if model is None:
        return JsonResponse({"result": False, "message": message, "data": None})

    qs = model.objects.all()
    for field in _CASE_FILTER_FIELDS:
        value = request.GET.get(field)
        if value:
            qs = qs.filter(**{field: value})

    try:
        page_size = min(max(int(request.GET.get("page_size", 50)), 1), 200)
        page_index = max(int(request.GET.get("page", 1)), 1)
    except (TypeError, ValueError):
        return JsonResponse({"result": False, "message": "invalid page params", "data": None})

    paginator = Paginator(qs.order_by("-last_seen_at"), page_size)
    page_obj = paginator.get_page(page_index)
    cases = list(page_obj.object_list)
    summaries = resolve_task_summaries([c.root_pipeline_id for c in cases])
    items = []
    for case in cases:
        item = _serialize_case(case)
        item["task"] = summaries.get(case.root_pipeline_id)
        items.append(item)
    data = {
        "total": paginator.count,
        "page": page_obj.number,
        "page_size": page_size,
        "items": items,
    }
    return JsonResponse({"result": True, "data": data})


@require_GET
@check_is_superuser()
@iam_intercept(AdminViewViewInterceptor())
def diagnostic_case_detail(request):
    model, message = _diagnostic_case_model()
    if model is None:
        return JsonResponse({"result": False, "message": message, "data": None})

    case_id = request.GET.get("case_id")
    if not case_id:
        return JsonResponse({"result": False, "message": "case_id is required", "data": None})

    case = model.objects.filter(id=case_id).first()
    if case is None:
        return JsonResponse({"result": False, "message": "case not found", "data": None})

    detail = _serialize_case(case)
    detail["evidence"] = case.evidence
    detail["related_objects"] = case.related_objects
    detail["recommended_actions"] = case.recommended_actions
    detail["forbidden_actions"] = case.forbidden_actions
    detail["task"] = resolve_task_summary(case.root_pipeline_id)
    detail["node_name"] = resolve_node_name(case.root_pipeline_id, case.node_id)
    audit_model = _audit_model()
    if audit_model is not None:
        audits = audit_model.objects.filter(case_id=case.id).order_by("-created_at")[:50]
        detail["audit_history"] = [_serialize_audit(a) for a in audits]
    else:
        detail["audit_history"] = []
    return JsonResponse({"result": True, "data": detail})


@require_POST
@check_is_superuser()
@iam_intercept(AdminEditViewInterceptor())
def diagnostic_case_status(request):
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except ValueError:
        return JsonResponse({"result": False, "message": "invalid json body"})

    case_id = body.get("case_id")
    status = body.get("status")
    if not case_id or not status:
        return JsonResponse({"result": False, "message": "case_id and status are required"})

    from gcloud.contrib.admin.diagnostics.cases_admin import set_case_status

    return JsonResponse(set_case_status(case_id, status, request.user.username))


@require_POST
@check_is_superuser()
@iam_intercept(AdminEditViewInterceptor())
def diagnostic_case_action(request):
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except ValueError:
        return JsonResponse({"result": False, "message": "invalid json body", "blockers": ["invalid json body"]})

    model, message = _diagnostic_case_model()
    if model is None:
        return JsonResponse({"result": False, "message": message, "blockers": [message]})

    case_id = body.get("case_id")
    action = body.get("action")
    mode = body.get("mode", "dry_run")
    if not case_id or not action:
        return JsonResponse({"result": False, "message": "case_id and action are required"})

    case = model.objects.filter(id=case_id).first()
    if case is None:
        return JsonResponse({"result": False, "message": "case not found"})

    evidence = case.evidence or {}
    related = case.related_objects or {}
    action_kwargs = {"root_pipeline_id": case.root_pipeline_id}
    schedule_id = body.get("schedule_id") or evidence.get("schedule_id") or related.get("schedule_id")
    callback_data_id = (
        body.get("callback_data_id") or evidence.get("callback_data_id") or related.get("callback_data_id")
    )
    if schedule_id is not None:
        action_kwargs["schedule_id"] = schedule_id
    if callback_data_id is not None:
        action_kwargs["callback_data_id"] = callback_data_id

    result = run_task_action(
        task_id=None,
        node_id=case.node_id,
        action=action,
        operator=request.user.username,
        mode=mode,
        **action_kwargs,
    )
    return JsonResponse(result)
