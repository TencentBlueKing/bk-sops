# Plugin Gateway Deployment Guide

This document explains how to deploy the plugin gateway, initialize source configuration, and sync API gateway resources after the feature is released.

## 1. Overview

The current implementation is split into:

- Django app: `gcloud.plugin_gateway`
- APIGW views: `gcloud.apigw.views.plugin_gateway`
- API prefix: `/apigw/plugin-gateway/`

The current version provides:

- built-in and third-party plugin category, list, and detail APIs
- execution registration
- synchronous completion, polling, and callback execution modes
- status and detail query APIs with `CREATED/RUNNING/WAITING_CALLBACK/SUCCEEDED/FAILED/CANCELLED`
- cancellation
- callback bridge
- source-level allow-list, block-list, default project, scope-to-project mapping, and timeout configuration

Current runtime boundary:

- plugin execution uses the component runtime shell and does not create a bk-sops engine `PipelineModel`
- `context.operator` is written into the plugin runtime context, so downstream systems keep real-user permission checks
- `context.scope_type/scope_value` is resolved to a bk-sops project inside bk-sops; unresolved context fails the run explicitly
- components that require unavailable engine node context should be configured in source-level `do_not_open_list`

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
- Celery workers for `open_plugin_dispatch`, `open_plugin_polling`, and `open_plugin_callback`
- beat / periodic task processes for timeout sweeping

If workers are split by queue, use commands similar to:

```bash
python manage.py celery worker -l info -Q open_plugin_dispatch
python manage.py celery worker -l info -Q open_plugin_polling
python manage.py celery worker -l info -Q open_plugin_callback
```

`sweep_expired_plugin_gateway_runs` is triggered by beat every 60 seconds. Confirm the beat schedule is deployed with the code.

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
        "scope_project_map": {
            "bkflow_space:space-1": 2001,
        },
        "do_not_open_list": ["builtin__unsafe_component"],
        "execution_timeout_seconds": 7200,
        "is_enabled": True,
    },
)
```

Important rules:

- an empty `callback_domain_allow_list` rejects all callback URLs
- a source can execute every catalog plugin by default and does not need to maintain `plugin_allow_list`
- plugins that cannot run safely in the component shell must be added to `do_not_open_list`
- built-in plugin ids use `builtin__<component_code>`; third-party plugin ids keep the bare code
- `scope_project_map` keys use `<scope_type>:<scope_value>`
- `do_not_open_list` blocks list, detail, and execute consistently
- `execution_timeout_seconds` controls the timeout sweep for a single run

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
| `POST` | `/apigw/plugin-gateway/runs/{run_id}/internal-callback/` | internal callback for callback-mode plugins |
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
    "plugin_id": "builtin__job_execute_task",
    "plugin_version": "legacy",
    "client_request_id": "demo_task_1_node_1_attempt_1",
    "callback_url": "https://bkflow.example.com/api/callback",
    "callback_token": "callback-token",
    "inputs": {
      "target_ip": "127.0.0.1"
    },
    "context": {
      "scope_type": "biz",
      "scope_value": "2",
      "operator": "bkflow-user",
      "space_id": "bkflow-space-1",
      "task_id": "demo_task_1",
      "node_id": "node_1"
    }
  }'
```

The created run starts as `CREATED`, then `open_plugin_dispatch` advances it to a terminal state or an async waiting state.

## 6. Operational Boundary

The current release should be treated as a full plugin gateway layer with these operational notes:

- catalog discovery covers both built-in and third-party plugins
- registration, synchronous completion, polling, callback, detail query, cancellation, and terminal callback are ready
- BKFlow only passes `context`; bk-sops resolves the target project
- execution does not create engine instances, so components that require engine node state or global variable decryption should be added to `do_not_open_list`
- third-party plugins now execute through the runtime shell path; run equivalence regression for synchronous third-party plugins before production rollout
