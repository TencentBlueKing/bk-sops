# Pipeline Tree 生成快速参考

## 核心规范速查

### ID 命名规范
- **节点 ID**: `^n[0-9a-z]+` (如: `node76393dcfedcf73dbc726f1c4786d`)
- **连线 ID**: `^l[0-9a-z]+` (如: `line490caa49d2a03e64829693281032`)
- **变量 Key**: `^\$\{(?!_env_|_system\.)[a-zA-Z0-9_]+\}$` (如: `${script_timeout}`)

### 必需字段
```python
{
    "start_event": {...},      # 必需
    "end_event": {...},         # 必需
    "activities": {...},        # 必需
    "flows": {...},             # 必需
    "gateways": {...},          # 必需（可为空）
    "constants": {...},         # 必需（可为空）
    "outputs": []                # 必需（可为空）
}
```

### 节点类型
- `start_event.type`: `"EmptyStartEvent"` (固定)
- `end_event.type`: `"EmptyEndEvent"` (固定)
- `activities[].type`: `"ServiceActivity"` 或 `"SubProcess"`
- `gateways[].type`: `"ParallelGateway"`, `"ConvergeGateway"`, `"ExclusiveGateway"`, `"ConditionalParallelGateway"`

### 验证函数
```python
from pipeline_web.parser.validator import validate_web_pipeline_tree
from gcloud.utils.strings import standardize_pipeline_node_name
from pipeline_web.drawing_new.drawing import draw_pipeline

# 1. 标准化名称
standardize_pipeline_node_name(pipeline_tree)

# 2. 验证结构
validate_web_pipeline_tree(pipeline_tree)

# 3. 绘制流程（生成 location 和 line）
draw_pipeline(pipeline_tree)
```

## 最小示例

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
    "incoming": "lineflow123",
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

## 常见错误与修复

### 错误 1: ID 格式不正确
- **问题**: 节点 ID 不以 `n` 开头，连线 ID 不以 `l` 开头
- **修复**: 使用 `PipelineTreeFixer.fix_node_ids()` 和 `fix_flow_ids()`

### 错误 2: 节点连接不一致
- **问题**: `incoming`/`outgoing` 与 `flows` 中的连接不匹配
- **修复**: 检查并同步更新所有引用

### 错误 3: 常量自引用或循环引用
- **问题**: `constants` 中存在自引用或循环引用
- **修复**: 使用 `validate_pipeline_tree_constants()` 检测并修复

### 错误 4: 节点名称过长
- **问题**: 节点名称超过 50 字符
- **修复**: 使用 `standardize_pipeline_node_name()` 自动截断

## 实施步骤概览

1. **规范梳理** ✅ (已完成)
2. **Prompt 设计** - 基于规范设计系统 Prompt
3. **验证机制** - 实现多层验证和自动修复
4. **API 开发** - 创建生成接口
5. **测试优化** - 单元测试和集成测试
6. **监控反馈** - 建立监控和持续优化机制

详细步骤请参考: `docs/llm_pipeline_tree_implementation_guide.md`




