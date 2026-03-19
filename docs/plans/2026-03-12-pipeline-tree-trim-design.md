# pipeline_tree MCP 响应裁剪 — 设计文档

> 日期：2026-03-12
> TAPD：--story=132544238
> 参考方案：`bk-sops-skills/docs/plans/pipeline-tree-trim-implementation.md`

---

## 1. 问题

当前 MCP Server 对返回 `pipeline_tree` 的接口完全移除该字段，导致 6 个 Skill 无法获取流程结构信息。

## 2. 方案

**MCP 请求默认仍不返回 `pipeline_tree`（向后兼容），需要的 Skill 通过 `include_pipeline_tree=true` 参数显式请求裁剪后的版本。** 裁剪逻辑移除前端渲染、画布布局、冗余元数据，保留 Skill 所需的全部语义信息。压缩率约 59%（28K → 11.7K tokens）。

### 2.1 行为矩阵

| 场景 | pipeline_tree 行为 |
|------|-------------------|
| MCP 请求，未传 `include_pipeline_tree` | **移除**（与现在一致，向后兼容） |
| MCP 请求，`include_pipeline_tree=true` | **返回裁剪后版本** |
| 非 MCP 请求 | **返回完整版本**（不变） |

## 3. 已确认的设计决策

| 决策 | 结论 | 说明 |
|------|------|------|
| 集成方式 | 修改 `@mcp_apigw` 装饰器 | 新增 `trim_responses` 参数，声明式配置 |
| 默认行为 | MCP 请求默认仍不返回 pipeline_tree | 向后兼容，避免存量用户 token 消耗增加 |
| opt-in 参数 | `include_pipeline_tree=true` | query 参数，仅 MCP 请求有效 |
| `get_template_info` | 支持 opt-in | `trim_responses={"pipeline_tree": trim_pipeline_tree}` |
| `get_task_detail` | 支持 opt-in | `task_webhook_history` 继续无条件移除 |
| `get_common_template_info` | 支持 opt-in | `template_constants` 继续无条件移除 |
| `create_task` | 不变 | 继续完全移除 pipeline_tree（创建响应中是冗余信息） |
| `get_task_node_detail` | `histories` 限制最近 3 条 | 视图内部处理，支持 `max_histories` 参数 |
| `shorten_ids` | 暂不启用 | 59% 压缩率已足够，避免 Skill 维护 id_map 的复杂度 |

## 4. 装饰器 trim_responses 语义

`trim_responses` 的含义：**该字段默认移除，可通过 `include_{field}=true` 参数显式请求裁剪后的版本**。

```python
@mcp_apigw(trim_responses={"pipeline_tree": trim_pipeline_tree})
```

装饰器内部逻辑：
1. 遍历 `trim_responses` 中的字段
2. 检查请求参数 `include_{field}` 是否为 `true`
3. 如果是 → 调用 trimmer 函数裁剪后保留
4. 如果否 → 从 `data` 中移除该字段（等同于 exclude）

## 5. 修改范围

### 5.1 新增文件

- `gcloud/apigw/pipeline_tree_trimmer.py` — 裁剪纯函数模块

### 5.2 修改文件

| 文件 | 变更 |
|------|------|
| `gcloud/apigw/decorators.py` | `mcp_apigw` 新增 `trim_responses` 参数 |
| `gcloud/apigw/views/get_template_info.py` | 装饰器参数从 exclude 改为 trim |
| `gcloud/apigw/views/get_task_detail.py` | 装饰器参数拆分为 trim + exclude |
| `gcloud/apigw/views/get_common_template_info.py` | 装饰器参数拆分为 trim + exclude |
| `gcloud/apigw/views/get_task_node_detail.py` | 移除 exclude_responses，视图内限制 histories |
| `docs/design/mcp-response-field-exclusions.md` | 更新裁剪策略文档 |
| `apigw/bk_apigw_resources_bk-sops_mcp_supplement.yaml` | 为 3 个接口补充 `include_pipeline_tree` 参数 |

### 5.3 新增测试

- `gcloud/tests/apigw/test_pipeline_tree_trimmer.py` — 裁剪函数单元测试

## 6. 裁剪规则摘要

详细规则见参考方案文档 §3。核心策略：

- **Activities**：白名单保留（id, type, name, component, pipeline, stage_name, retryable, skippable, error_ignorable, auto_retry, source_info）
- **Component.data**：hook 解包 + 空值移除 + 黑名单字段移除
- **Gateways**：白名单保留（id, type, name, conditions, default_condition, converge_gateway_id）
- **Flows**：仅保留 source, target, is_default
- **Events**：仅保留 id, type, name
- **Constants**：白名单保留 + 空值过滤
- **顶层移除**：`line`、`location`
