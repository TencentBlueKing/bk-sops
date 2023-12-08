# -*- coding: utf-8 -*-
import logging

from bamboo_engine import api as bamboo_engine_api
from bamboo_engine import states as bamboo_engine_states
from pipeline.eri.runtime import BambooDjangoRuntime

logger = logging.getLogger("root")


def force_tasks(tasks, username):
    for task in tasks:
        ctx = task.task_action("revoke", username)
        if ctx.get("result", False):
            try:
                force_failed_running_nodes(task.pipeline_instance.instance_id)
            except Exception as e:
                logger.exception("revoke task node failed, err={}".format(e))
                raise e
        else:
            raise Exception("revoke failed, result={}".format(ctx))


def force_failed_running_nodes(root_pipeline_id):
    # 获取当前任务正在运行的节点
    # kill 掉

    def _collect_running_nodes(task_status: dict) -> list:
        task_status["ex_data"] = {}
        children_list = [task_status["children"]]
        running_nodes = []
        while len(children_list) > 0:
            children = children_list.pop(0)
            for node_id, node in children.items():
                if node["state"] == bamboo_engine_states.RUNNING:
                    if len(node["children"]) > 0:
                        children_list.append(node["children"])
                        continue
                    running_nodes.append(node_id)
        return running_nodes

    status_result = bamboo_engine_api.get_pipeline_states(
        runtime=BambooDjangoRuntime(), root_id=root_pipeline_id, flat_children=True
    )
    running_nodes = _collect_running_nodes(status_result.data[root_pipeline_id])
    force_failed_details = {}

    for node_id in running_nodes:
        force_result = bamboo_engine_api.forced_fail_activity(
            runtime=BambooDjangoRuntime(),
            node_id=node_id,
            ex_data="auto forced fail this activity when the task revoked",
        )

        if not force_result.result:
            force_failed_details[node_id] = force_result.exc_trace

    if force_failed_details:
        raise Exception("终止流程下的节点失败, details={}".format(force_failed_details))
