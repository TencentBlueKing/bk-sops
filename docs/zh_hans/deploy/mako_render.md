# Mako 依赖升级与部署配置

对应 `bamboo-pipeline==3.24.19`，其包依赖已固定 `bamboo-engine==2.6.8`，无需另外覆盖 engine 版本。

以上依赖已发布到 PyPI，并包含下述通过 `RenderInfrastructureError` 显式报告基础设施故障的行为。部署时需同时更新应用依赖和本次 bk-sops `SystemObject` 源码修复，以完整接入故障处理和系统上下文传输修复。默认配置保持不变。

## 首次发布

按先发布、再回归的安排，在部署平台配置以下环境变量。下面的导入表恢复原有默认模块；若现网还配置了其他业务模块，需合并到同一个值中。

```bash
BKAPP_SOPS_MAKO_IMPORT_MODULES=datetime,re,hashlib,random,time,os.path,config.mock.mock_json:json
BKAPP_SOPS_MAKO_WHITELIST_MODE=warn
BKAPP_MAKO_RENDER_BACKEND=inprocess
```

- 导入表是**逗号分隔字符串**，格式为 `path` 或 `path:alias`，会替换整张表，未配置则为空。`config.mock.mock_json:json` 保留原有 JSON 包装模块。危险模块仍会被拒绝，`os.path` 是允许的例外，不能换成 `os`。
- 新旧引擎均在导入前过滤危险路径，包括 `io` / `_io` 文件访问模块以及 `http`、`urllib` 等网络模块，避免先导入再拒绝造成副作用。缺失模块会使配置加载失败；旧引擎仅跳过已确认存在、但不支持导入的类路径。
- `warn` 延后白名单阻断并记录命中；`.format()` 只在 `enforce` 下拒绝。`off` 同样放行 `.format()`，但不记录白名单告警。自定义 filter、`.format_map()`、危险属性等无条件限制不受该开关控制。
- 白名单模式去除首尾空格并转成小写，仅接受 `off` / `warn` / `enforce`；空值或拼写错误会使配置加载失败，避免静默关闭检查。未配置时仍默认为 `enforce`。
- `inprocess` 是默认值，保持进程内渲染。此时子进程池、超时、资源及网络隔离参数不参与渲染。
- 将相同配置下发到 Web 和所有执行任务的 Celery/Worker 进程，随版本发布重启。只在 WebConsole 当前 shell 中修改变量，不会更新已经运行的服务进程。

## config/default.py 中的绑定

该文件把 `MAKO_SANDBOX_IMPORT_MODULES`、`MAKO_SANDBOX_SHIELD_WORDS`、`MAKO_TEMPLATE_NAME_WHITELIST_MODE`、`MAKO_TEMPLATE_NAME_EXTRA_WHITELIST` 同步到 `BambooSettings`。legacy pipeline 的导入表从 Django settings 读取，白名单模式与渲染后端共用引擎设置。

`BKAPP_SOPS_MAKO_IMPORT_MODULES` 和 `BKAPP_SOPS_MAKO_WHITELIST_MODE` 由 `env_v2.py` / `env_v3.py` 读取；下面的隔离选项在 `config/default.py` 中统一读取，V2/V3 均生效。引擎不会自行读取这些环境变量，仅添加 Django 同名配置也不会自动同步给引擎。

| 环境变量 | 默认值 | 引擎配置及作用 |
| --- | --- | --- |
| `BKAPP_MAKO_RENDER_BACKEND` | `inprocess` | `MAKO_RENDER_BACKEND`；`subprocess` 才开启隔离后端 |
| `BKAPP_MAKO_RENDER_POOL_SIZE` | `4` | `MAKO_RENDER_POOL_SIZE`；每个宿主进程的池容量，非整个部署的总数 |
| `BKAPP_MAKO_RENDER_MAX_USES` | `500` | `MAKO_RENDER_MAX_USES`；每个 worker 复用次数 |
| `BKAPP_MAKO_RENDER_TIMEOUT` | `30` | `MAKO_RENDER_TIMEOUT`；单次请求含排队、启动和通信的总预算，秒 |
| `BKAPP_MAKO_RENDER_FALLBACK_INPROCESS` | `0` | `MAKO_RENDER_FALLBACK_INPROCESS`；是否允许不支持的 context/spec 在宿主回退 |
| `BKAPP_MAKO_RENDER_OS_HARDEN` | `1` | `MAKO_RENDER_OS_HARDEN`；Linux core/CPU/地址空间限制 |
| `BKAPP_MAKO_RENDER_NO_NETWORK` | `1` | `MAKO_RENDER_NO_NETWORK`；强制 Linux network namespace |
| `BKAPP_MAKO_RENDER_RLIMIT_CPU` | `30` | `MAKO_RENDER_RLIMIT_CPU`；worker 累计 CPU 秒数 |
| `BKAPP_MAKO_RENDER_RLIMIT_AS_MB` | `1024` | `MAKO_RENDER_RLIMIT_AS_MB`；worker 地址空间上限，MB |
| `BKAPP_MAKO_RENDER_ENV_SCRUB_EXTRA` | 空 | `MAKO_RENDER_ENV_SCRUB_EXTRA`；额外清理的环境变量名片段，逗号分隔 |

布尔项接受 `0/1` 或 `false/true`；后端名或布尔值拼写错误会使配置加载失败。数值项使用正数。首发只需前述三个变量，其余保留默认即可。屏蔽词和 `_system` / `_loop` 白名单保留代码默认值，无需另配环境变量。

## 后续灰度

白名单与子进程隔离是两个独立开关，可分别回归。切换 `enforce` 前需检查业务表达式及导入别名：例如 `datetime.datetime.now()` 需要在导入表中补 `datetime.datetime`，`datetime.date.today()` 需要补 `datetime.date`；恢复模块名本身不代表所有多级调用都会放行。

切换 `BKAPP_MAKO_RENDER_BACKEND=subprocess` 时，建议保持 `FALLBACK_INPROCESS=0`、`OS_HARDEN=1`、`NO_NETWORK=1`（均指上表完整变量名），先在目标 Linux 容器验证网络命名空间权限、Celery 进程模型和真实业务 context。无网络隔离建立失败时会拒绝渲染；开启进程内回退也不会绕过这种失败。不能把进程内路径回归通过等同于子进程隔离验收。

使用上述配套版本时，worker 启动、排队或通信超时、进程退出、协议异常及必需的网络隔离建立失败会通过 `RenderInfrastructureError` 显式使节点失败，不再把未渲染的表达式作为成功结果继续执行；即使 `FALLBACK_INPROCESS=1`，这些基础设施故障也不会回退到宿主渲染。

本次 `SystemObject` 修复保留 `engine_pickle_obj.context.SystemObject` 的 pickle 路径、属性字典及字符串表现。旧版本持久化的 pickle 可在修复后加载，并经引擎现有结构适配器传输给 worker，无需在 worker 中反序列化原应用类。继承属性行为的子类仍不属于可传输的普通属性对象。

兼容灰度仍支持显式配置 `BKAPP_SOPS_MAKO_WHITELIST_MODE=warn`、`BKAPP_MAKO_RENDER_BACKEND=subprocess`、`BKAPP_MAKO_RENDER_FALLBACK_INPROCESS=1`、`BKAPP_MAKO_RENDER_NO_NETWORK=0`。此时仅不支持的 context/spec 可走宿主回退，且不要求网络命名空间；这不等于无网络隔离验收，也不改变上表默认值。

[English](../../en/deploy/mako_render.md)
