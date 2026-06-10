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
- `POST /apigw/plugin-gateway/runs/{run_id}/cancel/`

### 数据模型

- `PluginGatewaySourceConfig`
  - 来源标识
  - 默认 `project_id`
  - 回调域名白名单
  - 插件白名单
  - 启用开关
- `PluginGatewayRun`
  - `open_plugin_run_id`
  - `(caller_app_code, client_request_id)` 维度的幂等约束
  - 回调地址与加密后的回调 token
  - 运行状态、输出、错误信息

## 非目标

- 当前版本不提供独立的来源配置页面
- 当前版本不重新设计标准运维现有执行引擎
- 当前版本不自动将执行请求同步转发到真实标准插件运行时

## 设计方案

### 1. 模块分层

能力分层如下：

| 文件 | 职责 |
|------|------|
| `gcloud/plugin_gateway/models.py` | 来源配置与运行记录模型 |
| `gcloud/plugin_gateway/services/catalog.py` | 分类、列表、详情元数据加载 |
| `gcloud/plugin_gateway/services/context.py` | 白名单校验与默认项目回填 |
| `gcloud/plugin_gateway/services/execution.py` | 执行登记、幂等冲突校验、详情与取消 |
| `gcloud/plugin_gateway/services/callbacks.py` | 结果回调桥接 |
| `gcloud/apigw/views/plugin_gateway.py` | APIGW 对外视图 |
| `gcloud/apigw/urls.py` | `/apigw/plugin-gateway/` 路由注册 |

这样可以保持：

- 对外接口继续遵循 `gcloud/apigw` 既有分层约定
- 领域模型与服务逻辑独立在 `gcloud.plugin_gateway`
- APIGW 文档、资源定义和实现入口集中维护

### 2. 目录协议

目录服务继续使用 fixture 驱动的静态实现，但补齐了运行时组装能力：

- `list_meta.json` 支持多个插件
- `detail_meta.json` 支持多插件明细
- `meta_url_template`、`url`、`polling.url` 由运行时基于当前部署域名注入
- fixture 加载增加 TTL 缓存，便于控制热更新和读取成本

当前目录协议返回的关键字段包括：

- `id`
- `name`
- `plugin_source`
- `plugin_code`
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
4. 按需回填 `default_project_id`
5. 以 `(caller_app_code, client_request_id)` 做幂等登记
6. 对重复幂等请求做关键字段冲突检测
7. 返回 `open_plugin_run_id`

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
| `plugin_allow_list` | 允许调用的插件 ID 白名单 |
| `is_enabled` | 来源开关 |

治理规则：

- `callback_domain_allow_list` 为空时，默认拒绝所有回调地址
- `plugin_allow_list` 为空时，默认拒绝所有插件

这避免了“空白名单即全放行”的安全歧义。

### 6. 回调桥接

`PluginGatewayCallbackService.callback_run(...)` 负责：

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

## 配套产物

本设计要求对以下 APIGW 配套产物同步维护：

- `docs/zh_hans/apidoc/*.md`
- `docs/en/apidoc/*.md`
- `gcloud/apigw/management/commands/data/api-resources.yml`
- `gcloud/apigw/docs/apigw-docs.tgz`

这样可以保证对外资源、接口文档和实际实现保持一致。

## 当前版本边界

当前版本已经具备：

- 目录发现
- 执行登记
- 来源治理
- 状态查询
- 取消执行
- 回调桥接

但尚未完成“插件网关 -> 真实标准插件运行时”的自动调度适配。因此当前版本应被定位为插件网关层，而不是完整执行代理层。
