# Mako package upgrade and deployment settings

Use `bamboo-pipeline==3.24.18`, which pins `bamboo-engine==2.6.7`. Do not override the engine dependency separately.

These are the currently released dependency versions. The explicit infrastructure-failure behavior described below requires a future engine release containing `RenderInfrastructureError`, a pipeline release pinning that engine, and deployment alongside this bk-sops `SystemObject` source fix. The versions above do not yet include that behavior. This change updates neither dependency versions nor default settings; packaging and publication are separate steps.

For the initial rollout, set:

```bash
BKAPP_SOPS_MAKO_IMPORT_MODULES=datetime,re,hashlib,random,time,os.path,config.mock.mock_json:json
BKAPP_SOPS_MAKO_WHITELIST_MODE=warn
BKAPP_MAKO_RENDER_BACKEND=inprocess
```

The import setting is a comma-separated replacement table, using `path` or `path:alias`. It defaults to empty. Merge any additional existing application imports into this value. Keep the original JSON wrapper mapping. Dangerous imports remain blocked; `os.path` is an allowed exception, while `os` is not.

Both engine versions filter dangerous paths before importing them, including file-access modules `io` / `_io` and network modules such as `http` and `urllib`, to avoid import side effects. Missing modules fail configuration loading. The legacy resolver only skips class paths confirmed to exist but unsupported by that resolver.

`warn` logs whitelist violations without enforcing them; `off` also disables these warnings. `.format()` is blocked only in `enforce`. Custom filters, `.format_map()` and dangerous attributes remain subject to unconditional checks. `inprocess` preserves in-process rendering; subprocess options are inactive with this backend.

Whitelist mode is trimmed and lowercased, then validated against `off`, `warn` and `enforce`. Empty or misspelled values fail configuration loading instead of silently disabling checks. When unset, the default remains `enforce`.

Apply the same environment to Web and all task-executing Celery/Worker processes and restart them with the release. Changing variables inside a WebConsole shell does not update running services.

## Settings binding

`config/default.py` binds import modules, shield words, whitelist mode and extra whitelist names to `BambooSettings`. Legacy pipeline reads imports from Django settings, while both engines share whitelist mode and backend selection. The import and whitelist environment variables are read through `env_v2.py` / `env_v3.py`; rendering options below are read directly in `config/default.py` for both PaaS versions. The engine does not automatically read environment variables or Django settings.

Each environment variable below maps to the engine setting obtained by removing `BKAPP_`:

| Environment variable | Default | Meaning |
| --- | --- | --- |
| `BKAPP_MAKO_RENDER_BACKEND` | `inprocess` | Set `subprocess` to enable the worker backend |
| `BKAPP_MAKO_RENDER_POOL_SIZE` | `4` | Pool capacity per host process, not per deployment |
| `BKAPP_MAKO_RENDER_MAX_USES` | `500` | Maximum requests per worker |
| `BKAPP_MAKO_RENDER_TIMEOUT` | `30` | Total request budget including queuing, startup and transport, in seconds |
| `BKAPP_MAKO_RENDER_FALLBACK_INPROCESS` | `0` | Allow host fallback for unsupported context/spec only |
| `BKAPP_MAKO_RENDER_OS_HARDEN` | `1` | Linux core, CPU and address-space restrictions |
| `BKAPP_MAKO_RENDER_NO_NETWORK` | `1` | Require a Linux network namespace |
| `BKAPP_MAKO_RENDER_RLIMIT_CPU` | `30` | Cumulative worker CPU seconds |
| `BKAPP_MAKO_RENDER_RLIMIT_AS_MB` | `1024` | Worker address-space limit, MB |
| `BKAPP_MAKO_RENDER_ENV_SCRUB_EXTRA` | empty | Additional environment-name fragments to scrub, comma-separated |

Boolean values accept `0/1` or `false/true`. Invalid boolean values or backend names fail configuration loading. Use positive numeric values. Only the initial three variables need explicit configuration for the first rollout. Retain the code defaults for shield words and the `_system` / `_loop` extra whitelist.

## Subsequent rollout

Whitelist enforcement and subprocess rendering are independent switches. Before enabling `enforce`, review expressions and class aliases: `datetime.datetime.now()` requires the `datetime.datetime` import entry; `datetime.date.today()` requires `datetime.date`. Restoring module names alone does not authorize every nested call.

Before setting `BKAPP_MAKO_RENDER_BACKEND=subprocess`, retain the default fallback/network/resource options and validate namespace permissions, Celery process behavior and real application contexts inside the target Linux container. Failure to establish the required network namespace prevents rendering; enabling in-process fallback does not bypass that failure. Passing in-process regression tests does not establish subprocess deployment readiness.

With the coordinated release, worker startup failures, admission or transport timeouts, worker exits, protocol errors and required network-isolation failures raise `RenderInfrastructureError` and explicitly fail the node. They no longer pass an unrendered expression onward as a successful result, and never trigger host rendering even when `FALLBACK_INPROCESS=1`.

The `SystemObject` fix preserves the pickle path `engine_pickle_obj.context.SystemObject`, its attribute dictionary and its string representation. Previously persisted pickles load after the fix and use the engine's existing structural adapter for worker transport, without unpickling the original application class inside the worker. Subclasses with inherited property behavior remain unsupported for portable transport.

Compatibility staging still supports explicitly setting `BKAPP_SOPS_MAKO_WHITELIST_MODE=warn`, `BKAPP_MAKO_RENDER_BACKEND=subprocess`, `BKAPP_MAKO_RENDER_FALLBACK_INPROCESS=1` and `BKAPP_MAKO_RENDER_NO_NETWORK=0`. Only unsupported context/spec values may fall back to host rendering, and a network namespace is not required in this configuration. This does not establish network-isolation readiness or change the defaults in the table above.

[简体中文](../../zh_hans/deploy/mako_render.md)
