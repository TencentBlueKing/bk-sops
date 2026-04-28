# -*- coding: utf-8 -*-
"""
Admin views that expose bk-sops task context on top of bamboo-engine diagnostics.
"""

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from gcloud.contrib.admin.diagnostics.context import get_task_context
from gcloud.core.decorators import check_is_superuser
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.admin import AdminViewViewInterceptor


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
