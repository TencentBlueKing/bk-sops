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

    sections = {
        "task": {
            "id": task.id,
            "project_id": task.project_id,
            "engine_ver": task.engine_ver,
            "current_flow": task.current_flow,
            "root_pipeline_id": task.pipeline_instance.instance_id if task.pipeline_instance else "",
        },
        "relations": relations,
        "callback_records": callback_records,
        "node_id": node_id,
    }
    return {"result": True, "message": "", "sections": sections}
