# 创建任务时复用上次执行参数

## 概述

在标准运维创建任务的填参步骤中，增加"使用上一次参数"功能，让用户可以一键导入同模板上次执行的参数值，减少重复填写。

## 需求范围

- **第一版**：仅支持"使用上一次参数"，即取同一模板在当前项目下最近一次执行的参数
- **后续扩展**：支持用户从最近 N 次执行中选择某一次的参数
- **模板范围**：仅限同一模板（project template 或 common template），不支持跨模板复用

## 设计方案

采用"preview_task_tree 视图层附带检查 + 新增轻量 API 获取参数"方案。

### 选型理由

| 维度 | 说明 |
|------|------|
| 检查开销 | 附带在已有的 preview_task_tree 请求中，零额外请求 |
| 数据精简 | 专用 API 只返回 constants，不返回完整 pipeline_tree |
| 扩展性 | 后续支持"选择历史参数"只需在同一 API 上加 limit 参数和列表返回，无需架构调整 |

---

## 后端设计

### 1. 在 preview_task_tree 视图层附带 `last_execution_id`

**文件**：`gcloud/taskflow3/apis/django/api.py`（`preview_task_tree` 视图函数）

**注意**：`last_execution_id` 的查询在**视图层**（`preview_task_tree` 视图函数）中进行，而非 `pipeline_web/preview.py` 的 `preview_template_tree` 函数。`preview_template_tree` 是纯粹的 pipeline 树变换工具函数，不应引入 `TaskFlowInstance` 依赖，避免 `pipeline_web` → `gcloud.taskflow3` 的循环依赖。

在 `preview_task_tree` 视图函数调用 `preview_template_tree` 获得 `data` 后，追加查询：

```python
data = preview_template_tree(project_id, template_source, template_id, version, exclude_task_nodes_id)

last_task = TaskFlowInstance.objects.filter(
    project_id=project_id,
    template_id=template_id,
    template_source=template_source,
    is_deleted=False,
    is_child_taskflow=False,
    pipeline_instance__is_started=True,
    pipeline_instance__isnull=False,
).order_by("-id").only("id").first()

data["last_execution_id"] = last_task.id if last_task else None
```

同样的逻辑需要在 `preview_task_tree_with_schemes`（DRF 视图）中添加，确保使用 scheme 方式预览时也能返回 `last_execution_id`。

返回值扩展为：

```python
{
    "pipeline_tree": {...},
    "constants_not_referred": {...},
    "last_execution_id": 123  // TaskFlowInstance.id，无记录时为 null
}
```

前端据 `last_execution_id` 是否为 `null` 决定是否显示"使用上一次参数"按钮。

### 2. 新增 API：获取上次执行的 constants

**路径**：`GET /taskflow/api/last_execution_constants/<project_id>/`

**权限控制**：与 `preview_task_tree` 保持一致，不单独添加 `@iam_intercept`，权限由上层页面入口（任务创建页面）统一控制。

**请求参数**（query string）：

| 参数 | 必填 | 说明 |
|------|------|------|
| `template_id` | 是 | 模板 ID（CharField，以字符串形式匹配） |
| `template_source` | 否 | 默认 `project`，可选 `common` |

**处理逻辑**：

1. 根据 `project_id` + `template_id`（字符串匹配）+ `template_source` + `is_deleted=False` + `is_child_taskflow=False` + `pipeline_instance__is_started=True` + `pipeline_instance__isnull=False` 查询 `TaskFlowInstance`，按 `-id` 排序取第一条
2. 若无记录，返回 `{"result": false, "message": "没有历史执行记录"}`
3. 校验 `pipeline_instance` 不为 `None`（虽然查询已过滤，增加防御性检查）
4. 从 `pipeline_instance.execution_data` 中提取 `constants`
5. 只返回 `show_type == "show"` 的变量（隐藏变量无需返回）
6. 精简返回字段：每个 constant 只保留 `key`、`name`、`value`、`custom_type`、`source_type`（因为只返回 `show_type=show` 的变量，`show_type` 字段冗余不再包含）

**返回值**：

```python
{
    "result": true,
    "data": {
        "task_id": 123,
        "task_name": "任务名称",
        "executor": "admin",
        "create_time": "2026-03-20 10:30:00",
        "constants": {
            "${ip}": {"key": "${ip}", "name": "目标IP", "value": "10.0.0.1", "custom_type": "input", "source_type": "component_inputs"},
            "${biz_id}": {"key": "${biz_id}", "name": "业务ID", "value": 2, "custom_type": "input", "source_type": "custom"}
        }
    }
}
```

附带 `task_name`、`executor`、`create_time` 用于前端在提示中告知用户参数来源。

**代码位置**：
- 视图：`gcloud/taskflow3/apis/django/api.py`
- URL：`gcloud/taskflow3/urls.py`

### 3. "上一次执行"的查询定义

```python
TaskFlowInstance.objects.filter(
    project_id=project_id,
    template_id=template_id,          # CharField，字符串匹配
    template_source=template_source,   # 排除 onetime 类型（onetime 的 template_id 无效）
    is_deleted=False,
    is_child_taskflow=False,           # 排除子任务，其 constants 是子流程级别的
    pipeline_instance__is_started=True,# 只取已实际执行过的任务
    pipeline_instance__isnull=False,   # 排除 pipeline_instance 为空的记录
).order_by("-id").first()
```

不区分创建人，取当前项目下全局最新的一次。

`template_source` 参数由前端传入（`project` 或 `common`），因此不会匹配到 `onetime` 类型。

---

## 前端交互设计

### 1. 按钮展示

- **位置**：`TaskParamFill.vue` 的"参数信息"栏目标题右侧
- **显示条件**：`preview_task_tree` 返回的 `last_execution_id` 不为 `null` 时渲染；为 `null` 则不显示
- **样式**：MagicBox 文字型按钮（text 类型），与标题平级但视觉上不抢占主操作

### 2. 点击交互流程

1. 用户点击"使用上一次参数"
2. 弹出二次确认对话框："将使用上次执行（{执行人} 于 {时间} 创建的「{任务名}」）的参数覆盖当前表单，是否继续？"
3. 用户确认后，调用 `GET /taskflow/api/last_execution_constants/<project_id>/`
4. 拿到 constants 后，逐个与当前表单的 constants 进行 key 匹配和值填充

### 3. 参数匹配规则

匹配逻辑应参考现有的 `TaskParamEdit.vue` 中通过 `reuseTaskId` 复用参数的实现，保持行为一致。

| 场景 | 处理方式 | 是否记录 |
|------|---------|---------|
| key 匹配且 `custom_type` 一致 | 用历史值覆盖当前值 | 不记录 |
| key 匹配但 `custom_type` 不同 | 跳过，不覆盖 | 记录为"未匹配" |
| 当前有但历史没有 | 保持默认值 | 记录为"未匹配" |
| 历史有但当前没有 | 忽略 | 不记录 |

### 4. 覆盖后提示

使用 MagicBox 的 `$bkMessage` 或 `$bkNotify`：

- **全部匹配成功**："已成功导入 N 个参数"
- **部分未匹配**："已成功导入 N 个参数，以下 M 个参数未能匹配，请手动填写：参数A、参数B、参数C"

参数名使用变量的 `name`（中文名）而非 `key`。

### 5. 涉及的改造文件

| 文件 | 改造内容 |
|------|---------|
| `TaskParamFill.vue` | 接收 `last_execution_id`，渲染按钮，处理点击和提示 |
| `task.js`（Vuex store） | 新增 action 调用获取上次执行 constants 的接口 |
| `TaskParamEdit.vue` | 暴露方法供父组件批量设置 constants 的值 |

---

## 错误处理与边界情况

### 接口请求失败

调用 `last_execution_constants` 接口失败时，按钮恢复可点击状态，提示用户"获取历史参数失败，请重试"。

### 并发竞态

1. **历史任务被删除**：用户看到按钮后点击前，历史任务被删除。此时接口返回无记录，前端提示"历史执行记录已不存在"并隐藏按钮。
2. **有更新的任务产生**：`preview_task_tree` 返回 `last_execution_id=123`，但点击按钮时已有新任务 `id=456`。`last_execution_constants` 接口实时查询，会返回最新的 `id=456` 的参数。这是可接受的行为——用户获得的始终是最新一次执行的参数。

### 重复点击

用户已点过一次后再次点击，按同样逻辑覆盖，二次确认对话框提供防误操作保护。

### 公共流程（common template）

`template_source` 为 `common` 时，查询使用 `template_source="common"` + `template_id`，仍限定在当前 `project_id` 下。

### 子流程参数

子流程节点的参数属于 `constants` 的一部分，按相同 key 匹配逻辑处理，无需特殊对待。子任务（`is_child_taskflow=True`）已在查询中排除。

### pipeline_instance 为空

`TaskFlowInstance.pipeline_instance` 是 `null=True, on_delete=SET_NULL` 的外键。查询中已通过 `pipeline_instance__isnull=False` 过滤，视图代码中仍增加防御性空检查。

---

## 后续扩展方向

当需要支持"从最近 N 次执行中选择"时：

1. `preview_task_tree` 视图层返回 `execution_history_count` 替代 `last_execution_id`，前端据此决定展示"使用上一次参数"还是扩展为"从历史中选择"
2. 新增 API 加 `?limit=10` 参数，返回最近 10 次执行的摘要列表（task_id、task_name、executor、create_time）
3. 用户选中某次后，按 task_id 获取具体 constants
4. 参数匹配和提示逻辑复用第一版实现
