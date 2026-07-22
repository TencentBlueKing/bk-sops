# -*- coding: utf-8 -*-
"""
Task-level action orchestration for the generic pipeline diagnostics operations.
"""

ACTION_OPERATION_NAMES = {
    "inspect_ack_converge": "inspect_ack_converge",
    "inspect_node_runtime_readiness": "inspect_node_runtime_readiness",
    "replay_callback_data": "replay_callback_data",
    "resend_schedule": "resend_schedule",
    "expire_stale_schedule": "expire_stale_schedule",
}

SCHEDULE_ACTIONS = {"resend_schedule", "expire_stale_schedule"}
INSPECT_ACTIONS = {"inspect_ack_converge", "inspect_node_runtime_readiness"}


def _blocked(message):
    return {"result": False, "message": message, "blockers": [message], "data": {}}


def _load_operation(action):
    from pipeline.contrib.diagnostics import operations

    return getattr(operations, ACTION_OPERATION_NAMES[action])


def _operation_result_to_dict(result):
    if hasattr(result, "_asdict"):
        return result._asdict()
    if isinstance(result, dict):
        return result
    return _blocked("invalid operation result")


def run_task_action(task_id, node_id, action, operator, mode="dry_run", **kwargs):
    if action not in ACTION_OPERATION_NAMES:
        return _blocked("unsupported action")

    if action in INSPECT_ACTIONS:
        root_pipeline_id = kwargs.get("root_pipeline_id")
        if not root_pipeline_id:
            return _blocked("root_pipeline_id is required")
        operation_args = (root_pipeline_id, node_id)
    elif action == "replay_callback_data":
        callback_data_id = kwargs.get("callback_data_id")
        if not callback_data_id:
            return _blocked("callback_data_id is required")
        operation_args = (callback_data_id,)
    elif action in SCHEDULE_ACTIONS:
        schedule_id = kwargs.get("schedule_id")
        if not schedule_id:
            return _blocked("schedule_id is required")
        operation_args = (schedule_id,)
    else:
        return _blocked("unsupported action")

    try:
        operation = _load_operation(action)
    except ImportError as err:
        return _blocked("pipeline diagnostics is unavailable: {}".format(err))

    result = operation(*operation_args, operator=operator, mode=mode)
    return _operation_result_to_dict(result)
