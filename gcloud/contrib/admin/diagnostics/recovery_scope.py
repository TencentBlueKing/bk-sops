# -*- coding: utf-8 -*-
"""
Scope resolver for pipeline diagnostics auto replay: the engine calls it by dotted path
(PIPELINE_DIAGNOSTICS_RECOVERY_SCOPE_RESOLVER) with a root_pipeline_id.
"""

from django.conf import settings

from gcloud.taskflow3.models import TaskFlowInstance


def _project_ids():
    raw = getattr(settings, "DIAGNOSTICS_RECOVERY_PROJECT_IDS", ())
    items = raw.split(",") if isinstance(raw, str) else raw
    return {str(item).strip() for item in items or () if str(item).strip()}


def in_recovery_scope(root_pipeline_id):
    """根流程所属项目在白名单内才允许自动重放；白名单为空时不放开，含 * 时放开全部，查不到任务时不放开。"""
    project_ids = _project_ids()
    if not project_ids:
        return False
    project_id = (
        TaskFlowInstance.objects.filter(pipeline_instance__instance_id=root_pipeline_id)
        .values_list("project_id", flat=True)
        .first()
    )
    if project_id is None:
        return False
    return "*" in project_ids or str(project_id) in project_ids
