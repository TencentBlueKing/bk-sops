# -*- coding: utf-8 -*-
"""
Reverse-mapping helpers: turn bamboo-engine ids (root_pipeline_id / node_id)
back into bk-sops task context that admins can understand.
"""

import logging

from django.conf import settings
from pipeline.models import PipelineInstance

from gcloud.taskflow3.models import TaskFlowInstance

logger = logging.getLogger("root")


def _format_dt(dt):
    try:
        return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None
    except Exception:  # noqa
        return None


def _task_url(project_id, task_id):
    host = getattr(settings, "BK_SOPS_HOST", "") or ""
    return "{}/taskflow/execute/{}/?instance_id={}".format(host.rstrip("/"), project_id, task_id)


def _summarize_task(task):
    pi = task.pipeline_instance
    project = getattr(task, "project", None)
    project_id = getattr(project, "id", None)
    project_name = getattr(project, "name", None)
    return {
        "task_id": task.id,
        "task_name": pi.name,
        "project_id": project_id,
        "project_name": project_name,
        "template_id": task.template_id,
        "executor": pi.executor,
        "create_time": _format_dt(pi.create_time),
        "task_url": _task_url(project_id, task.id) if project_id is not None else "",
    }


def resolve_task_summaries(root_pipeline_ids):
    """Batch map root_pipeline_id -> bk-sops task summary. Missing ids are omitted."""
    ids = [rid for rid in set(root_pipeline_ids or []) if rid]
    result = {}
    if not ids:
        return result
    try:
        qs = TaskFlowInstance.objects.filter(pipeline_instance__instance_id__in=ids).select_related(
            "pipeline_instance", "project"
        )
        for task in qs:
            pi = task.pipeline_instance
            if pi is None:
                continue
            try:
                result[pi.instance_id] = _summarize_task(task)
            except Exception:  # noqa - one bad row must not break the whole page
                logger.exception("[diagnostics] summarize task failed: task_id=%s", getattr(task, "id", None))
    except Exception:  # noqa - mapping is best-effort, never block the page
        logger.exception("[diagnostics] resolve_task_summaries failed")
        return result
    return result


def resolve_task_summary(root_pipeline_id):
    return resolve_task_summaries([root_pipeline_id]).get(root_pipeline_id)


def _find_node_name(tree, node_id):
    if not isinstance(tree, dict):
        return ""
    activities = tree.get("activities") or {}
    for nid, info in activities.items():
        if not isinstance(info, dict):
            continue
        if nid == node_id:
            return info.get("name") or ""
        if info.get("type") == "SubProcess":
            name = _find_node_name(info.get("pipeline"), node_id)
            if name:
                return name
    return ""


def resolve_node_name(root_pipeline_id, node_id):
    if not root_pipeline_id or not node_id:
        return ""
    try:
        pi = PipelineInstance.objects.filter(instance_id=root_pipeline_id).first()
        if pi is None:
            return ""
        return _find_node_name(pi.execution_data, node_id)
    except Exception:  # noqa - best-effort
        logger.exception("[diagnostics] resolve_node_name failed: root=%s node=%s", root_pipeline_id, node_id)
        return ""
