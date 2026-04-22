# Open Plugin Gateway Access Guide

This document explains how external platforms can consume the bk-sops open plugin gateway through API Gateway.

## 1. Prerequisites

Before integrating, make sure that:

1. the open plugin gateway has been deployed
2. `PluginGatewaySourceConfig` has been created
3. API Gateway resources have been exposed and granted to the consumer app
4. the consumer owns valid `bk_app_code / bk_app_secret`
5. the callback domain is included in `callback_domain_allow_list`
6. the target plugin id is included in `plugin_allow_list`

Additional rules:

- an empty `callback_domain_allow_list` rejects all callback URLs
- an empty `plugin_allow_list` rejects all plugins

## 2. API Flow

Recommended order:

1. query categories
2. query plugin list
3. query plugin detail by version
4. create an execution record
5. poll status or receive callback
6. cancel if needed

All APIs are exposed under `/apigw/plugin-gateway/`.

## 3. Catalog Discovery

### 3.1 Get Categories

```bash
GET /apigw/plugin-gateway/categories/
```

### 3.2 Get Plugin List

```bash
GET /apigw/plugin-gateway/plugins/
```

Example payload:

```json
{
  "result": true,
  "data": {
    "total": 2,
    "apis": [
      {
        "id": "plugin_job_execute",
        "name": "JOB 执行作业",
        "default_version": "1.2.0",
        "versions": ["1.2.0", "1.3.0"],
        "meta_url_template": "https://bk-sops.example/apigw/plugin-gateway/plugins/plugin_job_execute/?version={version}"
      }
    ]
  },
  "code": 0
}
```

### 3.3 Get Plugin Detail

```bash
GET /apigw/plugin-gateway/plugins/plugin_job_execute/?version=1.2.0
```

The detail response includes:

- the resolved execution URL
- polling configuration
- the selected plugin version

Both `url` and `polling.url` are injected at runtime from the current deployment domain.

## 4. Create a Run

```bash
POST /apigw/plugin-gateway/runs/
```

Request body example:

```json
{
  "source_key": "bkflow",
  "plugin_id": "plugin_job_execute",
  "plugin_version": "1.2.0",
  "client_request_id": "task_1_node_1_attempt_1",
  "callback_url": "https://bkflow.example.com/api/open-plugin/callback",
  "callback_token": "token-001",
  "inputs": {
    "target_ip": "127.0.0.1"
  },
  "project_id": 2001
}
```

Response example:

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

### 4.1 Idempotency Rules

Idempotency is scoped by `(caller_app_code, client_request_id)`.

- the same app can reuse the same `client_request_id` only for the same semantic request
- if the same app replays the same id with different key fields, the gateway returns a conflict error
- different apps may reuse the same `client_request_id`

## 5. Query Status and Detail

Status polling:

```bash
GET /apigw/plugin-gateway/runs/status/?task_tag=run-001
```

Detail query:

```bash
GET /apigw/plugin-gateway/runs/run-001/
```

The gateway checks that the caller app matches the app that created the run.

## 6. Callback

Internally, bk-sops reports the result through:

```python
from gcloud.plugin_gateway.services.callbacks import PluginGatewayCallbackService

PluginGatewayCallbackService.callback_run(
    open_plugin_run_id="run-001",
    run_status="SUCCEEDED",
    outputs={"job_instance_id": 1001},
)
```

Behavior:

- callback URL: `callback_url`
- callback header: `X-Callback-Token`
- `callback_token` is encrypted at rest
- the gateway retries the callback up to 3 times in a single invocation

If outputs are too large, the gateway returns a truncated payload plus a summary marker.

## 7. Cancel

```bash
POST /apigw/plugin-gateway/runs/run-001/cancel/
```

Cancellation only changes the gateway-side run record. It does not stop the real plugin runtime automatically.

## 8. Current Boundary

The current version is a gateway layer, not a full execution proxy. It supports:

- catalog discovery
- run registration
- status polling
- detail query
- cancellation
- callback bridge

Automatic dispatch to the real plugin runtime still needs to be implemented inside bk-sops.
