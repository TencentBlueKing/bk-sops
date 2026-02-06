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

import json
import logging
import re

import requests

from api.agent_client import AgentClient
from gcloud.utils.flow_converter import SimpleFlowConverter
from pipeline_web.drawing_new.drawing import draw_pipeline

logger = logging.getLogger("root")


class AgentProcessError(Exception):
    """智能体流程生成异常基类"""

    pass


class AgentAPIError(AgentProcessError):
    """智能体 API 调用异常"""

    pass


class AgentResponseParseError(AgentProcessError):
    """智能体响应解析异常"""

    pass


class FlowConversionError(AgentProcessError):
    """流程转换异常"""

    pass


class FlowLayoutError(AgentProcessError):
    """流程排版异常"""

    pass


def build_process_prompt(prompt: str, bk_biz_id: int) -> str:
    """
    构建流程生成的 prompt

    :param prompt: 用户输入的流程描述
    :param bk_biz_id: 业务ID
    :return: 完整的 prompt 内容
    """
    return (
        f"严格依据《标准运维流程知识库》中的示例结构进行编排。\n"
        f"Variable组件: 严格遵循知识库'2.2.9节'格式，无变量则不输出\n"
        f"业务 bk_biz_id：{bk_biz_id}\n"
        f"流程描述：{prompt}\n"
    )


def call_agent_api(prompt: str, bk_biz_id: int, username: str = "admin") -> dict:
    """
    调用智能体插件 API 生成流程

    :param prompt: 用户输入的流程描述
    :param bk_biz_id: 业务ID
    :param username: 用户名
    :return: API 响应结果
    """
    input_content = build_process_prompt(prompt, bk_biz_id)
    client = AgentClient(username=username)
    return client.call(input_content)


def _parse_json_array(content: str) -> list:
    """尝试解析标准 JSON 数组"""
    result = json.loads(content)
    if isinstance(result, list):
        return result
    return None


def _parse_json_lines(content: str) -> list:
    """尝试解析 JSON Lines 格式（每行一个 JSON 对象）"""
    result = []
    for line in content.strip().split("\n"):
        line = line.strip()
        if line:
            result.append(json.loads(line))
    return result if result else None


def _parse_json_content(content: str) -> list:
    """
    解析 JSON 内容，支持标准 JSON 数组和 JSON Lines 两种格式

    :param content: JSON 内容字符串
    :return: 解析后的列表
    :raises ValueError: 解析失败时抛出
    """
    parsers = [
        ("JSON array", _parse_json_array),
        ("JSON Lines", _parse_json_lines),
    ]

    for name, parser in parsers:
        try:
            result = parser(content)
            if result is not None:
                logger.info("_parse_json_content - Parsed as {} format, got {} items".format(name, len(result)))
                return result
        except json.JSONDecodeError:
            continue

    raise ValueError("JSON 解析失败, 原始内容: {}".format(content))


def _extract_json_content(content: str) -> str:
    """
    从智能体返回内容中提取 JSON 部分

    :param content: 原始内容
    :return: 提取的 JSON 内容
    """
    # 尝试匹配 ```json ... ```
    json_match = re.search(r"```json\s*([\s\S]*?)\s*```", content)
    if json_match:
        return json_match.group(1).strip()

    # 尝试匹配 ``` ... ```
    json_match = re.search(r"```\s*([\s\S]*?)\s*```", content)
    if json_match:
        return json_match.group(1).strip()

    # 尝试提取 JSON 数组
    start_idx = content.find("[")
    end_idx = content.rfind("]")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        return content[start_idx : end_idx + 1]

    return content.strip()


def parse_agent_response(agent_response: dict) -> list:
    """
    解析智能体 API 响应，提取生成的流程 JSON

    :param agent_response: 智能体 API 响应
    :return: 简化流程列表
    """
    if not agent_response.get("result"):
        raise ValueError("智能体 API 返回失败: {}".format(agent_response.get("message", "未知错误")))

    data = agent_response.get("data", {})
    choices = data.get("choices", [])

    if not choices:
        raise ValueError("智能体 API 返回数据为空")

    content = choices[0].get("delta", {}).get("content", "")

    if not content:
        raise ValueError("智能体 API 返回内容为空")

    logger.info("parse_agent_response - Raw content: {}".format(content[:500] if len(content) > 500 else content))

    json_content = _extract_json_content(content)

    logger.info(
        "parse_agent_response - JSON content to parse: {}".format(
            json_content[:300] if len(json_content) > 300 else json_content
        )
    )

    return _parse_json_content(json_content)


def generate_pipeline_tree(prompt: str, bk_biz_id: int, username: str = "admin") -> dict:
    """
    根据用户描述生成完整的 pipeline_tree

    :param prompt: 用户输入的流程描述
    :param bk_biz_id: 业务ID
    :param username: 用户名
    :return: 完整的 pipeline_tree
    :raises AgentAPIError: 智能体 API 调用失败
    :raises AgentResponseParseError: 智能体响应解析失败
    :raises FlowConversionError: 流程转换失败
    :raises FlowLayoutError: 流程排版失败
    """
    # 调用智能体 API
    try:
        agent_response = call_agent_api(prompt, bk_biz_id, username)
        simple_flow = parse_agent_response(agent_response)
    except requests.RequestException as e:
        logger.exception("generate_pipeline_tree: Agent API request failed - {}".format(str(e)))
        raise AgentAPIError("智能体 API 请求失败: {}".format(str(e)))
    except (ValueError, json.JSONDecodeError) as e:
        logger.exception("generate_pipeline_tree: Agent response parse failed - {}".format(str(e)))
        raise AgentResponseParseError("智能体响应解析失败: {}".format(str(e)))

    # 校验返回数据格式
    if not isinstance(simple_flow, list):
        raise AgentResponseParseError("智能体返回的数据不是有效的 JSON 数组")

    # 转换为 pipeline_tree
    try:
        converter = SimpleFlowConverter(simple_flow)
        pipeline_tree = converter.convert()
    except KeyError as e:
        logger.exception("generate_pipeline_tree: Missing required field - {}".format(str(e)))
        raise FlowConversionError("缺少必要字段: {}".format(str(e)))
    except Exception as e:
        logger.exception("generate_pipeline_tree: Conversion failed - {}".format(str(e)))
        raise FlowConversionError("流程转换失败: {}".format(str(e)))

    # 自动排版
    try:
        draw_pipeline(pipeline_tree)
    except Exception as e:
        logger.exception("generate_pipeline_tree: draw_pipeline failed - {}".format(str(e)))
        raise FlowLayoutError("流程自动排版失败: {}".format(str(e)))

    return pipeline_tree
