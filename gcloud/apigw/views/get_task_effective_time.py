# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from collections import defaultdict
from datetime import datetime

from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.db.models import Sum
from django.utils import timezone
from django.views.decorators.http import require_GET

from gcloud import err_code
from gcloud.analysis_statistics.models import TaskflowExecutedNodeStatistics, TaskflowStatistics
from gcloud.apigw.constants import PROJECT_SCOPE_CMDB_BIZ
from gcloud.apigw.decorators import mark_request_whether_is_trust, mcp_apigw, return_json_response
from gcloud.apigw.utils import get_project_with
from gcloud.apigw.views.utils import logger
from gcloud.contrib.operate_record.models import TaskOperateRecord
from gcloud.core.models import EnvironmentVariables, Project
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import TaskViewInterceptor
from gcloud.taskflow3.domains.dispatchers import TaskCommandDispatcher
from gcloud.taskflow3.models import TaskFlowInstance


def _get_excluded_component_codes():
    """
    从环境变量中获取需要排除的人工节点组件代码列表
    如果环境变量不存在，返回默认的排除节点列表
    """
    default_codes = []
    manual_waiting_codes = EnvironmentVariables.objects.get_var("MANUAL_WAITING_COMPONENT_CODES", "")
    if manual_waiting_codes:
        # 支持逗号分隔的多个组件代码
        codes = [code.strip() for code in manual_waiting_codes.split(",") if code.strip()]
        if codes:
            return codes
    return default_codes


def _check_revoke_operation(task_instance_id):
    """
    检查任务是否有终止操作
    """
    return TaskOperateRecord.objects.filter(instance_id=task_instance_id, operate_type="revoke").exists()


def _calculate_retry_node_time_adjustment(node_stats):
    """
    计算重试节点的耗时调整值
    对于is_retry=True的节点，忽略掉这个节点执行结束到下一个相同node_id节点（重试执行的新节点）开始之间这段时间的耗时
    """
    nodes_by_id = defaultdict(list)
    for node in node_stats:
        nodes_by_id[node.node_id].append(node)

    total_ignored_time = 0
    for node_id, nodes in nodes_by_id.items():
        if len(nodes) <= 1:
            continue

        nodes_sorted = sorted(
            nodes, key=lambda x: x.started_time if x.started_time else datetime.min.replace(tzinfo=timezone.utc)
        )

        for idx, current_node in enumerate(nodes_sorted):
            if not current_node.is_retry:
                continue

            if not current_node.archived_time:
                continue

            next_node = None
            for next_idx in range(idx + 1, len(nodes_sorted)):
                next_candidate = nodes_sorted[next_idx]
                if next_candidate.started_time:
                    next_node = next_candidate
                    break

            if next_node and next_node.started_time:
                retry_interval = (next_node.started_time - current_node.archived_time).total_seconds()
                if retry_interval > 0:
                    total_ignored_time += retry_interval

    return total_ignored_time


def _calculate_failure_wait_time(task_instance_id, instance_id, node_stats):
    """
    计算失败后等待时间：计算所有失败节点到用户操作（终止/跳过节点）之间的等待时间总和
    """
    failed_nodes = node_stats.filter(is_skip=True, archived_time__isnull=False).order_by("archived_time")

    if not failed_nodes.exists():
        return 0

    failed_nodes_list = list(failed_nodes)
    user_operations = TaskOperateRecord.objects.filter(
        instance_id=task_instance_id, operate_type__in=["revoke", "skip", "skip_exg", "skip_cpg", "retry"]
    ).order_by("operate_date")

    if not user_operations.exists():
        return 0

    user_operations_list = list(user_operations)
    total_wait_time = 0

    for failed_node in failed_nodes_list:
        failure_time = failed_node.archived_time
        if not failure_time:
            continue

        subsequent_operations = [op for op in user_operations_list if op.operate_date >= failure_time]
        if subsequent_operations:
            first_operation_after_failure = subsequent_operations[0]
            wait_time = (first_operation_after_failure.operate_date - failure_time).total_seconds()
            total_wait_time += max(0, int(wait_time))

    return max(0, int(total_wait_time))


def _find_parallel_gateway_branches(execution_data, status_tree, parallel_gateway_id, converge_gateway_id):
    """
    找出并行网关的所有分支节点ID集合

    Args:
        execution_data: 流程执行数据
        status_tree: 状态树
        parallel_gateway_id: 并行网关节点ID
        converge_gateway_id: 对应的汇聚网关节点ID

    Returns:
        list: 每个分支的节点ID列表
    """
    if parallel_gateway_id not in execution_data.get("gateways", {}):
        return []

    parallel_gateway = execution_data["gateways"][parallel_gateway_id]
    outgoing_flows = parallel_gateway.get("outgoing", [])

    if not isinstance(outgoing_flows, list):
        return []

    branches = []
    flows = execution_data.get("flows", {})

    for flow_id in outgoing_flows:
        if flow_id not in flows:
            continue

        flow = flows[flow_id]
        branch_start_node_id = flow.get("target")

        if not branch_start_node_id:
            continue

        # 从分支起始节点开始，沿着流程找到汇聚网关之前的所有节点
        branch_nodes = set()
        visited = set()
        queue = [branch_start_node_id]

        while queue:
            node_id = queue.pop(0)
            if node_id in visited or node_id == converge_gateway_id:
                continue

            visited.add(node_id)
            branch_nodes.add(node_id)

            # 如果是活动节点，添加到分支
            if node_id in execution_data.get("activities", {}):
                act = execution_data["activities"][node_id]
                outgoing = act.get("outgoing")
                if outgoing:
                    if isinstance(outgoing, list):
                        for out_flow_id in outgoing:
                            if out_flow_id in flows:
                                next_node = flows[out_flow_id].get("target")
                                if next_node and next_node != converge_gateway_id:
                                    queue.append(next_node)
                    else:
                        if outgoing in flows:
                            next_node = flows[outgoing].get("target")
                            if next_node and next_node != converge_gateway_id:
                                queue.append(next_node)

            # 如果是网关节点，继续遍历
            if node_id in execution_data.get("gateways", {}):
                gateway = execution_data["gateways"][node_id]
                gateway_outgoing = gateway.get("outgoing", [])
                if isinstance(gateway_outgoing, list):
                    for out_flow_id in gateway_outgoing:
                        if out_flow_id in flows:
                            next_node = flows[out_flow_id].get("target")
                            if next_node and next_node != converge_gateway_id:
                                queue.append(next_node)
                elif gateway_outgoing:
                    if gateway_outgoing in flows:
                        next_node = flows[gateway_outgoing].get("target")
                        if next_node and next_node != converge_gateway_id:
                            queue.append(next_node)

        if branch_nodes:
            branches.append(list(branch_nodes))

    return branches


def _calculate_branch_time(branch_node_ids, node_stats_dict):
    """
    计算分支的总耗时

    Args:
        branch_node_ids: 分支的节点ID列表
        node_stats_dict: 节点统计字典，key为node_id，value为节点统计对象

    Returns:
        int: 分支总耗时（秒）
    """
    branch_start_time = None
    branch_end_time = None

    for node_id in branch_node_ids:
        if node_id not in node_stats_dict:
            continue

        node_stat = node_stats_dict[node_id]
        if node_stat.started_time:
            if branch_start_time is None or node_stat.started_time < branch_start_time:
                branch_start_time = node_stat.started_time

        if node_stat.archived_time:
            if branch_end_time is None or node_stat.archived_time > branch_end_time:
                branch_end_time = node_stat.archived_time

    if branch_start_time and branch_end_time:
        return int((branch_end_time - branch_start_time).total_seconds())

    return 0


def _calculate_parallel_gateway_excluded_time_adjustment(
    task, execution_data, status_tree, node_stats, excluded_component_codes
):
    """
    计算并行网关场景下需要调整的排除时间

    对于并行网关中的非关键路径分支，如果分支中有人工节点，且该分支不是最慢的分支，
    则只排除超出关键路径的部分

    Returns:
        int: 需要调整的排除时间（秒），正数表示需要减少排除时间
    """
    if not execution_data or not status_tree:
        return 0

    gateways = execution_data.get("gateways", {})
    flows = execution_data.get("flows", {})

    # 找出所有并行网关及其对应的汇聚网关
    parallel_gateways = []
    for gateway_id, gateway in gateways.items():
        if gateway.get("type") != "ParallelGateway":
            continue

        # 收集并行网关的所有分支起始节点
        outgoing = gateway.get("outgoing", [])
        if not isinstance(outgoing, list):
            continue

        branch_start_nodes = []
        for flow_id in outgoing:
            if flow_id in flows:
                target_node = flows[flow_id].get("target")
                if target_node:
                    branch_start_nodes.append(target_node)

        if len(branch_start_nodes) < 2:
            continue

        # 沿着每个分支找到汇聚网关
        # 方法：从每个分支起始节点开始，沿着流程找到第一个ConvergeGateway
        converge_gateways_found = []
        for start_node in branch_start_nodes:
            visited = set()
            queue = [start_node]
            found_converge = None

            while queue and not found_converge:
                node_id = queue.pop(0)
                if node_id in visited:
                    continue
                visited.add(node_id)

                # 检查是否是汇聚网关
                if node_id in gateways:
                    target_gateway = gateways[node_id]
                    if target_gateway.get("type") == "ConvergeGateway":
                        found_converge = node_id
                        break
                    else:
                        # 如果是其他类型的网关节点，继续查找它的outgoing
                        gateway_outgoing = target_gateway.get("outgoing", [])
                        if isinstance(gateway_outgoing, list):
                            for out_flow_id in gateway_outgoing:
                                if out_flow_id in flows:
                                    next_node = flows[out_flow_id].get("target")
                                    if next_node:
                                        queue.append(next_node)
                        elif gateway_outgoing:
                            if gateway_outgoing in flows:
                                next_node = flows[gateway_outgoing].get("target")
                                if next_node:
                                    queue.append(next_node)
                    continue

                # 如果是活动节点，继续查找它的outgoing
                if node_id in execution_data.get("activities", {}):
                    act = execution_data["activities"][node_id]
                    act_outgoing = act.get("outgoing")
                    if act_outgoing:
                        if isinstance(act_outgoing, list):
                            for out_flow_id in act_outgoing:
                                if out_flow_id in flows:
                                    next_node = flows[out_flow_id].get("target")
                                    if next_node:
                                        queue.append(next_node)
                        else:
                            if act_outgoing in flows:
                                next_node = flows[act_outgoing].get("target")
                                if next_node:
                                    queue.append(next_node)

            if found_converge:
                converge_gateways_found.append(found_converge)

        # 如果所有分支都指向同一个汇聚网关，则是对应的汇聚网关
        if converge_gateways_found and len(set(converge_gateways_found)) == 1:
            converge_gateway_id = converge_gateways_found[0]
            parallel_gateways.append((gateway_id, converge_gateway_id))

    if not parallel_gateways:
        return 0

    # 构建节点统计字典
    node_stats_dict = {node.node_id: node for node in node_stats}

    total_adjustment = 0

    for parallel_gateway_id, converge_gateway_id in parallel_gateways:
        # 找出所有分支
        branches = _find_parallel_gateway_branches(
            execution_data, status_tree, parallel_gateway_id, converge_gateway_id
        )

        if len(branches) < 2:
            continue

        # 计算每个分支的总耗时
        branch_times = []
        for branch_node_ids in branches:
            branch_time = _calculate_branch_time(branch_node_ids, node_stats_dict)
            branch_times.append((branch_node_ids, branch_time))

        if not branch_times:
            continue

        # 找出关键路径（最慢的分支）
        branch_times.sort(key=lambda x: x[1], reverse=True)
        critical_path_time = branch_times[0][1]

        if critical_path_time == 0:
            continue

        # 对于非关键路径分支，计算需要调整的排除时间
        for branch_node_ids, branch_time in branch_times[1:]:
            if branch_time >= critical_path_time:
                # 如果分支时间大于等于关键路径，不需要调整
                continue

            # 计算该分支中人工节点的总耗时
            branch_excluded_time = 0
            for node_id in branch_node_ids:
                if node_id in node_stats_dict:
                    node_stat = node_stats_dict[node_id]
                    if node_stat.component_code in excluded_component_codes:
                        branch_excluded_time += node_stat.elapsed_time or 0

            # 如果分支中有人工节点，且分支时间小于关键路径时间
            # 说明该分支不是关键路径，分支中的人工节点不影响总执行时间
            # 调整值 = 分支中人工节点耗时（完全排除，因为不影响总时间）
            if branch_excluded_time > 0:
                total_adjustment += branch_excluded_time

    return total_adjustment


@login_exempt
@require_GET
@apigw_require
@mcp_apigw()
@return_json_response
@mark_request_whether_is_trust
@iam_intercept(TaskViewInterceptor())
def get_task_effective_time(request, task_id, bk_biz_id):
    """
    统计任务的有效执行时间（排除人工节点及其等待时间，以及失败后等待时间）
    """
    # 获取项目对象，支持通过 bk_biz_id 查询
    try:
        scope = request.GET.get("scope", PROJECT_SCOPE_CMDB_BIZ)
        project = get_project_with(obj_id=bk_biz_id, scope=scope)
    except Project.DoesNotExist:
        return {
            "result": False,
            "message": "project(bk_biz_id={bk_biz_id}) does not exist".format(bk_biz_id=bk_biz_id),
            "code": err_code.CONTENT_NOT_EXIST.code,
        }

    try:
        task = TaskFlowInstance.objects.get(pk=task_id, project_id=project.id, is_deleted=False)
    except TaskFlowInstance.DoesNotExist:
        message = "task[id={task_id}] does not exist".format(task_id=task_id)
        logger.exception(message)
        return {
            "result": False,
            "message": message,
            "code": err_code.CONTENT_NOT_EXIST.code,
        }

    # 检查任务是否已完成
    if not task.pipeline_instance.finish_time:
        return {
            "result": False,
            "message": "task[id={task_id}] is not finished yet".format(task_id=task_id),
            "code": err_code.REQUEST_PARAM_INVALID.code,
        }

    # 检查任务是否有终止操作，如果有则返回错误
    if _check_revoke_operation(task_id):
        return {
            "result": False,
            "message": "task[id={task_id}] was revoked, cannot calculate effective time".format(task_id=task_id),
            "code": err_code.REQUEST_PARAM_INVALID.code,
        }

    # 获取需要排除的节点组件代码列表
    excluded_component_codes = _get_excluded_component_codes()

    # 获取任务统计信息
    try:
        task_stat = TaskflowStatistics.objects.get(task_instance_id=task_id)
    except TaskflowStatistics.DoesNotExist:
        return {
            "result": False,
            "message": "task statistics not found for task[id={task_id}]".format(task_id=task_id),
            "code": err_code.CONTENT_NOT_EXIST.code,
        }

    # 获取该任务的所有节点执行记录
    node_stats = TaskflowExecutedNodeStatistics.objects.filter(instance_id=task_stat.instance_id)

    # 计算需要排除的节点总耗时（人工节点）
    excluded_nodes = node_stats.filter(component_code__in=excluded_component_codes)
    excluded_time = excluded_nodes.aggregate(total_time=Sum("elapsed_time"))["total_time"] or 0

    # 计算重试节点的耗时调整
    retry_node_time_adjustment = _calculate_retry_node_time_adjustment(node_stats)

    # 总执行时间
    total_elapsed_time = task_stat.elapsed_time or 0

    # 计算失败后等待时间
    failure_wait_time = _calculate_failure_wait_time(task_id, task_stat.instance_id, node_stats)

    # 获取执行树结构，用于处理并行网关场景
    execution_data = None
    status_tree = None
    try:
        dispatcher = TaskCommandDispatcher(
            engine_ver=task.engine_ver,
            taskflow_id=task.id,
            pipeline_instance=task.pipeline_instance,
            project_id=project.id,
        )
        status_result = dispatcher.get_task_status()
        if status_result.get("result"):
            status_tree = status_result.get("data", {})
            execution_data = task.pipeline_instance.execution_data
    except Exception as e:
        logger.warning("Failed to get execution tree for parallel gateway analysis: {}".format(e))

    # 计算并行网关场景下的排除时间调整
    parallel_gateway_adjustment = 0
    if execution_data and status_tree and excluded_component_codes:
        parallel_gateway_adjustment = _calculate_parallel_gateway_excluded_time_adjustment(
            task, execution_data, status_tree, node_stats, excluded_component_codes
        )

    # 计算有效执行时间 = 总执行时间 - 排除节点时间 - 失败后等待时间 - 重试节点耗时调整 + 并行网关调整
    # 并行网关调整为正数，表示需要减少排除时间（因为非关键路径分支中的人工节点不影响总时间）
    effective_time = max(
        0,
        total_elapsed_time
        - excluded_time
        - failure_wait_time
        - retry_node_time_adjustment
        + parallel_gateway_adjustment,
    )

    # 统计排除的节点数量
    excluded_node_count = excluded_nodes.count()

    # 统计总节点数量
    total_node_count = node_stats.count()

    return {
        "result": True,
        "data": {
            "task_instance_id": task_stat.task_instance_id,
            "instance_id": task_stat.instance_id,
            "template_id": task_stat.template_id,
            "task_template_id": task_stat.task_template_id,
            "project_id": task_stat.project_id,
            "creator": task_stat.creator,
            "create_method": task_stat.create_method,
            "create_time": task_stat.create_time.strftime("%Y-%m-%d %H:%M:%S") if task_stat.create_time else None,
            "start_time": task_stat.start_time.strftime("%Y-%m-%d %H:%M:%S") if task_stat.start_time else None,
            "finish_time": task_stat.finish_time.strftime("%Y-%m-%d %H:%M:%S") if task_stat.finish_time else None,
            "total_elapsed_time": total_elapsed_time,
            "excluded_time": excluded_time,
            "failure_wait_time": failure_wait_time,
            "retry_node_time_adjustment": retry_node_time_adjustment,
            "parallel_gateway_adjustment": parallel_gateway_adjustment,
            "effective_time": effective_time,
            "excluded_node_count": excluded_node_count,
            "total_node_count": total_node_count,
            "has_excluded_nodes": excluded_node_count > 0,
            "excluded_component_codes": excluded_component_codes,
            "category": task_stat.category,
        },
        "code": err_code.SUCCESS.code,
    }
