# 插件网关接入指南

本文说明外部平台如何通过 API 网关接入标准运维插件网关，并以 BKFlow 作为示例说明典型接入方式。

## 1. 接入前提

接入前请先确认：

1. 标准运维已完成插件网关部署
2. 标准运维侧已经创建 `PluginGatewaySourceConfig`
3. API 网关已将相关受限资源授权给消费方应用
4. 消费方持有合法的 `bk_app_code / bk_app_secret`
5. 消费方回调地址的域名已加入 `callback_domain_allow_list`
6. 目标插件 ID 已加入 `plugin_allow_list`

额外约束：

- `callback_domain_allow_list` 为空时，所有回调地址都会被拒绝
- `plugin_allow_list` 为空时，所有插件都会被拒绝

## 2. 接口总览

推荐调用顺序如下：

1. 查询分类
2. 查询插件列表
3. 按版本查询插件详情
4. 创建执行记录
5. 轮询状态或接收回调
6. 必要时取消执行

所有接口均走 `/apigw/plugin-gateway/` 前缀。

补充说明：

- 这组接口当前属于 API 网关受限资源，不支持在网关侧公开申请
- 接口免用户登录态，但仍要求应用鉴权和资源权限

## 3. 插件目录发现

### 3.1 查询分类

请求：

```bash
GET /apigw/plugin-gateway/categories/
```

返回示例：

```json
{
  "result": true,
  "data": {
    "categories": [
      {"id": "builtin", "name": "标准运维内置插件"},
      {"id": "third_party", "name": "标准运维第三方插件"}
    ]
  },
  "code": 0
}
```

### 3.2 查询插件列表

请求：

```bash
GET /apigw/plugin-gateway/plugins/
```

返回示例：

```json
{
  "result": true,
  "data": {
    "total": 1,
    "apis": [
      {
        "id": "bk_plugin_demo",
        "name": "Demo Plugin",
        "plugin_source": "third_party",
        "plugin_code": "bk_plugin_demo",
        "wrapper_version": "2.0.0",
        "default_version": "1.1.0",
        "latest_version": "1.1.0",
        "versions": ["1.0.0", "1.1.0"],
        "category": "third_party",
        "meta_url_template": "https://bk-sops.example/apigw/plugin-gateway/plugins/bk_plugin_demo/?version={version}"
      }
    ]
  },
  "code": 0
}
```

关键字段说明：

| 字段 | 说明 |
|------|------|
| `id` | 插件唯一标识 |
| `plugin_source` | 插件来源类型 |
| `plugin_code` | 插件代码 |
| `wrapper_version` | 当前统一为 `v4.0.0` |
| `default_version` | 默认版本 |
| `versions` | 可选版本列表 |
| `meta_url_template` | 按版本获取详情的 URL 模板 |

### 3.3 查询插件详情

请求：

```bash
GET /apigw/plugin-gateway/plugins/bk_plugin_demo/?version=1.1.0
```

返回示例：

```json
{
  "result": true,
  "data": {
    "id": "bk_plugin_demo",
    "name": "Demo Plugin",
    "plugin_source": "third_party",
    "plugin_code": "bk_plugin_demo",
    "plugin_version": "1.1.0",
    "wrapper_version": "2.0.0",
    "url": "https://bk-sops.example/apigw/plugin-gateway/runs/",
    "methods": ["POST"],
    "inputs": [
      {
        "key": "biz_id",
        "name": "业务 ID",
        "type": "integer",
        "description": "业务 ID",
        "required": true
      }
    ],
    "outputs": [
      {
        "key": "job_instance_id",
        "name": "作业实例 ID",
        "type": "integer",
        "description": "JOB instance id"
      }
    ],
    "polling": {
      "url": "https://bk-sops.example/apigw/plugin-gateway/runs/status/",
      "task_tag_key": "open_plugin_run_id",
      "success_tag": {"key": "status", "value": "SUCCEEDED", "data_key": "data.outputs"},
      "fail_tag": {"key": "status", "value": "FAILED", "msg_key": "data.error_message"},
      "running_tag": {"key": "status", "value": "RUNNING"}
    }
  },
  "code": 0
}
```

说明：

- 详情中的 `url` 与 `polling.url` 由标准运维运行时动态注入部署域名
- 若请求的 `version` 不在 `versions` 列表中，接口会返回不存在错误

## 4. 创建执行记录

请求：

```bash
POST /apigw/plugin-gateway/runs/
```

请求体：

```json
{
  "source_key": "bkflow",
  "plugin_id": "bk_plugin_demo",
  "plugin_version": "1.1.0",
  "client_request_id": "task_1_node_1_attempt_1",
  "callback_url": "https://bkflow.example.com/api/plugin-gateway/callback",
  "callback_token": "token-001",
  "inputs": {
    "target_ip": "127.0.0.1"
  },
  "project_id": 2001
}
```

字段说明：

| 字段 | 必填 | 说明 |
|------|------|------|
| `source_key` | 是 | 来源标识，需与 `PluginGatewaySourceConfig.source_key` 一致 |
| `plugin_id` | 是 | 插件 ID |
| `plugin_version` | 是 | 插件版本 |
| `client_request_id` | 是 | 调用方内的幂等键 |
| `callback_url` | 是 | 执行完成后标准运维回调的地址 |
| `callback_token` | 是 | 回调时写入 `X-Callback-Token` 的 token |
| `inputs` | 否 | 插件输入 |
| `project_id` | 否 | 可选项目 ID；未传时可由来源配置自动回填 |

响应示例：

```json
{
  "result": true,
  "data": {
    "open_plugin_run_id": "run-001",
    "status": "WAITING_CALLBACK"
  },
  "code": 0
}
```

### 4.1 幂等规则

标准运维按 `(caller_app_code, client_request_id)` 做幂等。

- 同一应用重复提交相同 `client_request_id` 且关键字段完全一致时，会复用同一条运行记录
- 同一应用重复提交相同 `client_request_id` 但 `source_key`、`plugin_id`、`plugin_version`、`callback_url`、`callback_token` 或触发载荷不一致时，会返回冲突错误
- 不同应用可以复用相同的 `client_request_id`

建议将 `client_request_id` 设计成“同一次触发意图”的稳定标识，例如：

```text
{task_id}_{node_id}_{attempt_no}
```

## 5. 状态查询与详情查询

### 5.1 状态轮询

请求：

```bash
GET /apigw/plugin-gateway/runs/status/?task_tag=run-001
```

其中 `task_tag` 直接使用 `open_plugin_run_id`。

### 5.2 详情查询

请求：

```bash
GET /apigw/plugin-gateway/runs/run-001/
```

标准运维会校验当前调用方的 `app_code` 与创建记录时的 `caller_app_code` 是否一致，不同应用之间不能互相读取运行状态。

## 6. 结果回调

标准运维内部在拿到执行结果后，会调用：

```python
from gcloud.plugin_gateway.services.callbacks import PluginGatewayCallbackService

PluginGatewayCallbackService.callback_run(
    open_plugin_run_id="run-001",
    run_status="SUCCEEDED",
    outputs={"job_instance_id": 1001},
)
```

回调行为如下：

- URL：`callback_url`
- Header：`X-Callback-Token: {callback_token}`
- `callback_token` 在数据库中加密存储，回调时解密使用
- 单次回调内最多重试 3 次

回调体示例：

```json
{
  "open_plugin_run_id": "run-001",
  "status": "SUCCEEDED",
  "outputs": {"job_instance_id": 1001},
  "error_message": "",
  "truncated": false,
  "truncated_fields": []
}
```

若 `outputs` 超过大小限制，标准运维会保留摘要并显式标记：

```json
{
  "outputs": {
    "_truncated": true,
    "_summary": {
      "original_size": 70000,
      "keys": ["payload"]
    }
  },
  "truncated": true,
  "truncated_fields": ["outputs"]
}
```

## 7. 取消执行

请求：

```bash
POST /apigw/plugin-gateway/runs/run-001/cancel/
```

当前版本的取消语义仅作用于插件网关执行记录本身：

- 未终态时置为 `CANCELLED`
- 已终态时幂等返回

当前版本不会自动反向中止真实标准插件运行时。

## 8. BKFlow 接入示例

BKFlow 的典型接入方式如下：

1. 调用 `/apigw/plugin-gateway/categories/` 与 `/apigw/plugin-gateway/plugins/` 同步目录
2. 根据 `meta_url_template` 拉取指定版本 detail
3. 将 detail 中的 `url`、`polling`、`plugin_version` 写入本地快照
4. 运行时以稳定的 `client_request_id` 调用 `/apigw/plugin-gateway/runs/`
5. 将 `open_plugin_run_id` 作为 `task_tag` 轮询
6. 同时监听 `callback_url` 上的异步结果回调

## 9. 常见问题

### 9.1 为什么创建记录成功后状态一直是 `WAITING_CALLBACK`？

当前版本会自动调度已暴露的第三方标准插件；如果运行时返回轮询态或回调态，网关会快速失败并通过 `error_message` 返回原因，避免调用方静默挂起。

### 9.2 为什么 `callback_url` 被拒绝？

因为来源配置中的 `callback_domain_allow_list` 未包含当前域名，或者白名单为空。建议按环境分别预置 BKFlow 的测试、预发、正式域名，并确保调用侧 `source_key` 与 `PluginGatewaySourceConfig.source_key` 完全一致。

### 9.3 为什么执行时报插件未开放？

因为 `plugin_id` 不在当前来源的 `plugin_allow_list` 中，或者白名单为空。

### 9.4 为什么同一个 `client_request_id` 会报冲突？

因为同一应用已经使用该幂等键创建过记录，但本次请求的关键字段与首次请求不一致。
