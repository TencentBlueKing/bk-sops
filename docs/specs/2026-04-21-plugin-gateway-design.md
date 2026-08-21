# 插件网关设计

## 概述

标准运维已经具备标准插件生态、第三方插件远程加载能力和 API 网关能力，但缺少一层面向外部平台的统一插件消费协议。

本设计在标准运维内部新增 `gcloud.plugin_gateway` 子系统，并将对外接口统一收敛到 `gcloud.apigw.views.plugin_gateway`，提供一组基于 `/apigw/plugin-gateway/` 的目录与执行网关接口，使外部平台可以：

- 发现可消费的插件目录
- 基于 `uniform_api v4.0.0` 风格元数据拉取插件详情
- 通过统一入口登记一次插件运行
- 按运行 ID 查询状态和详情
- 接收标准运维回调的执行结果

## 范围

### 对外接口

- `GET /apigw/plugin-gateway/categories/`
- `GET /apigw/plugin-gateway/plugins/`
- `GET /apigw/plugin-gateway/plugins/{plugin_id}/?version=...`
- `POST /apigw/plugin-gateway/runs/`
- `GET /apigw/plugin-gateway/runs/status/?task_tag=...`
- `GET /apigw/plugin-gateway/runs/{run_id}/`
- `POST /apigw/plugin-gateway/runs/{run_id}/internal-callback/`
- `POST /apigw/plugin-gateway/runs/{run_id}/cancel/`

### 数据模型

- `PluginGatewaySourceConfig`
  - 来源标识
  - 默认 `project_id`
  - 回调域名白名单
  - 插件白名单
  - 空间到项目映射
  - 来源级黑名单
  - 执行超时时间
  - 启用开关
- `PluginGatewayRun`
  - `open_plugin_run_id`
  - `(caller_app_code, client_request_id)` 维度的幂等约束
  - 回调地址与加密后的回调 token
  - 运行状态、输出、错误信息
  - 跨进程恢复用运行时输出、调度次数、执行过期时间

## 非目标

- 当前版本不提供独立的来源配置页面
- 当前版本不重新设计标准运维现有执行引擎
- 当前版本不创建标准运维引擎 `PipelineModel` 实例；插件通过组件运行壳直接执行

> 注意：2026-06-26 全量能力迭代已经收敛内置插件暴露/调度与同步、轮询、回调三种运行模式；详见 `docs/specs/2026-06-26-plugin-gateway-full-capability-design.md`。

## 设计方案

### 1. 模块分层

能力分层如下：

| 文件 | 职责 |
|------|------|
| `gcloud/plugin_gateway/models.py` | 来源配置与运行记录模型 |
| `gcloud/plugin_gateway/services/catalog.py` | 分类、列表、详情元数据加载 |
| `gcloud/plugin_gateway/services/builtin_catalog.py` | 内置组件元数据适配 |
| `gcloud/plugin_gateway/services/context.py` | 白名单校验与默认项目回填 |
| `gcloud/plugin_gateway/services/execution.py` | 执行登记、幂等冲突校验、详情与取消 |
| `gcloud/plugin_gateway/services/runner.py` | 组件运行壳，直接调 `execute/schedule` |
| `gcloud/plugin_gateway/services/callbacks.py` | 结果回调桥接 |
| `gcloud/apigw/views/plugin_gateway.py` | APIGW 对外视图 |
| `gcloud/apigw/urls.py` | `/apigw/plugin-gateway/` 路由注册 |

这样可以保持：

- 对外接口继续遵循 `gcloud/apigw` 既有分层约定
- 领域模型与服务逻辑独立在 `gcloud.plugin_gateway`
- APIGW 文档、资源定义和实现入口集中维护

### 2. 目录协议

目录服务已从早期的 fixture 静态实现切换为**内置组件适配 + 第三方插件动态拉取**：

- 内置插件由 `BuiltinCatalogService` 读取 `ComponentLibrary.component_list()`，输出 `plugin_source=builtin`，插件 ID 编码为 `builtin__<component_code>`
- 第三方插件通过 `PluginServiceApiClient.get_plugin_list()` 拉取清单，并逐个补齐 `_get_plugin_meta()` 的版本/框架信息，插件 ID 继续兼容裸 `code`
- 来源配置 `do_not_open_list` 会在列表、详情、执行三处保持一致拦截
- `detail_meta` 由 `_get_plugin_detail_schema()` 按 `(plugin_code, version)` 实时获取并转换为 v4 字段
- `meta_url_template`、`url`、`polling.url` 由运行时基于当前部署域名注入
- `polling.running_tag` 固定为 `RUNNING`
- 目录拉取与 detail 拉取均加 `TTLCache`（60s）控制读取成本
- `fixtures/uniform_api_v4/*.json` 当前仅作为单元测试夹具，不再作为线上目录数据源

当前目录协议返回的关键字段包括：

- `id`
- `name`
- `plugin_source`
- `plugin_code`
- `group`
- `wrapper_version`
- `default_version`
- `latest_version`
- `versions`
- `meta_url_template`

详情接口会校验请求版本必须出现在 `versions` 列表中。

### 3. 执行登记

`POST /apigw/plugin-gateway/runs/` 的职责如下：

1. 校验来源配置存在且启用
2. 校验 `callback_url` 的域名命中白名单
3. 校验 `plugin_id` 在来源白名单中
4. 校验插件不在来源 `do_not_open_list`
5. 按需保存 `context`，并在 dispatch 时按 `biz scope -> Project.bk_biz_id -> scope_project_map -> default_project_id` 解析项目
6. 将 `context.operator` 写入组件运行上下文
7. 以 `(caller_app_code, client_request_id)` 做幂等登记
8. 对重复幂等请求做关键字段冲突检测
9. 返回 `open_plugin_run_id`

关键约束：

- 同一应用内相同 `client_request_id` 只能对应一份语义一致的请求
- 不同应用可以复用同一个 `client_request_id`
- `callback_token` 以加密形式存储，避免明文凭证直接落库

### 4. 状态查询与详情查询

状态接口与详情接口都要求当前调用方应用与创建记录时的 `caller_app_code` 一致。

- 状态接口面向 polling 协议，只查询必要字段
- 详情接口返回完整运行记录视图

这样既保留 `uniform_api` 所需字段，又避免将完整对象查询复用到所有读取场景。

### 5. 来源治理

`PluginGatewaySourceConfig` 维护来源级治理信息：

| 字段 | 说明 |
|------|------|
| `source_key` | 来源标识 |
| `display_name` | 来源名称 |
| `default_project_id` | 默认项目回填值 |
| `callback_domain_allow_list` | 回调域名白名单 |
| `scope_project_map` | 业务空间到标准运维项目的显式映射 |
| `do_not_open_list` | 来源级黑名单 |
| `execution_timeout_seconds` | 单次执行超时时间 |
| `is_enabled` | 来源开关 |

治理规则：

- `callback_domain_allow_list` 为空时，默认拒绝所有回调地址
- 来源默认允许使用目录中的全部插件
- `do_not_open_list` 同时作用于列表、详情和执行

插件风险通过来源级黑名单和消费方空间级准入共同治理，无需维护逐插件来源白名单。

### 6. 回调桥接

内部回调入口 `POST /apigw/plugin-gateway/runs/{run_id}/internal-callback/` 用于回调型插件写回数据，并投递到 `open_plugin_callback` 队列推进 run。

`PluginGatewayCallbackService.callback_run(...)` 负责终态回调消费方：

1. 根据 `open_plugin_run_id` 找到运行记录
2. 若记录已是终态，则直接短路
3. 截断过大的 `outputs`
4. 更新运行状态、输出和错误信息
5. 使用 `callback_url + X-Callback-Token` 回调消费方
6. 在单次调用内做有限重试并记录日志

当前回调保护策略：

- 最大输出体大小：`64 * 1024` bytes
- 超限时保留 `_summary`
- 单次回调最多重试 3 次

## 安全边界

当前版本重点覆盖以下边界：

- 所有对外接口都通过 `@apigw_require`
- 输入错误在视图层统一转换为 4xx 风格错误码响应
- 回调域名与插件开放范围由来源配置显式治理
- 运行记录查询按 `caller_app_code` 做跨应用隔离
- 回调 token 加密存储
- 来源级 `do_not_open_list` 对列表、详情、执行一致生效

## 配套产物

本设计要求对以下 APIGW 配套产物同步维护：

- `docs/zh_hans/apidoc/*.md`
- `docs/en/apidoc/*.md`
- `gcloud/apigw/management/commands/data/api-resources.yml`
- `gcloud/apigw/docs/apigw-docs.tgz`

这样可以保证对外资源、接口文档和实际实现保持一致。

## 实现现状

2026-06-26 全量能力迭代后，本设计中原 MVP 缺口已收敛。需求口径与落地方案见 `docs/specs/2026-06-26-plugin-gateway-full-capability-design.md` 与 `docs/plans/2026-06-26-plugin-gateway-full-capability.md`。

- 目录发现：分类、列表、详情，覆盖内置插件和第三方插件
- 执行登记：`(caller_app_code, client_request_id)` 幂等、并发 `IntegrityError` 收敛为 409
- 真实调度：`tasks.dispatch_plugin_gateway_run` 通过组件运行壳直接实例化 `bound_service` 调 `execute/schedule`，不创建引擎实例
- 异步推进：轮询模式由 `poll_plugin_gateway_run` 推进，回调模式由内部回调入口和 `callback_plugin_gateway_run` 推进
- 来源治理：回调域白名单、插件白名单、`scope_project_map`、`do_not_open_list`、`default_project_id`、执行超时、来源开关
- 状态查询 / 详情查询 / 取消执行（跨应用按 `caller_app_code` 隔离）
- 回调桥接：终态回调、`X-Callback-Token`、输出体截断、有限重试、`callback_delivered_at` 去重

### 协议侧结论

BKFlow `uniform_api v4.0.0` 协议本身**无需扩展**即可承载全量能力：它已支持 `CREATED/RUNNING/WAITING_CALLBACK/SUCCEEDED/FAILED/CANCELLED` 全套状态、轮询与回调两种模式、空间级开放治理与快照。bk-sops execute body 仅新增可选 `context`，不升级 wrapper 版本；不传 `context` 时仍可按来源 `default_project_id` 兜底。
