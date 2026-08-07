# 标准运维操作审计一期补漏设计

## 背景

标准运维在 2024 年接入蓝鲸审计中心后，主要在页面侧项目、流程、任务、轻应用、周期任务等主路径中手工调用 `bk_audit_add_event`。随着 API Server、计划任务、任务参数修改、Webhook 等能力演进，现有审计出现三类缺口：

1. 同一业务操作在页面入口有审计，API Server 入口没有审计。
2. 首版已经定义了资源和动作，但部分入口从未调用审计上报。
3. 部分旧调用在业务完成前上报，或者没有判断业务返回结果，可能产生误报。

当前 `BK_AUDIT_DATA_TOKEN` 为空时，`ENABLE_BK_AUDIT` 为 `False`，所有审计调用直接返回。API Server 在 Token 未配置的状态下不会向审计中心发送事件。

## 一期目标

一期在不新增审计动作、不新增审计资源的前提下，完成以下目标：

- 复用现有项目、流程、任务、公共流程、轻应用、周期任务、计划任务资源补齐 P0 写操作。
- 页面与 API Server 对同一种业务操作使用相同的审计动作。
- 审计事件只在业务成功、事务提交后发送。
- 修改类操作携带脱敏后的修改前和修改后快照。
- 批量操作按实际成功资源逐条发送事件。
- 代码验证完成后，通过部署环境变量灰度打开 API Server 审计上报。

## 非目标

- 不新增审计中心动作或资源。
- 不调整 IAM 权限模型。
- 不接入插件网关运行/取消，因为现有七类资源无法准确表达插件运行实例。
- 不接入包源管理与同步，因为现有资源无法表达包源实例，且无资源的 `admin_edit` 不能满足对象追溯要求。
- 不接入流程市场标签等无法准确映射到现有资源的操作。
- 不审计列表、计数、状态轮询、预览、普通日志读取等高频只读接口。
- 不改变 API 请求参数、响应结构、HTTP 状态码和 APIGW 资源 schema。
- 不在代码仓库保存审计 Token、Endpoint 或其他部署密钥。

## 设计原则

1. **成功后上报**：权限校验通过不等于业务操作成功；事件只能在业务结果成功后产生。
2. **事务一致性**：数据库事务中的操作通过 `transaction.on_commit` 触发审计，回滚事务不产生成功事件。
3. **入口一致性**：页面、API Server、MCP 复用同一动作语义，不因调用入口不同而改变 action ID。
4. **资源真实**：事件中的资源 ID 必须是完成 scope 解析后的内部实例 ID，不能直接使用含义不确定的原始路由参数。
5. **不错误映射**：没有合适现有资源的操作明确延期，不用 `admin_edit` 或其他资源强行承载。
6. **业务可用性优先**：审计客户端异常不阻断业务，但必须留下可检索的结构化错误日志。
7. **最小敏感数据**：只记录识别资源和理解变更所需的信息，不记录密钥、变量值、流程树全文和日志正文。

## 现有动作与资源复用

一期只使用 `IAMMeta` 中已经存在的动作和七类资源。

| 业务操作 | action ID | resource ID |
| --- | --- | --- |
| 项目注册、项目执行代理修改 | `project_edit` | `project` |
| 项目流程创建/导入/复制 | `flow_create` | `flow` |
| 项目流程配置、Webhook 修改 | `flow_edit` | `flow` |
| 项目流程批量删除 | `flow_delete` | `flow` |
| 公共流程导入 | `common_flow_create` | `common_flow` |
| 公共流程批量删除 | `common_flow_delete` | `common_flow` |
| 项目流程创建任务 | `flow_create_task` | `task` |
| 公共流程创建任务 | `common_flow_create_task` | `task` |
| 一次性任务快速创建 | `project_fast_create_task` | `task` |
| 任务启动、暂停、继续、撤销、节点操作、节点回调 | `task_operate` | `task` |
| 任务参数修改、职能任务转普通任务 | `task_edit` | `task` |
| 职能任务认领、认领转交 | `task_claim` | `task` |
| 项目流程创建周期任务 | `flow_create_periodic_task` | `periodic_task` |
| 公共流程创建周期任务 | `common_flow_create_periodic_task` | `periodic_task` |
| 周期任务修改/删除 | `periodic_task_edit` / `periodic_task_delete` | `periodic_task` |
| 项目流程创建计划任务 | `flow_create_clocked_task` | `clocked_task` |
| 计划任务修改/删除 | `clocked_task_edit` / `clocked_task_delete` | `clocked_task` |

详情查看动作保留首版已有行为；一期不扩大详情读取审计范围。

## 审计底座

### 1. 保持兼容的公共入口

保留 `bk_audit_add_event(username, action_id, resource_id, instance, origin_data)` 作为最终发送入口，避免一次性修改所有首版调用。

新增事务安全的调用入口，职责包括：

- 在启用审计时生成必要快照。
- 在事务提交后调用现有发送函数。
- 接受修改前快照，生成 `instance_origin_data`。
- 保持审计异常不向业务调用方抛出。

页面和 API Server 新增调用统一使用事务安全入口；首版存在时机问题的调用迁移到该入口。

### 2. 修改前后快照

修改操作在业务变更前，使用与当前资源一致的审计序列化器生成修改前快照；事务成功后，再生成修改后快照并发送事件。

快照规则：

- 流程不记录 `pipeline_tree` 全文。
- 任务不记录 constants 的值和插件输入输出。
- 周期任务、计划任务不记录任务参数值，只保留名称、调度配置摘要、模板关联等必要字段。
- Webhook 不记录 endpoint 中的认证信息、headers、extra_info 明文。
- 项目执行代理只记录代理用户名和豁免用户标识，不记录无关项目配置。

创建操作没有修改前快照；删除操作的修改前快照来自删除前实例，修改后状态按资源的软删除或删除结果表达。

### 3. 成功判定

不同入口按真实业务结果判定：

- DRF 正常返回 2xx 且持久化完成，视为成功。
- 返回字典或 `JsonResponse` 的旧接口必须满足 `result is True`。
- 异步启动接口在任务成功进入队列后记录 `task_operate`，该事件表示“启动请求已受理”，不代表任务最终执行成功。
- `create_and_start_task` 产生两个事件：任务创建成功和启动请求受理成功。两个动作语义不同，不做合并。
- 权限拒绝、参数校验失败、业务返回失败、事务回滚、异步投递异常均不发送成功事件。

### 4. 批量操作

项目/公共流程导入、跨项目复制、批量删除根据最终结果逐个资源发送事件：

- 只对实际创建或删除成功的模板发送。
- 失败模板不发送成功事件。
- 资源 ID 使用导入、复制后生成的真实模板 ID。
- 不在一期引入新的批次资源或批次动作。

### 5. 失败处理与日志

审计客户端异常继续被捕获，不影响业务响应。错误日志至少包含：

- 固定事件标识 `bk_audit_add_event_failed`。
- action ID、resource ID、instance ID。
- 异常类型和异常栈。

日志不得包含 Token、原始请求体、变量值或其他敏感字段。一期不实现持久化重试队列；灰度阶段通过错误日志和审计中心实收数量发现丢失。

## 页面侧 P0 补漏

| 模块 | 操作 |
| --- | --- |
| 计划任务 | 创建、详情查看、修改、删除 |
| 任务控制 | V3/V4 节点操作、指定节点计时器调整 |
| 任务参数 | 修改任务全局变量 |
| 周期任务 | 启停、Cron 修改、参数修改的旧页面接口 |
| 职能任务 | 认领转交、转普通任务 |
| 流程 | 项目/公共流程导入、批量删除 |
| 项目配置 | 项目执行代理修改 |

首版已有调用同时修正以下问题：

- 项目修改从“修改前上报”改为“修改成功后上报”。
- 轻应用删除和周期任务删除从“删除前上报”改为“删除成功后上报”。
- 任务操作和职能任务认领只在返回 `result=true` 时上报。
- 公共流程创建周期任务使用 `common_flow_create_periodic_task`，不再统一使用项目流程动作。

## API Server P0 补漏

### 任务类

- `create_task`
- `create_and_start_task`
- `fast_create_task`
- `start_task`
- `operate_task`
- `operate_node`
- `node_callback`
- `modify_constants_for_task`

任务创建动作根据 `template_source` 和创建方式选择，不使用固定 action ID。

### 周期任务和计划任务

- `create_periodic_task`
- `set_periodic_task_enabled`
- `modify_cron_for_periodic_task`
- `modify_constants_for_periodic_task`
- `create_clocked_task`

周期任务创建根据项目流程或公共流程选择对应创建动作。

### 流程类

- `import_project_template`
- `import_common_template`
- `copy_template_across_project`
- 已有 `create_template` 保留并补测试

### 项目和流程配置

- `register_project`
- `claim_functionalization_task`
- `apply_webhook_configs`
- `modify_project_executor_proxy`
- 已有 `modify_template_notify`、`modify_template_executor_proxy` 保留并补测试

Webhook 批量配置按实际受影响模板逐条使用 `flow_edit` 上报，不记录 Webhook 认证信息。

## 明确延期的入口

以下接口一期不发送蓝鲸审计事件：

- `plugin_gateway_create_run`
- `plugin_gateway_cancel_run`
- 包源创建、修改、删除和同步
- 流程市场标签创建
- API Server 列表、计数、状态轮询、预览和日志读取接口
- 系统 callback、插件内部 callback 等非用户业务操作

这些入口必须在后续新增合适动作和资源后再接入，不能在一期映射为其他资源。

## API 和权限边界

- 审计调用放在权限校验和参数校验之后，不替代 IAM 校验。
- 权限拒绝不记录成功业务事件；拒绝事件属于后续安全审计范围。
- 使用 `project_inject` 的网关接口必须使用 `request.project.id` 和注入后的项目对象构造审计资源，不能重新解释原始 `bk_biz_id/project_id`。
- 信任应用接口保留当前权限边界，审计操作者使用请求上下文中已验证的用户；项目注册同时保留调用应用信息在现有访问日志中。
- `dispatch_plugin_query` 本身不产生通用业务审计；如果它调用了已覆盖的底层写入口，由底层入口负责发送事件。

## Token 与部署

代码继续通过以下环境变量控制审计：

- `BK_AUDIT_ENDPOINT`
- `BK_AUDIT_DATA_TOKEN`

仓库不新增 Token 默认值，也不提交任何真实 Token。

上线顺序：

1. Token 为空时部署一期代码。
2. 在预发布环境配置 Token，验证 API Server 事件能够被审计中心接收。
3. 在生产 API Server 少量实例配置 Token 并重启/滚动发布。
4. 对照 API Server 访问日志、内部操作记录和审计中心实收事件。
5. 确认身份、动作、资源 ID、成功判定和事件数量一致后，全量 API Server。
6. 页面模块是否配置 Token 单独发布和核验，不能用 API Server 上线状态代替全站审计状态。

如果后续需要在 Worker 记录异步操作的最终结果，Worker 必须单独配置 Token；该能力不属于一期。

## 测试设计

### 审计底座

- Token 关闭时不构造实例、不调用审计客户端。
- Token 开启时成功调用一次客户端。
- 审计客户端异常不影响业务，并产生固定错误标识日志。
- 事务回滚不发送事件，事务提交只发送一次。
- 修改事件包含脱敏后的修改前和修改后快照。

### 页面入口

- 每个新增 P0 入口覆盖成功上报和业务失败不上报。
- 首版提前上报问题覆盖回归测试。
- 项目/公共流程、一次性任务的动作映射分别验证。
- 周期任务和计划任务动作映射分别验证。

### API Server

- 每个写接口验证 action ID、resource ID、实例 ID 和调用次数。
- `create_and_start_task` 验证创建与启动两个事件。
- 异步投递失败不发送启动成功事件。
- 批量导入、复制、删除按实际成功实例发送。
- Webhook 事件不包含 endpoint 认证信息和 extra_info。
- scope 为 CMDB 业务 ID 或内部项目 ID 时，审计资源均使用解析后的内部实例 ID。

### 回归范围

- 原有请求、响应和 APIGW schema 不变。
- 原有操作记录 `record_operation` 保持不变，蓝鲸审计不能替代本地操作记录。
- Token 为空时业务行为、返回值和日志主流程与现状一致。

## 验收标准

一期完成必须同时满足：

1. 范围内所有 P0 页面和 API Server 写操作均有成功路径测试。
2. 权限失败、参数失败、业务失败和事务回滚不会产生成功审计事件。
3. 所有事件只使用现有动作和七类现有资源。
4. 插件网关、包源等延期入口没有被错误映射。
5. 测试中未出现密钥、变量值、流程树全文和日志正文。
6. Token 为空时审计客户端调用次数为零。
7. 预发布配置 Token 后，审计中心能够查询到 API Server 事件。
8. 生产 Token 通过灰度配置启用，不在代码仓库出现真实密钥。

## 实施与验证记录

- TAPD：[`136920805` 标准运维操作审计一期补漏及 API Server 上报](https://tapd.woa.com/10131351/prong/stories/view/1010131351136920805)。
- 审计底座、动作映射、批量成功实例、敏感数据脱敏、事务提交/回滚、页面/API Server 静态覆盖和 Webhook 安全摘要共 59 项测试通过。
- API Server 现有任务、调度、导入、Webhook 和模板配置回归共 69 项测试通过；与审计定向测试合并执行为 `128 passed`。
- 页面相关扩展回归中 28 项通过；另 13 项被仓库既有测试隔离问题阻塞，根因均为测试 patch 污染 DRF 路由扫描后触发 `MagicMock.__name__`，与审计变更前已确认的基线问题一致。
- 变更文件通过 Python 3.6 语法编译、Black、Flake8 和 `git diff --check`。
- `api-resources.yml`、`IAMMeta` 动作/资源配置、`config/default.py`、插件网关、包源和同步入口相对 `upstream/master` 均无差异；仓库未写入 Token 或 Endpoint。
- 审计中心实收、预发布 API Server Token 开启及生产灰度仍属于部署后验收，不能由本地测试替代。
