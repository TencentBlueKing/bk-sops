# Plugin Gateway Deployment Guide

This document explains how to deploy the plugin gateway, initialize source configuration, and sync API gateway resources after the feature is released.

## 1. Overview

The current implementation is split into:

- Django app: `gcloud.plugin_gateway`
- APIGW views: `gcloud.apigw.views.plugin_gateway`
- API prefix: `/apigw/plugin-gateway/`

The current version provides:

- plugin category, list, and detail APIs
- execution registration
- status and detail query APIs
- cancellation
- callback bridge
- source-level allow-list and default project configuration

Current boundary:

- catalog APIs are ready for external consumption
- execution APIs currently handle registration, persistence, and callback bridging
- the gateway dispatches exposed third-party standard plugins automatically; polling/callback runtime states fail fast instead of hanging

## 2. Release Steps

### 2.1 Publish Code

Deploy the version that contains `gcloud.plugin_gateway` and `gcloud.apigw.views.plugin_gateway`.

### 2.2 Install Dependencies

If your deployment rebuilds the Python environment, install dependencies as usual:

```bash
pip install -r requirements.txt
```

### 2.3 Run Migrations

The gateway adds two models:

- `PluginGatewaySourceConfig`
- `PluginGatewayRun`

Run:

```bash
python manage.py migrate
```

Or only for this app:

```bash
python manage.py migrate plugin_gateway
```

### 2.4 Restart Services

Restart at least:

- web processes
- Celery workers
- beat / periodic task processes if they are deployed separately

No dedicated plugin gateway worker is required in the current version.

## 3. Initialize Source Configuration

There is no standalone admin page yet. Initialize `PluginGatewaySourceConfig` through Django shell, a bootstrap script, or a data migration.

Example:

```bash
python manage.py shell
```

```python
from gcloud.plugin_gateway.models import PluginGatewaySourceConfig

PluginGatewaySourceConfig.objects.update_or_create(
    source_key="bkflow",
    defaults={
        "display_name": "BKFlow",
        "default_project_id": 2001,
        "callback_domain_allow_list": ["bkflow.example.com"],
        "plugin_allow_list": ["plugin_job_execute", "plugin_job_status"],
        "is_enabled": True,
    },
)
```

Important rules:

- an empty `callback_domain_allow_list` rejects all callback URLs
- an empty `plugin_allow_list` rejects all plugins

## 4. Sync API Gateway Artifacts

The gateway-related artifacts are:

- resource definition: `gcloud/apigw/management/commands/data/api-resources.yml`
- gateway definition: `gcloud/apigw/management/commands/data/api-definition.yml`
- resource docs archive: `gcloud/apigw/docs/apigw-docs.tgz`

Resources to expose:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/apigw/plugin-gateway/categories/` | get categories |
| `GET` | `/apigw/plugin-gateway/plugins/` | get plugin list |
| `GET` | `/apigw/plugin-gateway/plugins/{plugin_id}/` | get plugin detail |
| `POST` | `/apigw/plugin-gateway/runs/` | create execution record |
| `GET` | `/apigw/plugin-gateway/runs/status/` | poll status |
| `GET` | `/apigw/plugin-gateway/runs/{run_id}/` | get execution detail |
| `POST` | `/apigw/plugin-gateway/runs/{run_id}/cancel/` | cancel execution |

Recommended sync sequence:

1. update `api-resources.yml`
2. update `docs/{zh_hans,en}/apidoc/*.md`
3. rebuild `gcloud/apigw/docs/apigw-docs.tgz`
4. run the existing APIGW sync command

## 5. Post-Deployment Checks

Check source config:

```bash
python manage.py shell -c "
from gcloud.plugin_gateway.models import PluginGatewaySourceConfig
print(list(PluginGatewaySourceConfig.objects.values('source_key', 'is_enabled')))
"
```

Check catalog API:

```bash
curl -X GET 'https://{gateway-host}/apigw/plugin-gateway/plugins/' \
  -H 'X-Bkapi-Authorization: ...'
```

Check execution registration:

```bash
curl -X POST 'https://{gateway-host}/apigw/plugin-gateway/runs/' \
  -H 'Content-Type: application/json' \
  -H 'X-Bkapi-Authorization: ...' \
  -d '{
    "source_key": "bkflow",
    "plugin_id": "plugin_job_execute",
    "plugin_version": "1.2.0",
    "client_request_id": "demo_task_1_node_1_attempt_1",
    "callback_url": "https://bkflow.example.com/api/callback",
    "callback_token": "callback-token",
    "inputs": {
      "target_ip": "127.0.0.1"
    }
  }'
```

The created run should enter `WAITING_CALLBACK`.

## 6. Operational Boundary

The current release should be treated as a gateway layer:

- catalog discovery is ready
- registration, polling, detail query, cancellation, and callback are ready
- exposed third-party standard plugins are dispatched automatically; polling/callback runtime states fail fast
