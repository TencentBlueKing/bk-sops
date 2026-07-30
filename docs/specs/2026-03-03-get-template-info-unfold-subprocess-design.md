# Design: get_template_info 新增 unfold_subprocess 参数

**日期**：2026-03-03  
**状态**：已批准，待实现

---

## 背景与目标

`get_template_info` 网关接口返回的 `pipeline_tree` 中，SubProcess（子流程）节点只包含 `template_id` 和 `constants` 参数映射，不包含子流程的完整结构。

AI Agent 在通过 skill 分析流程完整结构时，需要递归多次调用接口才能拿到全貌。本次新增 `unfold_subprocess` 参数，允许一次调用返回完整的、递归展开的流程树，降低调用复杂度。

**调用链**：AI Agent → SOPS Skill → API Gateway → `get_template_info`

---

## 决策记录

| 决策点 | 结论 |
|---|---|
| 主要使用方 | 外部 API 调用（非 MCP 链路），`mcp_apigw` 排除逻辑不受影响 |
| 递归深度控制 | 复用全局配置 `TEMPLATE_MAX_RECURSIVE_NUMBER`（默认 200），不新增深度参数 |
| 实现方案 | 方案 A：在原始数据层调用现有 `PipelineTemplateWebWrapper.unfold_subprocess`，后接递归 ID 转换 |
| 默认值 | `false`，存量调用行为完全不变 |

---

## 接口变更

### 新增查询参数

| 字段 | 类型 | 必选 | 默认值 | 描述 |
|---|---|---|---|---|
| `unfold_subprocess` | bool | 否 | `false` | 是否展开 `pipeline_tree` 中所有子流程的完整配置 |

### 请求示例

```
GET /get_template_info/{template_id}/{bk_biz_id}/?unfold_subprocess=true
```

### 响应结构变化

`unfold_subprocess=true` 时，`pipeline_tree.activities` 中每个 `type=SubProcess` 的节点，新增 `pipeline` 字段，内容为该子流程完整的 `pipeline_tree` 结构，并递归展开其内部子流程：

```json
{
  "result": true,
  "data": {
    "pipeline_tree": {
      "activities": {
        "node_abc": {
          "type": "SubProcess",
          "template_id": "123",
          "name": "子流程节点名",
          "pipeline": {
            "start_event": {},
            "end_event": {},
            "activities": {
              "node_xyz": {
                "type": "SubProcess",
                "pipeline": {}
              }
            },
            "gateways": {},
            "flows": {},
            "constants": {}
          }
        }
      }
    }
  }
}
```

`unfold_subprocess=false`（默认）时，接口行为与现有完全一致，SubProcess 节点无 `pipeline` 字段。

---

## 核心实现逻辑

### 数据流对比

**现有路径**（`unfold_subprocess=false`）：

```
template.pipeline_tree
  → 内部已做 replace_template_id(reverse=True)，SubProcess.template_id 为用户可见 pk
  → pop line/location
  → varschema.add_schema_for_input_vars
  → 返回
```

**新路径**（`unfold_subprocess=true`）：

```
deepcopy(template.pipeline_template.data)
  （原始数据，SubProcess.template_id 为内部 pipeline_template UUID）
  → PipelineWebTreeCleaner.clean()          # 清洗顶层 web 数据
  → PipelineTemplateWebWrapper.unfold_subprocess(tree, template.__class__)
      （递归展开，写入 act["pipeline"]；展开后各层均为内部 UUID）
  → 递归 replace_template_id(reverse=True)  # 全树递归：内部 UUID → 用户可见 pk
  → pop line/location（顶层）
  → varschema.add_schema_for_input_vars（顶层）
  → 返回
```

### 关键新增：递归 ID 转换函数

现有 `replace_template_id` 只处理顶层 `activities`，展开后子流程数据位于 `act["pipeline"]`，需要新增递归版本：

```python
def replace_template_id_recursive(template_model, pipeline_data, reverse=False):
    """对整棵 pipeline_tree（含所有层级的 act["pipeline"]）递归执行 ID 转换"""
    replace_template_id(template_model, pipeline_data, reverse=reverse)
    for act in pipeline_data.get("activities", {}).values():
        if act.get("type") == "SubProcess" and "pipeline" in act:
            subprocess_template_model = (
                CommonTemplate if act.get("template_source") == "common" else template_model
            )
            replace_template_id_recursive(subprocess_template_model, act["pipeline"], reverse=reverse)
```

### 错误处理

| 场景 | 处理方式 |
|---|---|
| 子流程模板不存在 | `unfold_subprocess` 内部抛异常，视图层捕获，返回 `result=false` + 错误信息 |
| 递归层数超限 | `unfold_subprocess` 内部抛 `PipelineException`，视图层捕获，返回 `result=false` + 错误信息 |

---

## 改动文件清单

| 文件 | 改动内容 |
|---|---|
| `gcloud/apigw/serializers.py` | `IncludeTemplateSerializer` 新增 `unfold_subprocess` 字段 |
| `gcloud/apigw/views/get_template_info.py` | 读取 `unfold_subprocess` 参数，传入 `format_template_data`；新增异常捕获 |
| `gcloud/apigw/views/utils.py` | `format_template_data` 新增 `unfold_subprocess` 分支；新增 `replace_template_id_recursive` 辅助函数 |
| `docs/apidoc/zh_hans/get_template_info.md` | 更新查询参数表和响应字段说明 |
| `.cursor/skills/references/get_template_info.md` | 更新 skill 参考文档，说明新参数用法 |

---

## 不在本次范围内

- `get_common_template_info` 接口暂不同步支持（如有需要单独评估）
- MCP 调用链路下的 `pipeline_tree` 暴露策略不变
- 不新增深度限制参数，调用方通过控制模板层级复杂度自行管控
