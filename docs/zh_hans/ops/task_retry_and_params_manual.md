# 任务节点重试与填参操作说明

本文档说明标准运维中**节点/子流程重试**、**重试时能否改参**、以及**「节点重试填参」开关**的配置方式，便于升级评估与运维落地。

---

## 1. 版本与行为变化（3.6.x → 3.28+）

- **约从 V3.28.0 起**（2022 年 10 月合入相关提交），重试时的交互做了产品级调整，提交说明为 **optimization**：重试时**仅围绕「输入参数」可重新填写**，其它配置不再在默认路径里开放重配。
- 该变化属于**产品设计**，**不是**偶然 Bug 回归。
- **默认（未开启节点重试填参）**：重试走 **「修改入参」侧栏（ModifyParams）**，仅能改**当前任务根流程**在 `pipeline_tree` 里展示的**全局变量**（`constants` 中 `show_type` 为展示等的变量）。适合「节点引用了任务全局变量」时通过改全局变量间接影响节点。
- **子流程节点**在默认路径下同样**只能改子流程对外暴露的全局变量**，**不能**在界面上直接改子流程**内部某个标准插件节点**上的常量（如作业节点脚本、目标 IP、执行用户等写在节点上的配置）。

---

## 2. 「节点重试填参」开关是什么

- 代码里通过 **`TaskConfig`** 表、**任务维度**记录是否启用；前端调用 **`GET /api/v3/taskflow/{task_id}/enable_fill_retry_params/`** 判断是否开启。
- **开源仓库的 `env.py` 中无同名环境变量**。若现场文档写「环境变量」，多为部署侧脚本或平台把配置写入 DB/配置中心的约定，**以实际环境为准**；从本仓库实现看，**权威开关是 `TaskConfig`（`enable_fill_retry_params`）**。

### 2.1 开启后的前端行为（普通节点）

- 开启后重试走 **`RetryNode`**：加载当前失败节点的**插件表单**，可改的是该节点在模板中的**插件入参**。
- **`loadNodeInfo` 逻辑**（V2、非子流程）：
  - 入参在模板上**接了全局变量**（`hook === true`）：表单用接口返回的**当前实际入参值**展示/编辑。
  - 入参为**节点常量**（`hook === false`）：表单用模板里的 **`value`** 展示/编辑。
- 因此：**既包含「接变量的参数」，也包含「节点常量」**，**不是**「只能改接成全局变量的那几项」。表单项需与 `nodeInfo.data.inputs` 及节点 `componentData` 能对应上。

### 2.2 子流程节点（`subprocess_plugin`）

- 开启填参后，子流程仍按 **`RetryNode` + `getSubflowInputsConfig`** 处理：仅根据**子流程模板 pipeline 的 `constants`** 生成表单，即**子流程级全局变量**。
- **不包含**子流程画布内**其它内部节点**的插件常量/变量配置。若需改内部节点参数，需产品扩展（例如与旧版能力对齐的需求）。

---

## 3. 引擎与子流程重试（补充）

- **引擎 V1**：子流程重试在调度层会直接返回不支持（需升级到 **V2 引擎** 等）。这与「重试时能否改哪些参数」是不同维度的问题。

---

## 4. 如何配置「节点重试填参」

### 4.1 数据模型（`taskflow3_taskconfig`）

启用时需存在一条 **`TaskConfig`** 记录，且 **`enable_fill_retry_params()` 仅识别任务级配置**（代码注释：**仅识别任务级别配置**）。

| 字段 | 说明 | 启用时的取值 |
|------|------|----------------|
| `scope` | 配置范围 | **`3`**（`SCOPE_TYPE_TASK`，任务） |
| `scope_id` | 范围对象 ID | **任务实例 ID**（`TaskFlowInstance` 主键） |
| `config_type` | 配置类型 | **`2`**（`CONFIG_TYPE_RETRY_PARAMS`） |
| `config_value` | 配置值 | **`enable_fill_retry_params`**（字符串，与模型 choices 一致） |

关闭：删除该条记录，或将 `config_value` 设为 **`disable_fill_retry_params`**（当前判断逻辑以「存在且为 enable」为准，以线上代码为准）。

### 4.2 配置入口

1. **Django Admin**：`TaskConfig` 已在 `gcloud/taskflow3/admin.py` 注册，在后台 **「任务配置 TaskConfig」** 中新增/维护。
2. **脚本 / `manage.py shell`**：按上表对**指定任务 ID** 插入或 `get_or_create`。

示例（仅供参考，执行前请确认环境与 ID）：

```python
from gcloud.taskflow3.models import TaskConfig

TaskConfig.objects.get_or_create(
    scope=TaskConfig.SCOPE_TYPE_TASK,
    scope_id=<任务实例ID>,
    config_type=TaskConfig.CONFIG_TYPE_RETRY_PARAMS,
    defaults={"config_value": TaskConfig.ENABLE_FILL_RETRY_PARAMS},
)
```

本仓库**未提供**对外业务 API 用于写入该配置，需 Admin、运维脚本或二次开发接口。

### 4.3 能否按「业务 / 项目」一键全开

- **当前实现：不能。** `enable_fill_retry_params(task_id)` **只查询** `scope=任务` 且 `scope_id=任务ID`，**不会**读取 `scope=项目` 或 `scope=模板`（与「独立子流程」等项目/模板级策略不同）。
- 若要对某项目下**所有任务**默认开启，只能：
  - 对每个任务写入一条任务级 `TaskConfig`；或
  - 在**创建任务**流程中自动写入；或
  - **修改产品代码**：扩展为支持项目/模板维度回退查询（需需求评审与权限设计）。

---

## 5. 相关代码位置（便于二次开发或核对）

| 说明 | 路径 |
|------|------|
| 是否开启节点重试填参 | `gcloud/taskflow3/models.py` → `TaskConfigManager.enable_fill_retry_params` |
| 查询接口 | `gcloud/core/apis/drf/viewsets/taskflow.py` → `enable_fill_retry_params` |
| 重试入口分支 | `frontend/desktop/src/pages/task/TaskExecute/TaskOperation.vue` → `onRetryClick` |
| 插件表单重试 | `frontend/desktop/src/pages/task/TaskExecute/RetryNode.vue` |
| 仅改任务全局变量 | `frontend/desktop/src/pages/task/TaskExecute/ModifyParams.vue` |

---

## 6. 与升级说明文档的关系

若某次版本升级涉及引擎默认版本、重试行为等，可在 **`docs/ops/version_update_notes.md`** 中增加对应版本条目，并引用本文档。
