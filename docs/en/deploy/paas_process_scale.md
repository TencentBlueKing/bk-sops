# PaaS process specs and instance operations

On BlueKing PaaS, the multi-tenant / enterprise layout splits into four modules from `app_desc.yaml`: `default`, `api`, `callback`, and `pipeline`. Replica count, resource plan, and gunicorn settings can be changed per environment without touching application code.

For community source or upload-package deploy, see [source_code_deploy.md](source_code_deploy.md) and [upload_pack_deploy.md](upload_pack_deploy.md). This page covers Smart-app multi-module processes only.

## How to read a spec

Each process in `app_desc.yaml` has two fields:

```yaml
plan: 4C2G5R
replicas: 2
```

| Field | Meaning |
|---|---|
| `4C` | CPU **limit: 4 cores** |
| `2G` | Memory **limit: 2Gi** |
| `5R` | Plan-name suffix, **not** 5 instances |
| `replicas` | Pod count for this process |

`4C2G5R` × `replicas: 2` means two 4-core / 2Gi instances. `4C1G5R` is the 1Gi variant. PaaS also sets a small request (often `100m` / `64Mi`); OOM and burst capacity follow the limit.

## Repository baseline (current descriptor)

| Module | Process | Role | Plan | Replicas |
|---|---|---|---|---|
| default | web | UI, admin, internal HTTP | 4C2G5R | 3 |
| default | beat | Celery beat; must stay at 1 | 4C1G5R | 1 |
| default | dworker | `default` queue | 4C2G5R | 2 |
| api | web | Gateway create/start/status | 4C2G5R | 2 |
| callback | web | Node / plugin callbacks | 4C2G5R | 2 |
| pipeline | api-er-e / api-er-s | API task execute / schedule | 4C2G5R | 2 |
| pipeline | api-task | API task prepare | 4C1G5R | 2 |
| pipeline | er-e / er-s | UI task execute / schedule | 4C2G5R | 2 |
| pipeline | peri-er-e / peri-er-s | Periodic execute / schedule | 4C2G5R | 2 |
| pipeline | cworker | timeout, retry, task callback | 4C1G5R | 2 |
| pipeline | stats-worker | statistics | 4C2G5R | 2 |
| pipeline | cleaner | history cleanup | 4C2G5R | 2 |
| pipeline | web | Celery queue exporter | 4C2G5R | 1 |
| pipeline | node-timeout | node timeout scanner | 4C2G5R | 1 |
| pipeline | ai-notify | AI notify (keep 1 if unused) | 4C2G5R | 1 |

The descriptor no longer ships `v1-engine`. If the environment still has V1 engine tasks, add that process back or those queues will have no consumer.

## How to change instances

Pick one place as source of truth for an environment.

### 1. Change the repository baseline

Edit `plan` / `replicas` in `app_desc.yaml` and release. Use this for the default of new environments.

`default` web starts via `bin/start_web.sh`; `api` / `callback` web commands live in the descriptor. Keep gunicorn flags in sync.

### 2. Change one environment only

In PaaS **Application Engine → module → Processes**, change replicas or the resource plan. This usually scales immediately, without a code release.

Notes:

- Console changes apply to **that environment** and are not written back to Git.
- A later full deploy from the descriptor may overwrite the console, or keep existing env values. Check the process list after release.
- Keep `beat`, `node-timeout`, and pipeline `web` (exporter) at 1 replica. Extra `beat` replicas duplicate periodic tasks.

### 3. Tune gunicorn without changing replica count

`default` / `api` / `callback` web processes read these variables. Roll or redeploy the module after changing them:

| Variable | Default | Notes |
|---|---|---|
| `GUNICORN_WORKER_NUM` | `2` | Workers per Pod; **do not set to 1** |
| `GUNICORN_THREAD_NUM` | `10` | Threads per worker |
| `GUNICORN_MAX_REQUESTS` | `2000` | Recycle a worker after this many requests |
| `GUNICORN_MAX_REQUESTS_JITTER` | `200` | Jitter so workers do not recycle together |

Existing PaaS env vars are often **not** replaced by new yaml defaults. If the env still has `GUNICORN_WORKER_NUM=1` or `GUNICORN_MAX_REQUESTS=500`, change them in the console and roll.

## When to add replicas vs raise the plan

Look at queues and memory first. Do not scale every process to 5 replicas.

| Symptom | Touch first | Action |
|---|---|---|
| Gateway `create_task` / `start_task` / `get_task_status` returns a few-ms 502 with nginx 150-byte HTML | `api` web | Keep workers ≥ 2; then raise `replicas` from 2 to 3–5 |
| Slow UI, default web CPU saturated | default web | Add replicas; raise the plan if one Pod RSS nears 2Gi |
| Missing callbacks, callback 4xx/502 | callback web | Add replicas; keep workers ≥ 2 |
| API tasks queue up (`er_execute_api` / `er_schedule_api`) | `api-er-e` / `api-er-s` | Add replicas (`-c 100` each) |
| UI tasks queue up | `er-e` / `er-s` | Add replicas |
| Periodic backlog or peri worker RSS > 70% for a long time | `peri-er-e` / `peri-er-s` | Confirm the 2G plan, then add replicas |
| `default` queue backlog | dworker | Add replicas |
| Worker RSS pinned at the limit, repeated OOM | that process | **Raise `plan`** (1G→2G). Extra replicas will not fix per-process leak or render-pool memory |
| AI notify unused | ai-notify | Keep 1 |

Callers poll `get_task_status` heavily, so `api` web QPS is often an order of magnitude above create/start. Sizing from “tasks created” underestimates it.

## After a release

1. Web module argv shows `-w 2` (or your value) and `--max-requests-jitter`.
2. `Autorestarting worker` should not burst. At 2000, a medium-traffic pod recycles every few hours; hourly recycles usually mean the env is still at 500.
3. Web RSS around 300–700Mi with 2 workers is normal. If it sits near 2Gi, raise the plan or lower `GUNICORN_WORKER_NUM`.
4. For pipeline, watch RabbitMQ depth, not web QPS.
5. Do not scale the last consumer of a queue to 0.

## Relation to 502s

When a single gunicorn worker recycles, or a keepalive is stale, Ingress may return the default nginx 502 HTML in a few milliseconds. The request never reaches `create_task`.

Order of action:

1. Confirm `api` (and default / callback) `GUNICORN_WORKER_NUM≥2` with jitter.
2. Confirm `GUNICORN_MAX_REQUESTS` is not an aggressive 500.
3. If connect failures remain, add Ingress `proxy_next_upstream` for 502 (platform side, not this repo).
