# PaaS 进程规格与实例运维

多租户 / 企业版在蓝鲸 PaaS 上按 `app_desc.yaml` 拆成 `default`、`api`、`callback`、`pipeline` 四个模块。副本数、套餐和 gunicorn 参数都可以按环境调整，不必改业务代码。

社区版源码部署、上传打包见 [source_code_deploy.md](source_code_deploy.md)、[upload_pack_deploy.md](upload_pack_deploy.md)。本文只覆盖智能应用多模块进程。

## 规格怎么读

`app_desc.yaml` 里每个进程有两行：

```yaml
plan: 4C2G5R
replicas: 2
```

| 字段 | 含义 |
|---|---|
| `4C` | CPU **limit 4 核** |
| `2G` | 内存 **limit 2Gi** |
| `5R` | PaaS 套餐名后缀，**不是** 5 个实例 |
| `replicas` | 该进程的 Pod 数 |

`4C2G5R` × `replicas: 2` = 两个「4 核 2G」的实例。常见套餐还有 `4C1G5R`（1Gi）。PaaS 还会写很小的 request（常见 `100m` / `64Mi`），OOM 和可打满的上限看 limit。

## 仓库基线（当前描述文件）

| 模块 | 进程 | 作用 | 套餐 | 副本 |
|---|---|---|---|---|
| default | web | 页面、后台、管理接口 | 4C2G5R | 3 |
| default | beat | Celery 定时调度，全局只能 1 个 | 4C1G5R | 1 |
| default | dworker | `default` 队列 | 4C2G5R | 2 |
| api | web | 网关 create/start/status 等 | 4C2G5R | 2 |
| callback | web | 节点 / 插件回调 | 4C2G5R | 2 |
| pipeline | api-er-e / api-er-s | API 任务执行 / 调度 | 4C2G5R | 2 |
| pipeline | api-task | API 任务准备 | 4C1G5R | 2 |
| pipeline | er-e / er-s | 页面任务执行 / 调度 | 4C2G5R | 2 |
| pipeline | peri-er-e / peri-er-s | 周期任务执行 / 调度 | 4C2G5R | 2 |
| pipeline | cworker | 超时、重试、任务回调等 | 4C1G5R | 2 |
| pipeline | stats-worker | 统计 | 4C2G5R | 2 |
| pipeline | cleaner | 历史数据清理 | 4C2G5R | 2 |
| pipeline | web | Celery 队列导出 | 4C2G5R | 1 |
| pipeline | node-timeout | 节点超时扫描 | 4C2G5R | 1 |
| pipeline | ai-notify | AI 通知（未开放时可保持 1） | 4C2G5R | 1 |

描述文件不再默认部署 `v1-engine`。环境里还有 V1 引擎存量任务时，需要把该进程加回去，否则对应队列无人消费。

## 怎么改实例

按生效范围选一种，不要两处各改一版却对不上。

### 1. 改仓库基线（推荐作为默认值）

改 `app_desc.yaml` 对应模块的 `plan` / `replicas`，随版本发布。适用于「所有新环境都用这套默认值」。

`default` 的 Web 走 `bin/start_web.sh`；`api` / `callback` 的 Web 命令写在描述文件里。两边的 gunicorn 参数要一起改。

### 2. 只改某一个环境

在 PaaS「应用引擎 → 对应模块 → 进程」里改副本或资源方案，一般立刻扩缩容，不用发版。

注意：

- 控制台改的是**这个环境**，不会回写 Git。
- 下次用描述文件全量部署时，平台可能用仓库值覆盖控制台，也可能保留环境已有值。发布后对照进程列表，不要假设一定以 yaml 为准。
- `beat`、`node-timeout`、pipeline `web`（exporter）保持 1 副本。`beat` 多于 1 会重复投递周期任务。

### 3. 改 gunicorn，不改进程数

`default` / `api` / `callback` 的 Web 读这些环境变量，改完后**滚动或重新部署该模块**才生效：

| 变量 | 默认 | 说明 |
|---|---|---|
| `GUNICORN_WORKER_NUM` | `2` | 每个 Pod 的 worker 数，**不要设成 1** |
| `GUNICORN_THREAD_NUM` | `10` | 每个 worker 的线程数 |
| `GUNICORN_MAX_REQUESTS` | `2000` | 处理这么多请求后回收 worker，防内存缓涨 |
| `GUNICORN_MAX_REQUESTS_JITTER` | `200` | 回收抖动，避免多个 worker 同时退出 |

PaaS 里已经存在的环境变量，发布时**经常不会**被 yaml 新默认值覆盖。现场如果还是 `GUNICORN_WORKER_NUM=1` 或 `GUNICORN_MAX_REQUESTS=500`，要在控制台改掉再滚动。

## 什么时候加副本、什么时候加规格

先看队列和内存，不要先把所有进程都加成 5 副本。

| 现象 | 先动谁 | 怎么动 |
|---|---|---|
| 网关 `create_task` / `start_task` / `get_task_status` 偶发数毫秒级 502，响应是 nginx 的 150 字节 HTML | `api` web | worker 先保证 ≥ 2；仍不够再把 `replicas` 从 2 加到 3～5 |
| 页面打开慢、default web CPU 打满 | default web | 加副本；单 Pod RSS 接近 2Gi 再升套餐 |
| 回调丢失、callback 4xx/502 | callback web | 加副本；保持 worker ≥ 2 |
| API 任务排队久、`er_execute_api` / `er_schedule_api` 堆积 | `api-er-e` / `api-er-s` | 加副本（每副本 `-c 100`） |
| 页面任务排队 | `er-e` / `er-s` | 加副本 |
| 周期任务堆积或 peri worker RSS 长期 > 70% | `peri-er-e` / `peri-er-s` | 先确认是 2G 套餐，再加副本 |
| `default` 队列堆积 | dworker | 加副本 |
| 某 worker RSS 顶满 limit、反复 OOM | 对应进程 | **升 `plan`**（1G→2G），只加副本解决不了单进程泄漏或渲染池占内存 |
| AI 通知未使用 | ai-notify | 保持 1，不必加 |

`get_task_status` 会被调用方高频轮询，`api` web 的 QPS 往往比 create/start 高一个数量级。按「创建任务数」估副本会偏小。

## 发布后核对

1. 三个 Web 模块的启动参数里是 `-w 2`（或你设的值），且带 `--max-requests-jitter`。
2. gunicorn 日志里的 `Autorestarting worker` 不要在短时间成片出现。2000 量级时，中等流量大约数小时回收一次；若仍约每小时一次，说明环境变量还是 500。
3. `kubectl top` 或监控里，Web RSS 大约 300～700Mi（2 worker）属正常；长期贴近 2Gi 再升套餐或降 `GUNICORN_WORKER_NUM`。
4. pipeline 看 RabbitMQ 队列深度，不要看 Web QPS。
5. 不要把某个队列的最后一个消费者副本收到 0。

## 和 502 的关系

Ingress 在 gunicorn 单 worker 回收、或过期 keepalive 时，会直接回 nginx 默认 502 HTML，`backend_duration` 只有几毫秒，请求进不了 `create_task` 业务代码。

处理顺序：

1. 确认 `api`（以及 default / callback）`GUNICORN_WORKER_NUM≥2` 且有 jitter。
2. 确认 `GUNICORN_MAX_REQUESTS` 不是过勤的 500。
3. 仍有连接失败再在 Ingress 上对 502 做 `proxy_next_upstream`（平台侧，不在本仓库）。
