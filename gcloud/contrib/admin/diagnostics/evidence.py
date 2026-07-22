# -*- coding: utf-8 -*-
"""
Lightweight evidence package builder for task-level diagnostics.
"""

from gcloud.taskflow3.models import TaskCallBackRecord, TaskFlowInstance, TaskFlowRelation


def build_task_evidence(task_id, node_id=""):
    task = TaskFlowInstance.objects.filter(id=task_id).select_related("pipeline_instance").first()
    if task is None:
        return {"result": False, "message": "task not found", "sections": {}}

    related_task_ids = list(TaskFlowRelation.objects.filter(root_task_id=task_id).values_list("task_id", flat=True))
    callback_records = list(TaskCallBackRecord.objects.filter(task_id__in=[task_id] + related_task_ids).values())
    relations = list(TaskFlowRelation.objects.filter(root_task_id=task_id).values())

    root_pipeline_id = task.pipeline_instance.instance_id if task.pipeline_instance else ""
    sections = {
        "task": {
            "id": task.id,
            "project_id": task.project_id,
            "engine_ver": task.engine_ver,
            "current_flow": task.current_flow,
            "root_pipeline_id": root_pipeline_id,
        },
        "relations": relations,
        "callback_records": callback_records,
        "node_id": node_id,
        "engine": _build_engine_evidence(root_pipeline_id),
    }
    return {"result": True, "message": "", "sections": sections}


def _build_engine_evidence(root_pipeline_id):
    """补充引擎运行时证据（进程心跳/节点起止时间/最近日志），fail-safe。"""
    if not root_pipeline_id:
        return {}
    try:
        from pipeline.eri.models import LogEntry, Process, State

        procs = list(
            Process.objects.filter(root_pipeline_id=root_pipeline_id).values(
                "id", "current_node_id", "dead", "last_heartbeat"
            )
        )
        node_ids = [p["current_node_id"] for p in procs if p["current_node_id"]]
        states = list(
            State.objects.filter(node_id__in=node_ids).values("node_id", "name", "started_time", "archived_time")
        )
        last_logs = list(
            LogEntry.objects.filter(node_id__in=node_ids).order_by("-logged_at").values("node_id", "logged_at")[:20]
        )
        return {"processes": procs, "states": states, "last_logs": last_logs}
    except Exception:
        return {}
