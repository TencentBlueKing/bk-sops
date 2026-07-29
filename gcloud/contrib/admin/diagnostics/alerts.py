# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger("root")


def build_task_alert_payload(case, task_context):
    return {
        "task_id": task_context.get("task_id"),
        "project_id": task_context.get("project_id"),
        "root_pipeline_id": case.root_pipeline_id,
        "node_id": case.node_id,
        "stuck_type": case.stuck_type,
        "severity": case.severity,
        "evidence": case.evidence,
        "recommended_actions": case.recommended_actions,
        "message": case.message,
    }


def emit_task_alert(case, task_context):
    payload = build_task_alert_payload(case, task_context)
    logger.warning("[bk_sops_task_diagnostic_alert] %s", payload)
    return payload
