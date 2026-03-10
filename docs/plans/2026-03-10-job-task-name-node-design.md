# Job 插件任务名「节点名称+时间戳」设计

## 背景

标准运维创建作业平台（JOB）任务时，多数插件不传 `task_name`，作业平台自动生成（如 `API Quick execution script` + 时间戳），导致在作业平台侧难以与 SOPS 流程节点对应。

## 目标

为 6 个核心 Job 插件新增小版本，默认使用「节点名称 + 时间戳」作为 job 任务名，便于在作业平台中识别来源节点。

## 需求结论

| 决策点 | 结论 |
|--------|------|
| 任务名策略 | 默认使用「节点名称 + 时间戳」，无需用户选择 |
| 时间戳格式 | 与旧默认一致：毫秒级数字（如 `1521100521303`） |
| 节点名处理 | 做 sanitize（去除非法字符、截断超长） |
| 节点名缺失 | 不传 task_name，交由作业平台自动生成 |
| 改造范围 | 3 个核心插件（快速执行脚本、快速分发文件、执行作业） |

## 方案：公共工具 + 各插件内联调用

### 1. 工具函数

**位置**：`pipeline_plugins/components/utils/sites/open/utils.py`

**签名**：
```python
def get_job_task_name(root_pipeline_id: str, node_id: str) -> str | None:
    """
    生成 job 任务名：节点名称_sanitize + 毫秒时间戳。
    若无法获取节点名则返回 None（调用方不传 task_name，由作业平台自动生成）。
    """
```

**实现逻辑**：
1. 通过 `root_pipeline_id` 查询 `PipelineInstance` 的 `execution_data`（pipeline tree）
2. 在 `activities` 中递归查找 `node_id`（支持子流程），取 `activities[node_id]["name"]`
3. Sanitize：沿用 `standardize_name` 思路，去除 `<>$&'"` 等非法字符，节点名部分截断至 50 字符
4. 拼接：`sanitized_name + str(int(time.time() * 1000))`
5. 节点名为空或获取失败时返回 `None`

**依赖**：`PipelineInstance`（pipeline.models）、`pipeline.core.constants.PE`

### 2. 插件改造

| 插件 | 新版本文件 | 基于 | 使用表单 |
|------|------------|------|----------|
| 快速执行脚本 | fast_execute_script/v2_1.py | v2_0 | v2_0.js |
| 快速分发文件 | fast_push_file/v3_1.py | v3_0 | v3_0.js |
| 执行作业 | execute_task/v2_1.py | v2_0 | v2_0.js |

**改造方式**：在构造 `job_kwargs` 时增加：
```python
task_name = get_job_task_name(self.root_pipeline_id, self.id)
if task_name:
    job_kwargs["task_name"] = task_name
```

**特殊处理**：`fast_push_file` 使用 `batch_execute_func` 多次调用，每次调用生成新的 `task_name`（时间戳不同），保证唯一性。

### 3. 数据流

```
插件 plugin_execute
    │
    ├─► get_job_task_name(root_pipeline_id, node_id)
    │       │
    │       ├─► PipelineInstance.objects.get(instance_id=root_pipeline_id)
    │       ├─► 从 execution_data 递归查找 activities[node_id]["name"]
    │       ├─► standardize_name 做 sanitize
    │       └─► 返回 "节点名_毫秒时间戳" 或 None
    │
    ├─► if task_name: job_kwargs["task_name"] = task_name
    │
    └─► client.jobv3.xxx(job_kwargs)
```

### 4. 异常处理

| 场景 | 处理方式 |
|------|----------|
| PipelineInstance 不存在 | 返回 None |
| 节点在子流程中 | 递归遍历 SubProcess 的 pipeline 查找 |
| 节点名称为空 | 返回 None |
| standardize_name 后为空 | 返回 None |
| 工具函数内部异常 | try-except 捕获，返回 None |

### 5. 测试

- **get_job_task_name 单元测试**：正常节点、子流程节点、节点名为空、PipelineInstance 不存在、sanitize 等
- **插件集成测试**：mock `get_job_task_name`，验证 `job_kwargs` 包含正确 `task_name`
