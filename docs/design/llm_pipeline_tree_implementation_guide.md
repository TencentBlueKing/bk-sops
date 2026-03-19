# 使用大模型构建 pipeline_tree 的实施步骤指南

## 一、项目背景与目标

### 1.1 背景
标准运维 (SOPS) 使用 `pipeline_tree` 作为流程定义的核心数据结构，通过可视化界面进行任务流程编排与执行。为了提升流程创建效率，需要利用大模型自动生成符合项目规范的 `pipeline_tree`。

### 1.2 目标
- 确保大模型生成的 `pipeline_tree` 完全符合项目规范
- 保证生成的流程可以直接使用，无需人工修正
- 建立完善的验证和反馈机制

## 二、pipeline_tree 核心规范

### 2.1 数据结构要求

#### 2.1.1 必需字段
`pipeline_tree` 必须包含以下字段：
- `start_event`: 开始节点（必需）
- `end_event`: 结束节点（必需）
- `activities`: 任务节点字典（必需）
- `flows`: 顺序流字典（必需）
- `gateways`: 网关节点字典（必需，可为空）
- `constants`: 全局变量字典（必需，可为空）
- `outputs`: 输出变量列表（必需，可为空）

#### 2.1.2 ID 命名规范
- **节点 ID (Node ID)**: 必须以 `n` 开头，后跟小写字母和数字，格式：`^n[0-9a-z]+`
  - 示例：`node76393dcfedcf73dbc726f1c4786d`
- **连线 ID (Flow ID)**: 必须以 `l` 开头，后跟小写字母和数字，格式：`^l[0-9a-z]+`
  - 示例：`line490caa49d2a03e64829693281032`
- **变量 Key**: 格式为 `${key_name}`，不能以 `_env_` 或 `_system.` 开头，格式：`^\$\{(?!_env_|_system\.)[a-zA-Z0-9_]+\}$`
  - 示例：`${script_timeout}`, `${custom_key1}`

#### 2.1.3 节点名称长度限制
- 活动节点名称：最大长度 50 字符
- 常量名称：最大长度 50 字符

### 2.2 start_event 规范

```json
{
  "id": "node<unique_id>",
  "name": "",  // 可为空字符串
  "type": "EmptyStartEvent",  // 固定值
  "incoming": "",  // 必须为空字符串
  "outgoing": "line<flow_id>"  // 必须指向一个 flow ID
}
```

**要求**：
- `type` 必须是 `"EmptyStartEvent"`
- `incoming` 必须为空字符串
- `outgoing` 必须是单个 flow ID（字符串类型）

### 2.3 end_event 规范

```json
{
  "id": "node<unique_id>",
  "name": "",  // 可为空字符串
  "type": "EmptyEndEvent",  // 固定值
  "incoming": "line<flow_id>" | ["line<flow_id>", ...],  // 单个或多个 flow ID
  "outgoing": ""  // 必须为空字符串
}
```

**要求**：
- `type` 必须是 `"EmptyEndEvent"`
- `incoming` 可以是字符串或字符串数组
- `outgoing` 必须为空字符串

### 2.4 activities 规范

#### 2.4.1 ServiceActivity（普通任务节点）

```json
{
  "node<activity_id>": {
    "id": "node<activity_id>",
    "type": "ServiceActivity",
    "name": "节点名称",  // 1-50 字符
    "incoming": "line<flow_id>" | ["line<flow_id>", ...],
    "outgoing": "line<flow_id>",
    "optional": true | false,
    "component": {
      "code": "组件代码",  // 如 "job_fast_execute_script", "sleep_timer"
      "data": {
        "param_name": {
          "hook": false | true,  // 是否引用变量
          "value": "值" | "${variable_key}"  // 实际值或变量引用
        }
      }
    },
    "error_ignorable": false,  // 是否可忽略错误
    "retryable": true,  // 是否可重试（新规范）
    "skippable": false  // 是否可跳过（新规范）
  }
}
```

**要求**：
- `type` 必须是 `"ServiceActivity"`
- `name` 长度 1-50 字符
- `component.code` 必须是有效的组件代码
- `component.data` 中的每个参数必须包含 `hook` 和 `value` 字段

#### 2.4.2 SubProcess（子流程节点）

```json
{
  "node<subprocess_id>": {
    "id": "node<subprocess_id>",
    "type": "SubProcess",
    "name": "子流程名称",
    "incoming": "line<flow_id>" | ["line<flow_id>", ...],
    "outgoing": "line<flow_id>",
    "template_id": "模板ID",  // 字符串或数字
    "constants": {},  // 子流程的常量覆盖
    "version": "版本号"  // 可选
  }
}
```

### 2.5 gateways 规范

#### 2.5.1 ParallelGateway（并行网关）

```json
{
  "node<gateway_id>": {
    "id": "node<gateway_id>",
    "type": "ParallelGateway",
    "name": "并行网关",
    "incoming": "line<flow_id>" | ["line<flow_id>", ...],
    "outgoing": ["line<flow_id>", ...]  // 必须是数组
  }
}
```

#### 2.5.2 ConvergeGateway（汇聚网关）

```json
{
  "node<gateway_id>": {
    "id": "node<gateway_id>",
    "type": "ConvergeGateway",
    "name": "汇聚网关",
    "incoming": ["line<flow_id>", ...],  // 必须是数组
    "outgoing": "line<flow_id>"  // 必须是单个字符串
  }
}
```

#### 2.5.3 ExclusiveGateway（分支网关）

```json
{
  "node<gateway_id>": {
    "id": "node<gateway_id>",
    "type": "ExclusiveGateway",
    "name": "分支网关",
    "incoming": "line<flow_id>" | ["line<flow_id>", ...],
    "outgoing": ["line<flow_id>", ...],
    "conditions": {
      "line<flow_id>": {
        "evaluate": "条件表达式"  // Python 表达式
      }
    }
  }
}
```

#### 2.5.4 ConditionalParallelGateway（条件并行网关）

```json
{
  "node<gateway_id>": {
    "id": "node<gateway_id>",
    "type": "ConditionalParallelGateway",
    "name": "条件并行网关",
    "incoming": "line<flow_id>" | ["line<flow_id>", ...],
    "outgoing": ["line<flow_id>", ...],
    "conditions": {
      "line<flow_id>": {
        "evaluate": "条件表达式"
      }
    }
  }
}
```

### 2.6 flows 规范

```json
{
  "line<flow_id>": {
    "id": "line<flow_id>",
    "source": "node<source_node_id>",
    "target": "node<target_node_id>",
    "is_default": false  // 可选，默认 false
  }
}
```

**要求**：
- `source` 和 `target` 必须指向存在的节点 ID
- 所有 flow 必须形成有向无环图（DAG）
- 每个节点的 `incoming` 和 `outgoing` 必须与 flows 中的连接一致

### 2.7 constants 规范

```json
{
  "${variable_key}": {
    "key": "${variable_key}",  // 必须与字典 key 一致
    "name": "变量名称",
    "index": 0,  // 显示顺序
    "desc": "变量描述",
    "source_type": "custom" | "component_inputs" | "component_outputs" | "system",
    "custom_type": "input" | "textarea" | "datetime" | "int" | "",  // source_type=custom 时有效
    "source_tag": "",  // source_type 为 component_inputs/outputs 时有效
    "source_info": {},  // 来源节点信息
    "value": "",  // 变量值
    "show_type": "show" | "hide",
    "validation": ""  // 正则表达式验证规则
  }
}
```

**要求**：
- Key 格式必须符合 `${key_name}` 规范
- `key` 字段值必须与字典 key 一致
- 禁止自引用和循环引用
- `source_type` 为 `custom` 时，`custom_type` 不能为空

### 2.8 outputs 规范

```json
[
  "${variable_key1}",
  "${variable_key2}"
]
```

**要求**：
- 数组中的每个元素必须是 `constants` 中存在的 key
- 格式必须符合 `${key_name}` 规范

## 三、验证机制

### 3.1 Schema 验证

项目使用 JSON Schema 进行结构验证，定义在：
- 后端：`pipeline_web/parser/schemas.py` - `WEB_PIPELINE_SCHEMA`
- 前端：`frontend/desktop/src/constants/pipelineTreeSchema.js` - `pipelineTreeSchema`

### 3.2 验证函数

#### 3.2.1 后端验证

```python
from pipeline_web.parser.validator import validate_web_pipeline_tree

try:
    validate_web_pipeline_tree(pipeline_tree)
    print("验证通过")
except exceptions.ParserWebTreeException as e:
    print(f"验证失败: {e}")
```

验证内容包括：
1. **Schema 验证**：使用 `Draft4Validator` 验证 JSON Schema
2. **Key 格式验证**：验证 constants 和 outputs 的 key 格式
3. **常量引用验证**：检查自引用和循环引用
4. **流程树验证**：验证 DAG 结构，检查节点连接一致性

#### 3.2.2 节点名称标准化

```python
from gcloud.utils.strings import standardize_pipeline_node_name

standardize_pipeline_node_name(pipeline_tree)
```

#### 3.2.3 流程绘制

```python
from pipeline_web.drawing_new.drawing import draw_pipeline

draw_pipeline(pipeline_tree)
```

此函数会：
- 自动计算节点的 `location`（位置信息）
- 生成 `line`（连线信息）
- 确保流程图的可视化布局

## 四、大模型 Prompt 设计

### 4.1 系统 Prompt 模板

```
你是一个专业的流程编排专家，负责根据用户需求生成符合 BK-SOPS 规范的 pipeline_tree JSON 结构。

## 核心规范

### 1. ID 命名规范
- 节点 ID: 必须以 `n` 开头，后跟小写字母和数字，格式：`^n[0-9a-z]+`
- 连线 ID: 必须以 `l` 开头，后跟小写字母和数字，格式：`^l[0-9a-z]+`
- 变量 Key: 格式为 `${key_name}`，不能以 `_env_` 或 `_system.` 开头

### 2. 必需字段
pipeline_tree 必须包含：start_event, end_event, activities, flows, gateways, constants, outputs

### 3. start_event 规范
- type: "EmptyStartEvent"（固定值）
- incoming: ""（空字符串）
- outgoing: 单个 flow ID（字符串）

### 4. end_event 规范
- type: "EmptyEndEvent"（固定值）
- incoming: flow ID（字符串或数组）
- outgoing: ""（空字符串）

### 5. activities 规范
- ServiceActivity: 必须包含 id, type, name, incoming, outgoing, component
- component.code: 有效的组件代码（如 "job_fast_execute_script", "sleep_timer", "pause_node"）
- component.data: 每个参数包含 hook（boolean）和 value（string）

### 6. flows 规范
- 必须形成有向无环图（DAG）
- source 和 target 必须指向存在的节点 ID
- 节点的 incoming/outgoing 必须与 flows 一致

### 7. constants 规范
- Key 格式：`${key_name}`
- key 字段值必须与字典 key 一致
- 禁止自引用和循环引用
- source_type: "custom" | "component_inputs" | "component_outputs" | "system"

### 8. 节点名称长度限制
- 活动节点名称：最大 50 字符
- 常量名称：最大 50 字符

## 生成要求

1. 生成完整的 pipeline_tree JSON，确保所有必需字段都存在
2. 确保所有 ID 符合命名规范
3. 确保节点连接关系正确，形成有效的 DAG
4. 确保 constants 中的变量引用正确，无自引用和循环引用
5. 节点名称长度不超过限制
6. 只输出 JSON，不要包含其他解释文字

## 示例结构

参考以下最小示例：

```json
{
  "start_event": {
    "id": "nodestart123",
    "name": "",
    "type": "EmptyStartEvent",
    "incoming": "",
    "outgoing": "lineflow123"
  },
  "end_event": {
    "id": "nodeend123",
    "name": "",
    "type": "EmptyEndEvent",
    "incoming": "lineflow456",
    "outgoing": ""
  },
  "activities": {
    "nodeact123": {
      "id": "nodeact123",
      "type": "ServiceActivity",
      "name": "执行脚本",
      "incoming": "lineflow123",
      "outgoing": "lineflow456",
      "optional": false,
      "component": {
        "code": "job_fast_execute_script",
        "data": {
          "script_content": {
            "hook": false,
            "value": "echo hello"
          }
        }
      },
      "error_ignorable": false,
      "retryable": true,
      "skippable": false
    }
  },
  "flows": {
    "lineflow123": {
      "id": "lineflow123",
      "source": "nodestart123",
      "target": "nodeact123",
      "is_default": false
    },
    "lineflow456": {
      "id": "lineflow456",
      "source": "nodeact123",
      "target": "nodeend123",
      "is_default": false
    }
  },
  "gateways": {},
  "constants": {},
  "outputs": []
}
```
```

### 4.2 用户 Prompt 模板

```
请根据以下需求生成 pipeline_tree：

需求描述：[用户的具体需求]

要求：
1. 流程包含以下步骤：[步骤1, 步骤2, ...]
2. 使用的组件：[组件列表]
3. 需要的全局变量：[变量列表]
4. 特殊要求：[并行执行、条件分支等]

请生成符合规范的 pipeline_tree JSON。
```

## 五、实施步骤

### 5.1 阶段一：规范梳理与文档化（已完成）

✅ **任务清单**：
- [x] 梳理 pipeline_tree 完整规范
- [x] 整理验证机制和函数
- [x] 收集示例数据
- [x] 编写规范文档

### 5.2 阶段二：Prompt 工程与测试

#### 5.2.1 开发 Prompt 模板
- [ ] 基于规范文档设计系统 Prompt
- [ ] 设计用户需求 Prompt 模板
- [ ] 准备测试用例集（简单、中等、复杂场景）

#### 5.2.2 测试与优化
- [ ] 使用测试用例验证 Prompt 效果
- [ ] 分析生成结果的错误模式
- [ ] 迭代优化 Prompt
- [ ] 建立错误分类和修复策略

### 5.3 阶段三：验证与修复机制

#### 5.3.1 实现验证包装器

```python
# 文件：gcloud/llm/pipeline_tree_validator.py

from pipeline_web.parser.validator import validate_web_pipeline_tree
from pipeline_web import exceptions
from gcloud.utils.strings import standardize_pipeline_node_name
from pipeline_web.drawing_new.drawing import draw_pipeline
import logging

logger = logging.getLogger("root")


class PipelineTreeValidator:
    """Pipeline Tree 验证和修复工具"""

    def __init__(self, pipeline_tree: dict):
        self.pipeline_tree = pipeline_tree
        self.errors = []
        self.warnings = []

    def validate(self) -> tuple[bool, list]:
        """
        验证 pipeline_tree

        Returns:
            (is_valid, errors): 是否有效和错误列表
        """
        # 1. 标准化节点名称
        try:
            standardize_pipeline_node_name(self.pipeline_tree)
        except Exception as e:
            self.errors.append(f"节点名称标准化失败: {e}")
            return False, self.errors

        # 2. Schema 和结构验证
        try:
            validate_web_pipeline_tree(self.pipeline_tree)
        except exceptions.ParserWebTreeException as e:
            self.errors.append(f"结构验证失败: {e}")
            return False, self.errors

        # 3. 绘制流程（验证布局）
        try:
            draw_pipeline(self.pipeline_tree)
        except Exception as e:
            self.warnings.append(f"流程绘制警告: {e}")
            # 绘制失败不影响验证，但记录警告

        return len(self.errors) == 0, self.errors

    def get_validation_report(self) -> dict:
        """获取验证报告"""
        is_valid, errors = self.validate()
        return {
            "valid": is_valid,
            "errors": errors,
            "warnings": self.warnings,
            "pipeline_tree": self.pipeline_tree if is_valid else None
        }
```

#### 5.3.2 实现自动修复机制

```python
# 文件：gcloud/llm/pipeline_tree_fixer.py

import re
import uuid
from typing import Dict, List, Set


class PipelineTreeFixer:
    """Pipeline Tree 自动修复工具"""

    NODE_ID_PATTERN = re.compile(r'^n[0-9a-z]+$')
    FLOW_ID_PATTERN = re.compile(r'^l[0-9a-z]+$')
    VAR_KEY_PATTERN = re.compile(r'^\$\{(?!_env_|_system\.)[a-zA-Z0-9_]+\}$')

    def __init__(self, pipeline_tree: dict):
        self.pipeline_tree = pipeline_tree
        self.fixes_applied = []

    def generate_node_id(self) -> str:
        """生成符合规范的节点 ID"""
        unique_part = uuid.uuid4().hex[:16]
        return f"node{unique_part}"

    def generate_flow_id(self) -> str:
        """生成符合规范的连线 ID"""
        unique_part = uuid.uuid4().hex[:16]
        return f"line{unique_part}"

    def fix_node_ids(self) -> Dict[str, str]:
        """修复节点 ID 格式"""
        id_mapping = {}

        # 检查并修复 start_event
        if 'start_event' in self.pipeline_tree:
            old_id = self.pipeline_tree['start_event'].get('id', '')
            if not self.NODE_ID_PATTERN.match(old_id):
                new_id = self.generate_node_id()
                id_mapping[old_id] = new_id
                self.pipeline_tree['start_event']['id'] = new_id
                self.fixes_applied.append(f"修复 start_event ID: {old_id} -> {new_id}")

        # 检查并修复 end_event
        if 'end_event' in self.pipeline_tree:
            old_id = self.pipeline_tree['end_event'].get('id', '')
            if not self.NODE_ID_PATTERN.match(old_id):
                new_id = self.generate_node_id()
                id_mapping[old_id] = new_id
                self.pipeline_tree['end_event']['id'] = new_id
                self.fixes_applied.append(f"修复 end_event ID: {old_id} -> {new_id}")

        # 检查并修复 activities
        if 'activities' in self.pipeline_tree:
            for act_id, activity in list(self.pipeline_tree['activities'].items()):
                if not self.NODE_ID_PATTERN.match(act_id):
                    new_id = self.generate_node_id()
                    id_mapping[act_id] = new_id
                    self.pipeline_tree['activities'][new_id] = activity
                    activity['id'] = new_id
                    del self.pipeline_tree['activities'][act_id]
                    self.fixes_applied.append(f"修复 activity ID: {act_id} -> {new_id}")

        # 检查并修复 gateways
        if 'gateways' in self.pipeline_tree:
            for gw_id, gateway in list(self.pipeline_tree['gateways'].items()):
                if not self.NODE_ID_PATTERN.match(gw_id):
                    new_id = self.generate_node_id()
                    id_mapping[gw_id] = new_id
                    self.pipeline_tree['gateways'][new_id] = gateway
                    gateway['id'] = new_id
                    del self.pipeline_tree['gateways'][gw_id]
                    self.fixes_applied.append(f"修复 gateway ID: {gw_id} -> {new_id}")

        return id_mapping

    def fix_flow_ids(self, node_id_mapping: Dict[str, str]) -> Dict[str, str]:
        """修复连线 ID 格式并更新节点引用"""
        flow_id_mapping = {}

        if 'flows' not in self.pipeline_tree:
            return flow_id_mapping

        # 修复 flow ID 格式
        for flow_id, flow in list(self.pipeline_tree['flows'].items()):
            if not self.FLOW_ID_PATTERN.match(flow_id):
                new_id = self.generate_flow_id()
                flow_id_mapping[flow_id] = new_id
                flow['id'] = new_id
                self.pipeline_tree['flows'][new_id] = flow
                del self.pipeline_tree['flows'][flow_id]
                self.fixes_applied.append(f"修复 flow ID: {flow_id} -> {new_id}")

        # 更新节点引用
        def update_reference(ref, mapping):
            if isinstance(ref, str):
                return mapping.get(ref, ref)
            elif isinstance(ref, list):
                return [mapping.get(r, r) for r in ref]
            return ref

        # 更新 flows 中的 source/target
        for flow in self.pipeline_tree['flows'].values():
            flow['source'] = update_reference(flow.get('source'), node_id_mapping)
            flow['target'] = update_reference(flow.get('target'), node_id_mapping)

        # 更新节点的 incoming/outgoing
        if 'start_event' in self.pipeline_tree:
            self.pipeline_tree['start_event']['outgoing'] = update_reference(
                self.pipeline_tree['start_event'].get('outgoing'), flow_id_mapping
            )

        if 'end_event' in self.pipeline_tree:
            self.pipeline_tree['end_event']['incoming'] = update_reference(
                self.pipeline_tree['end_event'].get('incoming'), flow_id_mapping
            )

        for activity in self.pipeline_tree.get('activities', {}).values():
            activity['incoming'] = update_reference(activity.get('incoming'), flow_id_mapping)
            activity['outgoing'] = update_reference(activity.get('outgoing'), flow_id_mapping)

        for gateway in self.pipeline_tree.get('gateways', {}).values():
            gateway['incoming'] = update_reference(gateway.get('incoming'), flow_id_mapping)
            gateway['outgoing'] = update_reference(gateway.get('outgoing'), flow_id_mapping)

        return flow_id_mapping

    def fix_constants_keys(self):
        """修复 constants 的 key 格式"""
        if 'constants' not in self.pipeline_tree:
            return

        constants = self.pipeline_tree['constants']
        new_constants = {}

        for key, value in constants.items():
            if not self.VAR_KEY_PATTERN.match(key):
                # 提取 key 名称
                key_name = key.replace('${', '').replace('}', '').strip('$')
                if not key_name:
                    key_name = f"var_{uuid.uuid4().hex[:8]}"
                new_key = f"${{{key_name}}}"
                new_constants[new_key] = value
                value['key'] = new_key
                self.fixes_applied.append(f"修复 constant key: {key} -> {new_key}")
            else:
                new_constants[key] = value

        self.pipeline_tree['constants'] = new_constants

    def fix_outputs_keys(self):
        """修复 outputs 的 key 格式"""
        if 'outputs' not in self.pipeline_tree:
            self.pipeline_tree['outputs'] = []
            return

        fixed_outputs = []
        for output_key in self.pipeline_tree['outputs']:
            if not self.VAR_KEY_PATTERN.match(output_key):
                key_name = output_key.replace('${', '').replace('}', '').strip('$')
                if not key_name:
                    continue  # 跳过无效的 key
                new_key = f"${{{key_name}}}"
                fixed_outputs.append(new_key)
                self.fixes_applied.append(f"修复 output key: {output_key} -> {new_key}")
            else:
                fixed_outputs.append(output_key)

        self.pipeline_tree['outputs'] = fixed_outputs

    def fix_all(self) -> dict:
        """执行所有修复"""
        # 1. 修复节点 ID
        node_id_mapping = self.fix_node_ids()

        # 2. 修复连线 ID 和引用
        flow_id_mapping = self.fix_flow_ids(node_id_mapping)

        # 3. 修复 constants keys
        self.fix_constants_keys()

        # 4. 修复 outputs keys
        self.fix_outputs_keys()

        return {
            "pipeline_tree": self.pipeline_tree,
            "fixes_applied": self.fixes_applied,
            "node_id_mapping": node_id_mapping,
            "flow_id_mapping": flow_id_mapping
        }
```

### 5.4 阶段四：集成与 API 开发

#### 5.4.1 创建 LLM Pipeline Tree 生成服务

```python
# 文件：gcloud/llm/pipeline_tree_generator.py

import json
import logging
from typing import Dict, Optional
from gcloud.llm.pipeline_tree_validator import PipelineTreeValidator
from gcloud.llm.pipeline_tree_fixer import PipelineTreeFixer

logger = logging.getLogger("root")


class LLMPipelineTreeGenerator:
    """基于大模型的 Pipeline Tree 生成器"""

    def __init__(self, llm_client):
        """
        Args:
            llm_client: 大模型客户端（如 OpenAI, Claude 等）
        """
        self.llm_client = llm_client
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """加载系统 Prompt"""
        # 从文件或配置加载系统 Prompt
        # 这里使用简化版本，实际应从配置文件加载
        return """
        你是一个专业的流程编排专家，负责根据用户需求生成符合 BK-SOPS 规范的 pipeline_tree JSON 结构。

        [系统 Prompt 内容，参考第四章节]
        """

    def generate(
        self,
        user_request: str,
        max_retries: int = 3,
        auto_fix: bool = True
    ) -> Dict:
        """
        生成 pipeline_tree

        Args:
            user_request: 用户需求描述
            max_retries: 最大重试次数
            auto_fix: 是否自动修复

        Returns:
            {
                "success": bool,
                "pipeline_tree": dict,
                "errors": list,
                "warnings": list,
                "fixes_applied": list
            }
        """
        for attempt in range(max_retries):
            try:
                # 1. 调用大模型生成
                response = self.llm_client.chat(
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_request}
                    ],
                    temperature=0.1  # 降低随机性，提高一致性
                )

                # 2. 解析 JSON
                pipeline_tree = self._parse_response(response)

                # 3. 自动修复（如果需要）
                if auto_fix:
                    fixer = PipelineTreeFixer(pipeline_tree)
                    fix_result = fixer.fix_all()
                    pipeline_tree = fix_result["pipeline_tree"]

                # 4. 验证
                validator = PipelineTreeValidator(pipeline_tree)
                is_valid, errors = validator.validate()

                if is_valid:
                    return {
                        "success": True,
                        "pipeline_tree": pipeline_tree,
                        "errors": [],
                        "warnings": validator.warnings,
                        "fixes_applied": fix_result.get("fixes_applied", []) if auto_fix else []
                    }
                else:
                    # 如果验证失败，尝试修复后再次验证
                    if attempt < max_retries - 1:
                        logger.warning(f"验证失败，尝试修复: {errors}")
                        continue
                    else:
                        return {
                            "success": False,
                            "pipeline_tree": None,
                            "errors": errors,
                            "warnings": validator.warnings,
                            "fixes_applied": []
                        }

            except json.JSONDecodeError as e:
                logger.error(f"JSON 解析失败: {e}")
                if attempt < max_retries - 1:
                    continue
                return {
                    "success": False,
                    "pipeline_tree": None,
                    "errors": [f"JSON 解析失败: {e}"],
                    "warnings": [],
                    "fixes_applied": []
                }

            except Exception as e:
                logger.error(f"生成失败: {e}")
                return {
                    "success": False,
                    "pipeline_tree": None,
                    "errors": [f"生成失败: {e}"],
                    "warnings": [],
                    "fixes_applied": []
                }

        return {
            "success": False,
            "pipeline_tree": None,
            "errors": ["达到最大重试次数"],
            "warnings": [],
            "fixes_applied": []
        }

    def _parse_response(self, response) -> dict:
        """解析大模型响应，提取 JSON"""
        content = response.get("content", "") if isinstance(response, dict) else str(response)

        # 尝试提取 JSON 代码块
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
        else:
            # 尝试提取第一个 { ... } 块
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)

        return json.loads(content)
```

#### 5.4.2 创建 API 接口

```python
# 文件：gcloud/llm/apis/django/api.py

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from gcloud.llm.pipeline_tree_generator import LLMPipelineTreeGenerator
from gcloud.llm.llm_client import get_llm_client
import json
import logging

logger = logging.getLogger("root")


@csrf_exempt
@require_POST
def generate_pipeline_tree(request):
    """
    生成 pipeline_tree API

    Request Body:
    {
        "user_request": "用户需求描述",
        "max_retries": 3,  // 可选
        "auto_fix": true   // 可选
    }

    Response:
    {
        "result": true,
        "data": {
            "success": true,
            "pipeline_tree": {...},
            "errors": [],
            "warnings": [],
            "fixes_applied": []
        }
    }
    """
    try:
        params = json.loads(request.body)
        user_request = params.get("user_request", "")

        if not user_request:
            return JsonResponse({
                "result": False,
                "message": "user_request 不能为空"
            })

        # 初始化生成器
        llm_client = get_llm_client()
        generator = LLMPipelineTreeGenerator(llm_client)

        # 生成 pipeline_tree
        result = generator.generate(
            user_request=user_request,
            max_retries=params.get("max_retries", 3),
            auto_fix=params.get("auto_fix", True)
        )

        return JsonResponse({
            "result": True,
            "data": result
        })

    except Exception as e:
        logger.exception("生成 pipeline_tree 失败")
        return JsonResponse({
            "result": False,
            "message": f"生成失败: {str(e)}"
        })
```

### 5.5 阶段五：测试与优化

#### 5.5.1 单元测试

```python
# 文件：gcloud/llm/tests/test_pipeline_tree_generator.py

from django.test import TestCase
from gcloud.llm.pipeline_tree_generator import LLMPipelineTreeGenerator
from gcloud.llm.pipeline_tree_validator import PipelineTreeValidator
from gcloud.llm.pipeline_tree_fixer import PipelineTreeFixer


class TestPipelineTreeGenerator(TestCase):
    """Pipeline Tree 生成器测试"""

    def test_simple_pipeline_generation(self):
        """测试简单流程生成"""
        # Mock LLM client
        mock_client = MockLLMClient()
        generator = LLMPipelineTreeGenerator(mock_client)

        result = generator.generate(
            user_request="创建一个执行脚本的简单流程"
        )

        self.assertTrue(result["success"])
        self.assertIsNotNone(result["pipeline_tree"])

        # 验证结构
        validator = PipelineTreeValidator(result["pipeline_tree"])
        is_valid, errors = validator.validate()
        self.assertTrue(is_valid, f"验证失败: {errors}")

    def test_complex_pipeline_generation(self):
        """测试复杂流程生成（包含网关、并行等）"""
        # 测试用例
        pass

    def test_auto_fix_mechanism(self):
        """测试自动修复机制"""
        # 创建一个有问题的 pipeline_tree
        invalid_tree = {
            "start_event": {
                "id": "invalid_id",  # 不符合规范
                "type": "EmptyStartEvent",
                "incoming": "",
                "outgoing": "flow1"
            },
            # ... 其他字段
        }

        fixer = PipelineTreeFixer(invalid_tree)
        result = fixer.fix_all()

        # 验证修复后的结构
        validator = PipelineTreeValidator(result["pipeline_tree"])
        is_valid, errors = validator.validate()
        self.assertTrue(is_valid)
```

#### 5.5.2 集成测试

- [ ] 测试不同复杂度场景
- [ ] 测试错误处理和重试机制
- [ ] 测试自动修复效果
- [ ] 性能测试

### 5.6 阶段六：监控与持续优化

#### 5.6.1 建立监控指标

- 生成成功率
- 验证通过率
- 自动修复成功率
- 常见错误类型统计
- 用户满意度

#### 5.6.2 建立反馈机制

- 收集用户反馈
- 分析错误模式
- 持续优化 Prompt
- 更新规范文档

## 六、最佳实践

### 6.1 Prompt 设计原则

1. **明确规范**：在 Prompt 中明确列出所有规范要求
2. **提供示例**：给出完整的、可运行的示例
3. **结构化输出**：要求模型只输出 JSON，不要额外解释
4. **分步生成**：对于复杂流程，可以分步生成

### 6.2 验证策略

1. **多层验证**：Schema 验证 → 结构验证 → 业务逻辑验证
2. **自动修复**：对于可修复的错误，自动修复后重新验证
3. **错误反馈**：将验证错误反馈给模型，进行迭代生成

### 6.3 错误处理

1. **分类错误**：将错误分为可修复和不可修复
2. **重试策略**：对于可修复错误，自动重试
3. **人工介入**：对于无法自动修复的错误，记录并通知人工处理

## 七、参考资源

### 7.1 代码文件

- `pipeline_web/parser/schemas.py` - Schema 定义
- `pipeline_web/parser/validator.py` - 验证函数
- `gcloud/utils/pipeline.py` - 常量验证
- `gcloud/utils/strings.py` - 名称标准化
- `pipeline_web/drawing_new/drawing.py` - 流程绘制

### 7.2 文档

- `docs/apidoc/en/fast_create_task.md` - API 文档
- `docs/apidoc/en/get_template_info.md` - 模板信息
- `frontend/desktop/src/constants/pipelineTreeSchema.js` - 前端 Schema

### 7.3 Context7 文档

- https://context7.com/tencentblueking/bk-sops
- https://context7.com/tencentblueking/bamboo-engine

## 八、实施时间表

| 阶段 | 任务 | 预计时间 | 负责人 |
|------|------|----------|--------|
| 阶段一 | 规范梳理与文档化 | 1-2 天 | - |
| 阶段二 | Prompt 工程与测试 | 3-5 天 | - |
| 阶段三 | 验证与修复机制 | 5-7 天 | - |
| 阶段四 | 集成与 API 开发 | 3-5 天 | - |
| 阶段五 | 测试与优化 | 5-7 天 | - |
| 阶段六 | 监控与持续优化 | 持续 | - |

**总计**：约 3-4 周（不含持续优化阶段）

## 九、风险与应对

### 9.1 风险识别

1. **大模型生成质量不稳定**
   - 应对：建立多层验证和自动修复机制
   - 应对：提供高质量示例和详细规范

2. **复杂流程生成困难**
   - 应对：分步生成，先简单后复杂
   - 应对：建立流程模板库

3. **性能问题**
   - 应对：缓存常用流程模板
   - 应对：异步生成机制

### 9.2 质量保证

1. **严格验证**：所有生成的 pipeline_tree 必须通过验证
2. **人工审核**：复杂流程建议人工审核
3. **持续监控**：建立监控和告警机制

## 十、总结

本指南提供了使用大模型构建 pipeline_tree 的完整实施步骤，包括：

1. ✅ 完整的规范文档
2. ✅ Prompt 设计模板
3. ✅ 验证和修复机制
4. ✅ 代码实现示例
5. ✅ 测试策略
6. ✅ 最佳实践

按照本指南实施，可以确保生成的 pipeline_tree 符合项目规范，并建立完善的验证和反馈机制。




