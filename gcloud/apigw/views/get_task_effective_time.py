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

from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.db.models import Sum
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
from gcloud.utils.dates import format_datetime


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


def _get_node_stat(node_id, node_stats_dict):
    """获取节点的统计信息"""
    return node_stats_dict.get(node_id)


def _get_all_node_stats_by_id(node_stats):
    """获取所有节点统计，按node_id分组"""
    nodes_by_id = defaultdict(list)
    for node in node_stats:
        nodes_by_id[node.node_id].append(node)
    return nodes_by_id


def _is_excluded_node(node_id, execution_data, node_stats_dict, excluded_component_codes):
    """判断节点是否是人工节点（需要排除的节点）"""
    if node_id not in execution_data.get("activities", {}):
        return False

    node_stat = _get_node_stat(node_id, node_stats_dict)
    if not node_stat:
        return False

    activity = execution_data["activities"][node_id]
    component_code = activity.get("component", {}).get("code", "")
    return component_code in excluded_component_codes


def _get_node_elapsed_time(node_id, node_stats_dict, nodes_by_id=None):
    """
    获取节点的耗时
    如果同一个node_id有多个执行记录，累加所有记录的耗时
    """
    total_time = 0
    if nodes_by_id and node_id in nodes_by_id:
        # 累加同一个node_id的所有节点的耗时
        for node_stat in nodes_by_id[node_id]:
            total_time += node_stat.elapsed_time or 0
    else:
        # 如果没有nodes_by_id，使用node_stats_dict（向后兼容）
        node_stat = _get_node_stat(node_id, node_stats_dict)
        if node_stat:
            total_time = node_stat.elapsed_time or 0
    return total_time


def _calculate_failure_wait_time_for_node(node_id, node_stat, user_operations_list):
    """
    计算单个失败节点的等待时间

    Args:
        node_id: 节点ID
        node_stat: 节点统计对象
        user_operations_list: 用户操作记录列表（已按operate_date排序）

    Returns:
        int: 等待时间（秒），如果没有等待则返回0
    """
    if not node_stat.is_skip or not node_stat.archived_time:
        return 0

    failure_time = node_stat.archived_time
    subsequent_operations = [op for op in user_operations_list if op.operate_date >= failure_time]

    if subsequent_operations:
        first_operation_after_failure = subsequent_operations[0]
        wait_time = (first_operation_after_failure.operate_date - failure_time).total_seconds()
        return max(0, int(wait_time))

    return 0


def _find_converge_gateway(execution_data, start_node_id, visited=None):
    """
    从起始节点开始，沿着流程找到第一个汇聚网关

    Returns:
        str: 汇聚网关ID，如果没找到返回None
    """
    if visited is None:
        visited = set()

    if start_node_id in visited:
        return None

    visited.add(start_node_id)

    gateways = execution_data.get("gateways", {})
    flows = execution_data.get("flows", {})
    activities = execution_data.get("activities", {})

    # 检查当前节点是否是汇聚网关
    if start_node_id in gateways:
        gateway = gateways[start_node_id]
        if gateway.get("type") == "ConvergeGateway":
            return start_node_id

    # 获取当前节点的outgoing flows
    outgoing_flows = []

    if start_node_id in gateways:
        gateway = gateways[start_node_id]
        outgoing = gateway.get("outgoing", [])
        if isinstance(outgoing, list):
            outgoing_flows = outgoing
        elif outgoing:
            outgoing_flows = [outgoing]
    elif start_node_id in activities:
        activity = activities[start_node_id]
        outgoing = activity.get("outgoing")
        if isinstance(outgoing, list):
            outgoing_flows = outgoing
        elif outgoing:
            outgoing_flows = [outgoing]

    # 递归查找每个outgoing flow的目标节点
    for flow_id in outgoing_flows:
        if flow_id not in flows:
            continue

        target_node_id = flows[flow_id].get("target")
        if not target_node_id:
            continue

        converge_gateway_id = _find_converge_gateway(execution_data, target_node_id, visited)
        if converge_gateway_id:
            return converge_gateway_id

    return None


def _dfs_calculate_effective_time(
    node_id,
    execution_data,
    node_stats_dict,
    excluded_component_codes,
    nodes_by_id=None,
    user_operations_list=None,
    visited=None,
    debug_info=None,
):
    """
    使用深度优先搜索计算从指定节点开始的有效耗时

    Args:
        node_id: 起始节点ID
        execution_data: 流程执行数据
        node_stats_dict: 节点统计字典
        excluded_component_codes: 需要排除的组件代码列表
        nodes_by_id: 按node_id分组的节点统计字典（用于计算重试间隔）
        user_operations_list: 用户操作记录列表（用于计算失败等待时间）
        visited: 已访问的节点集合（用于防止循环）
        debug_info: 调试信息字典（可选）

    Returns:
        int: 有效耗时（秒）
    """
    if visited is None:
        visited = set()

    if nodes_by_id is None:
        nodes_by_id = {}
    if user_operations_list is None:
        user_operations_list = []
    if debug_info is None:
        debug_info = {}

    if node_id in visited:
        return 0

    visited.add(node_id)

    gateways = execution_data.get("gateways", {})
    flows = execution_data.get("flows", {})
    activities = execution_data.get("activities", {})
    start_event = execution_data.get("start_event", {})
    end_event = execution_data.get("end_event", {})

    # 如果是结束节点，返回0
    if node_id == end_event.get("id"):
        return 0

    # 如果是汇聚网关，返回0（因为已经在并行网关处理过了）
    if node_id in gateways:
        gateway = gateways[node_id]
        if gateway.get("type") == "ConvergeGateway":
            return 0

        # 如果是活动节点（ServiceActivity）
    if node_id in activities:
        activity = activities[node_id]
        node_stat = _get_node_stat(node_id, node_stats_dict)

        # 记录调试信息
        if node_stat and debug_info is not None:
            # 计算该node_id所有节点的总耗时
            total_elapsed_time = _get_node_elapsed_time(node_id, node_stats_dict, nodes_by_id)
            node_info = {
                "node_id": node_id,
                "component_code": node_stat.component_code if node_stat else None,
                "elapsed_time": total_elapsed_time,
                "effective_time": 0,  # 将在后面设置
                "is_excluded": False,
            }
            if node_id not in debug_info.get("nodes", {}):
                debug_info.setdefault("nodes", {})[node_id] = node_info
            else:
                # 更新已存在的节点信息
                existing_info = debug_info["nodes"][node_id]
                existing_info["elapsed_time"] = total_elapsed_time

        # 如果是人工节点，排除其耗时
        is_excluded = _is_excluded_node(node_id, execution_data, node_stats_dict, excluded_component_codes)
        if is_excluded:
            # 记录调试信息
            if debug_info is not None and node_id in debug_info.get("nodes", {}):
                debug_info["nodes"][node_id]["is_excluded"] = True
                debug_info["nodes"][node_id]["effective_time"] = 0

            # 继续遍历后续节点
            outgoing = activity.get("outgoing")
            if outgoing:
                if isinstance(outgoing, list):
                    next_node_ids = [flows.get(fid, {}).get("target") for fid in outgoing if fid in flows]
                else:
                    next_node_id = flows.get(outgoing, {}).get("target")
                    next_node_ids = [next_node_id] if next_node_id else []

                total_result = 0
                for next_node_id in next_node_ids:
                    if next_node_id:
                        next_result = _dfs_calculate_effective_time(
                            next_node_id,
                            execution_data,
                            node_stats_dict,
                            excluded_component_codes,
                            nodes_by_id,
                            user_operations_list,
                            visited.copy(),
                            debug_info,
                        )
                        total_result += next_result

                return total_result

            return 0
        else:
            # 非人工节点，累加其耗时，然后继续遍历后续节点
            node_time = _get_node_elapsed_time(node_id, node_stats_dict, nodes_by_id)

            outgoing = activity.get("outgoing")
            if outgoing:
                if isinstance(outgoing, list):
                    next_node_ids = [flows.get(fid, {}).get("target") for fid in outgoing if fid in flows]
                else:
                    next_node_id = flows.get(outgoing, {}).get("target")
                    next_node_ids = [next_node_id] if next_node_id else []

                max_result = 0
                for next_node_id in next_node_ids:
                    if next_node_id:
                        next_result = _dfs_calculate_effective_time(
                            next_node_id,
                            execution_data,
                            node_stats_dict,
                            excluded_component_codes,
                            nodes_by_id,
                            user_operations_list,
                            visited.copy(),
                            debug_info,
                        )
                        if next_result > max_result:
                            max_result = next_result

                result_effective_time = node_time + max_result
                # 记录调试信息（有效时间只记录节点自身的耗时）
                if debug_info is not None and node_id in debug_info.get("nodes", {}):
                    debug_info["nodes"][node_id]["effective_time"] = node_time
                    debug_info["nodes"][node_id]["is_excluded"] = False

                return result_effective_time

            # 记录调试信息
            if debug_info is not None and node_id in debug_info.get("nodes", {}):
                debug_info["nodes"][node_id]["effective_time"] = node_time
                debug_info["nodes"][node_id]["is_excluded"] = False

            return node_time

    # 如果是并行网关或条件并行网关
    if node_id in gateways:
        gateway = gateways[node_id]
        gateway_type = gateway.get("type")

        if gateway_type in ["ParallelGateway", "ConditionalParallelGateway"]:
            # 找到对应的汇聚网关
            converge_gateway_id = None

            # 先尝试从gateway的converge_gateway_id属性获取
            if "converge_gateway_id" in gateway:
                converge_gateway_id = gateway["converge_gateway_id"]
            else:
                # 从第一个分支开始查找汇聚网关
                outgoing = gateway.get("outgoing", [])
                if isinstance(outgoing, list) and outgoing:
                    first_flow_id = outgoing[0]
                    if first_flow_id in flows:
                        first_target = flows[first_flow_id].get("target")
                        if first_target:
                            converge_gateway_id = _find_converge_gateway(execution_data, first_target)

            if not converge_gateway_id:
                # 如果找不到汇聚网关，按普通节点处理
                outgoing = gateway.get("outgoing", [])
                if isinstance(outgoing, list):
                    next_node_ids = [flows.get(fid, {}).get("target") for fid in outgoing if fid in flows]
                else:
                    next_node_id = flows.get(outgoing, {}).get("target") if outgoing else None
                    next_node_ids = [next_node_id] if next_node_id else []

                branch_results = []
                for next_node_id in next_node_ids:
                    if next_node_id:
                        branch_result = _dfs_calculate_effective_time(
                            next_node_id,
                            execution_data,
                            node_stats_dict,
                            excluded_component_codes,
                            nodes_by_id,
                            user_operations_list,
                            visited.copy(),
                            debug_info,
                        )
                        branch_results.append(branch_result)

                if branch_results:
                    return max(branch_results)

                return 0

            # 计算每个分支的有效耗时
            outgoing = gateway.get("outgoing", [])
            if not isinstance(outgoing, list):
                outgoing = [outgoing] if outgoing else []

            branch_results = []
            branch_details = []
            for flow_id in outgoing:

                if flow_id not in flows:
                    continue

                branch_start_node_id = flows[flow_id].get("target")
                if not branch_start_node_id:
                    continue

                # 计算从分支起始节点到汇聚网关的有效耗时
                branch_result = _dfs_calculate_effective_time_until_converge(
                    branch_start_node_id,
                    converge_gateway_id,
                    execution_data,
                    node_stats_dict,
                    excluded_component_codes,
                    nodes_by_id,
                    user_operations_list,
                    visited.copy(),
                    debug_info,
                )
                branch_results.append(branch_result)
                branch_details.append(
                    {
                        "branch_start_node_id": branch_start_node_id,
                        "branch_end_node_id": converge_gateway_id,
                        "effective_time": branch_result,
                    }
                )

            # 返回最大分支耗时（并行网关取各分支的最大值）
            if branch_results:
                max_branch = max(branch_results)
                # 记录并行网关调试信息
                if debug_info is not None:
                    parallel_gateway_info = {
                        "parallel_gateway_id": node_id,
                        "converge_gateway_id": converge_gateway_id,
                        "branches": branch_details,
                        "selected_branch_effective_time": max_branch,
                    }
                    debug_info.setdefault("parallel_gateways", []).append(parallel_gateway_info)
                return max_branch

            return 0

        elif gateway_type == "ExclusiveGateway":
            # 分支网关（条件网关），需要找到实际执行的分支
            # 这里简化处理：取所有分支的最大值（因为无法确定实际执行的分支）
            outgoing = gateway.get("outgoing", [])
            if not isinstance(outgoing, list):
                outgoing = [outgoing] if outgoing else []

            branch_results = []
            for flow_id in outgoing:
                if flow_id not in flows:
                    continue

                next_node_id = flows[flow_id].get("target")
                if next_node_id:
                    branch_result = _dfs_calculate_effective_time(
                        next_node_id,
                        execution_data,
                        node_stats_dict,
                        excluded_component_codes,
                        nodes_by_id,
                        user_operations_list,
                        visited.copy(),
                        debug_info,
                    )
                    branch_results.append(branch_result)

            if branch_results:
                max_branch = max(branch_results)
                return max_branch

            return 0

    # 如果是开始节点
    if node_id == start_event.get("id"):
        outgoing = start_event.get("outgoing")
        if outgoing:
            if isinstance(outgoing, list):
                next_node_ids = [flows.get(fid, {}).get("target") for fid in outgoing if fid in flows]
            else:
                next_node_id = flows.get(outgoing, {}).get("target")
                next_node_ids = [next_node_id] if next_node_id else []

            total_result = 0
            for next_node_id in next_node_ids:
                if next_node_id:
                    next_result = _dfs_calculate_effective_time(
                        next_node_id,
                        execution_data,
                        node_stats_dict,
                        excluded_component_codes,
                        nodes_by_id,
                        user_operations_list,
                        visited.copy(),
                        debug_info,
                    )
                    total_result += next_result
            return total_result

    return 0


def _dfs_calculate_effective_time_until_converge(
    node_id,
    converge_gateway_id,
    execution_data,
    node_stats_dict,
    excluded_component_codes,
    nodes_by_id=None,
    user_operations_list=None,
    visited=None,
    debug_info=None,
):
    """
    计算从指定节点到汇聚网关的有效耗时

    Args:
        node_id: 起始节点ID
        converge_gateway_id: 汇聚网关ID
        execution_data: 流程执行数据
        node_stats_dict: 节点统计字典
        excluded_component_codes: 需要排除的组件代码列表
        nodes_by_id: 按node_id分组的节点统计字典（用于计算重试间隔）
        user_operations_list: 用户操作记录列表（用于计算失败等待时间）
        visited: 已访问的节点集合
        debug_info: 调试信息字典（可选）

    Returns:
        int: 有效耗时（秒）
    """
    if visited is None:
        visited = set()

    if nodes_by_id is None:
        nodes_by_id = {}
    if user_operations_list is None:
        user_operations_list = []
    if debug_info is None:
        debug_info = {}

    if node_id in visited:
        return 0

    if node_id == converge_gateway_id:
        return 0

    visited.add(node_id)

    gateways = execution_data.get("gateways", {})
    flows = execution_data.get("flows", {})
    activities = execution_data.get("activities", {})
    # 如果是汇聚网关，返回0
    if node_id in gateways:
        gateway = gateways[node_id]
        if gateway.get("type") == "ConvergeGateway":
            return 0

    # 如果是活动节点
    if node_id in activities:
        activity = activities[node_id]
        node_stat = _get_node_stat(node_id, node_stats_dict)

        # 记录调试信息
        if node_stat and debug_info is not None:
            # 计算该node_id所有节点的总耗时
            total_elapsed_time = _get_node_elapsed_time(node_id, node_stats_dict, nodes_by_id)
            node_info = {
                "node_id": node_id,
                "component_code": node_stat.component_code if node_stat else None,
                "elapsed_time": total_elapsed_time,
                "effective_time": 0,  # 将在后面设置
                "is_excluded": False,
            }
            if node_id not in debug_info.get("nodes", {}):
                debug_info.setdefault("nodes", {})[node_id] = node_info
            else:
                # 更新已存在的节点信息
                existing_info = debug_info["nodes"][node_id]
                existing_info["elapsed_time"] = total_elapsed_time

        # 如果是人工节点，排除其耗时
        is_excluded = _is_excluded_node(node_id, execution_data, node_stats_dict, excluded_component_codes)
        if is_excluded:
            # 记录调试信息
            if debug_info is not None and node_id in debug_info.get("nodes", {}):
                debug_info["nodes"][node_id]["is_excluded"] = True
                debug_info["nodes"][node_id]["effective_time"] = 0

            # 继续遍历后续节点
            outgoing = activity.get("outgoing")
            if outgoing:
                if isinstance(outgoing, list):
                    next_node_ids = [flows.get(fid, {}).get("target") for fid in outgoing if fid in flows]
                else:
                    next_node_id = flows.get(outgoing, {}).get("target")
                    next_node_ids = [next_node_id] if next_node_id else []

                total_result = 0
                for next_node_id in next_node_ids:
                    if next_node_id:
                        next_result = _dfs_calculate_effective_time_until_converge(
                            next_node_id,
                            converge_gateway_id,
                            execution_data,
                            node_stats_dict,
                            excluded_component_codes,
                            nodes_by_id,
                            user_operations_list,
                            visited.copy(),
                            debug_info,
                        )
                        total_result += next_result

                return total_result

            return 0
        else:
            # 非人工节点，累加其耗时
            node_time = _get_node_elapsed_time(node_id, node_stats_dict, nodes_by_id)

            outgoing = activity.get("outgoing")
            if outgoing:
                if isinstance(outgoing, list):
                    next_node_ids = [flows.get(fid, {}).get("target") for fid in outgoing if fid in flows]
                else:
                    next_node_id = flows.get(outgoing, {}).get("target")
                    next_node_ids = [next_node_id] if next_node_id else []

                max_result = 0
                for next_node_id in next_node_ids:
                    if next_node_id:
                        next_result = _dfs_calculate_effective_time_until_converge(
                            next_node_id,
                            converge_gateway_id,
                            execution_data,
                            node_stats_dict,
                            excluded_component_codes,
                            nodes_by_id,
                            user_operations_list,
                            visited.copy(),
                            debug_info,
                        )
                        if next_result > max_result:
                            max_result = next_result

                result_effective_time = node_time + max_result
                # 记录调试信息（有效时间只记录节点自身的耗时）
                if debug_info is not None and node_id in debug_info.get("nodes", {}):
                    debug_info["nodes"][node_id]["effective_time"] = node_time
                    debug_info["nodes"][node_id]["is_excluded"] = False

                return result_effective_time

            # 记录调试信息
            if debug_info is not None and node_id in debug_info.get("nodes", {}):
                debug_info["nodes"][node_id]["effective_time"] = node_time
                debug_info["nodes"][node_id]["is_excluded"] = False

            return node_time

    # 如果是网关节点（非汇聚网关）
    if node_id in gateways:
        gateway = gateways[node_id]
        gateway_type = gateway.get("type")

        if gateway_type in ["ParallelGateway", "ConditionalParallelGateway"]:
            # 嵌套的并行网关，递归处理
            converge_gateway_id_nested = None
            if "converge_gateway_id" in gateway:
                converge_gateway_id_nested = gateway["converge_gateway_id"]
            else:
                outgoing = gateway.get("outgoing", [])
                if isinstance(outgoing, list) and outgoing:
                    first_flow_id = outgoing[0]
                    if first_flow_id in flows:
                        first_target = flows[first_flow_id].get("target")
                        if first_target:
                            converge_gateway_id_nested = _find_converge_gateway(execution_data, first_target)

            if converge_gateway_id_nested:
                outgoing = gateway.get("outgoing", [])
                if not isinstance(outgoing, list):
                    outgoing = [outgoing] if outgoing else []

                branch_results = []
                branch_details = []
                for flow_id in outgoing:
                    if flow_id not in flows:
                        continue

                    branch_start_node_id = flows[flow_id].get("target")
                    if not branch_start_node_id:
                        continue

                    branch_result = _dfs_calculate_effective_time_until_converge(
                        branch_start_node_id,
                        converge_gateway_id_nested,
                        execution_data,
                        node_stats_dict,
                        excluded_component_codes,
                        nodes_by_id,
                        user_operations_list,
                        visited.copy(),
                        debug_info,
                    )
                    branch_results.append(branch_result)
                    branch_details.append(
                        {
                            "branch_start_node_id": branch_start_node_id,
                            "branch_end_node_id": converge_gateway_id_nested,
                            "effective_time": branch_result,
                        }
                    )

                # 记录嵌套并行网关调试信息
                if debug_info is not None and branch_results:
                    max_branch_nested = max(branch_results)
                    parallel_gateway_info = {
                        "parallel_gateway_id": node_id,
                        "converge_gateway_id": converge_gateway_id_nested,
                        "branches": branch_details,
                        "selected_branch_effective_time": max_branch_nested,
                    }
                    debug_info.setdefault("parallel_gateways", []).append(parallel_gateway_info)

                # 继续遍历到外层汇聚网关
                if converge_gateway_id_nested != converge_gateway_id:
                    gateway_outgoing = gateways[converge_gateway_id_nested].get("outgoing")
                    if gateway_outgoing:
                        next_node_id = flows.get(gateway_outgoing, {}).get("target")
                        if next_node_id:
                            next_result = _dfs_calculate_effective_time_until_converge(
                                next_node_id,
                                converge_gateway_id,
                                execution_data,
                                node_stats_dict,
                                excluded_component_codes,
                                nodes_by_id,
                                user_operations_list,
                                visited.copy(),
                                debug_info,
                            )
                            if branch_results:
                                max_branch = max(branch_results)
                                return max_branch + next_result
                            return next_result

                if branch_results:
                    return max(branch_results)

                return 0

        elif gateway_type == "ExclusiveGateway":
            # 分支网关
            outgoing = gateway.get("outgoing", [])
            if not isinstance(outgoing, list):
                outgoing = [outgoing] if outgoing else []

            branch_results = []
            for flow_id in outgoing:
                if flow_id not in flows:
                    continue

                next_node_id = flows[flow_id].get("target")
                if next_node_id:
                    branch_result = _dfs_calculate_effective_time_until_converge(
                        next_node_id,
                        converge_gateway_id,
                        execution_data,
                        node_stats_dict,
                        excluded_component_codes,
                        nodes_by_id,
                        user_operations_list,
                        visited.copy(),
                        debug_info,
                    )
                    branch_results.append(branch_result)

            if branch_results:
                return max(branch_results)

            return 0

    return 0


def _calculate_effective_time_by_dfs(
    execution_data, node_stats, excluded_component_codes, task_instance_id=None, debug_info=None
):
    """
    使用深度优先搜索计算整个流程的有效耗时

    Args:
        execution_data: 流程执行数据
        node_stats: 节点统计查询集
        excluded_component_codes: 需要排除的组件代码列表
        task_instance_id: 任务实例ID（用于查询用户操作记录）
        debug_info: 调试信息字典（可选）

    Returns:
        dict: {
            'effective_time': int,  # 有效耗时（秒）
            'debug_info': dict,  # 调试信息（仅在debug模式下）
        }
    """
    if not execution_data:
        return {"effective_time": 0, "debug_info": debug_info if debug_info else None}

    # 构建节点统计字典
    node_stats_dict = {node.node_id: node for node in node_stats}

    # 构建按node_id分组的节点统计字典（用于计算重试间隔）
    nodes_by_id = _get_all_node_stats_by_id(node_stats)

    # 获取用户操作记录（用于计算失败等待时间）
    user_operations_list = []
    if task_instance_id:
        user_operations = TaskOperateRecord.objects.filter(
            instance_id=task_instance_id,
            operate_type__in=["revoke", "skip", "skip_exg", "skip_cpg", "retry"],
        ).order_by("operate_date")
        user_operations_list = list(user_operations)

    # 获取开始节点
    start_event = execution_data.get("start_event", {})
    start_node_id = start_event.get("id")

    if not start_node_id:
        return 0

    # 初始化调试信息
    if debug_info is None:
        debug_info = {}

    # 从开始节点开始DFS遍历
    result = _dfs_calculate_effective_time(
        start_node_id,
        execution_data,
        node_stats_dict,
        excluded_component_codes,
        nodes_by_id,
        user_operations_list,
        None,
        debug_info,
    )

    return {
        "effective_time": max(0, int(result)),
        "debug_info": debug_info if debug_info else None,
    }


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

    # 检查是否启用调试模式
    debug_mode = request.GET.get("debug", "0") == "1"

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

    # 计算需要排除的节点总耗时（人工节点）- 用于统计展示
    excluded_nodes = node_stats.filter(component_code__in=excluded_component_codes)
    excluded_time = excluded_nodes.aggregate(total_time=Sum("elapsed_time"))["total_time"] or 0

    # 总执行时间
    total_elapsed_time = task_stat.elapsed_time or 0

    # 获取执行树结构，用于DFS遍历计算有效时间
    execution_data = None
    try:
        dispatcher = TaskCommandDispatcher(
            engine_ver=task.engine_ver,
            taskflow_id=task.id,
            pipeline_instance=task.pipeline_instance,
            project_id=project.id,
        )
        status_result = dispatcher.get_task_status()
        if status_result.get("result"):
            execution_data = task.pipeline_instance.execution_data
    except Exception as e:
        logger.warning("Failed to get execution tree for effective time calculation: {}".format(e))

    # 使用DFS方法计算有效执行时间（只排除人工节点）
    # DFS方法会遍历整个流程，在遍历过程中统计：
    # 1. 排除人工节点的耗时
    # 2. 并行网关场景（取各分支最大有效耗时）
    # 注意：不再排除失败等待时间和重试间隔时间
    debug_info = {} if debug_mode else None

    if execution_data:
        dfs_result = _calculate_effective_time_by_dfs(
            execution_data, node_stats, excluded_component_codes, task_id, debug_info
        )
        effective_time_by_dfs = dfs_result["effective_time"]
        dfs_debug_info = dfs_result.get("debug_info")
    elif not excluded_component_codes:
        # 如果没有需要排除的组件，且无法获取执行数据，使用总时间
        effective_time_by_dfs = total_elapsed_time
        dfs_debug_info = None
    else:
        # 如果无法获取执行数据，使用旧方法计算（仅排除人工节点）
        effective_time_by_dfs = max(0, total_elapsed_time - excluded_time)
        dfs_debug_info = None

    # 最终有效时间 = DFS计算的有效时间（只排除人工节点，不再排除失败等待和重试间隔）
    effective_time = max(0, effective_time_by_dfs)

    # 统计排除的节点数量
    excluded_node_count = excluded_nodes.count()

    # 统计总节点数量
    total_node_count = node_stats.count()

    # 构建返回数据
    response_data = {
        "task_instance_id": task_stat.task_instance_id,
        "instance_id": task_stat.instance_id,
        "template_id": task_stat.template_id,
        "task_template_id": task_stat.task_template_id,
        "project_id": task_stat.project_id,
        "creator": task_stat.creator,
        "create_method": task_stat.create_method,
        "create_time": format_datetime(task_stat.create_time) if task_stat.create_time else None,
        "start_time": format_datetime(task_stat.start_time) if task_stat.start_time else None,
        "finish_time": format_datetime(task_stat.finish_time) if task_stat.finish_time else None,
        "total_elapsed_time": total_elapsed_time,
        "effective_time": effective_time,
        "excluded_node_count": excluded_node_count,
        "total_node_count": total_node_count,
        "excluded_component_codes": excluded_component_codes,
        "category": task_stat.category,
    }

    # 如果启用调试模式，添加调试信息
    if debug_mode and dfs_debug_info:
        # 整理节点明细
        node_details = []
        if "nodes" in dfs_debug_info:
            for node_id, node_info in dfs_debug_info["nodes"].items():
                node_details.append(
                    {
                        "node_id": node_id,
                        "component_code": node_info.get("component_code"),
                        "elapsed_time": node_info.get("elapsed_time", 0),
                        "effective_time": node_info.get("effective_time", 0),
                        "is_excluded": node_info.get("is_excluded", False),
                    }
                )

        # 并行网关明细
        parallel_gateway_details = dfs_debug_info.get("parallel_gateways", [])

        # 收集原始数据
        raw_data = {}

        # 节点统计数据
        node_stats_list = []
        for node_stat in node_stats:
            node_stats_list.append(
                {
                    "node_id": node_stat.node_id,
                    "component_code": node_stat.component_code,
                    "elapsed_time": node_stat.elapsed_time,
                    "started_time": format_datetime(node_stat.started_time) if node_stat.started_time else None,
                    "archived_time": format_datetime(node_stat.archived_time) if node_stat.archived_time else None,
                    "is_retry": node_stat.is_retry,
                    "is_skip": node_stat.is_skip,
                    "status": node_stat.status,
                    "template_node_id": getattr(node_stat, "template_node_id", None),
                }
            )
        raw_data["node_statistics"] = node_stats_list

        # 任务统计数据
        raw_data["task_statistics"] = {
            "task_instance_id": task_stat.task_instance_id,
            "instance_id": task_stat.instance_id,
            "template_id": task_stat.template_id,
            "task_template_id": task_stat.task_template_id,
            "project_id": task_stat.project_id,
            "creator": task_stat.creator,
            "create_method": task_stat.create_method,
            "create_time": format_datetime(task_stat.create_time) if task_stat.create_time else None,
            "start_time": format_datetime(task_stat.start_time) if task_stat.start_time else None,
            "finish_time": format_datetime(task_stat.finish_time) if task_stat.finish_time else None,
            "elapsed_time": task_stat.elapsed_time,
            "category": task_stat.category,
        }

        # 用户操作记录
        user_operations_raw = []
        if task_id:
            user_operations = TaskOperateRecord.objects.filter(
                instance_id=task_id,
                operate_type__in=["revoke", "skip", "skip_exg", "skip_cpg", "retry"],
            ).order_by("operate_date")
            for op in user_operations:
                user_operations_raw.append(
                    {
                        "instance_id": op.instance_id,
                        "operate_type": op.operate_type,
                        "operate_date": format_datetime(op.operate_date) if op.operate_date else None,
                        "operator": getattr(op, "operator", None),
                    }
                )
        raw_data["user_operations"] = user_operations_raw

        response_data["debug"] = {
            "node_details": node_details,
            "parallel_gateways": parallel_gateway_details,
            "raw_data": raw_data,
        }

    return {
        "result": True,
        "data": response_data,
        "code": err_code.SUCCESS.code,
    }
