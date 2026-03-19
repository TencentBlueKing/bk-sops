# Celery Threads 模式内存泄露修复方案

## 问题分析

在 `app_desc.yaml` 中，所有 celery worker 都使用了 `-P threads` 模式。该模式下：
- ❌ `--max-tasks-per-child` **不生效**（只对 prefork 模式有效）
- ✅ 必须通过重启**整个进程**来释放内存
- ✅ 需要使用其他机制触发进程重启

## 有效解决方案

### 方案 1：使用 --max-memory-per-child（推荐）⭐

监控整个进程的内存使用，超过阈值后自动重启进程。

**修改前：**
```yaml
command: celery worker -A blueapps.core.celery -P threads -Q er_execute_api -n api_er_e_worker@%h -c 100 -l info
```

**修改后：**
```yaml
command: celery worker -A blueapps.core.celery -P threads -Q er_execute_api -n api_er_e_worker@%h -c 100 -l info --max-memory-per-child 524288
```

**参数说明：**
- 单位：KB（千字节）
- `524288` = 512MB
- `1048576` = 1GB
- `2097152` = 2GB

**推荐配置：**
```yaml
# 高并发 worker (c=100, plan: 4C1G)
--max-memory-per-child 819200   # 800MB，留20%缓冲

# 高并发 worker (c=100, plan: 4C2G)
--max-memory-per-child 1638400  # 1.6GB，留20%缓冲

# 中等并发 worker (c=50, plan: 4C1G)
--max-memory-per-child 819200   # 800MB

# 低并发 worker (c=6-10, plan: 4C1G)
--max-memory-per-child 819200   # 800MB

# default worker (c=10, plan: 4C2G)
--max-memory-per-child 1638400  # 1.6GB
```

### 方案 2：使用环境变量配置时间限制重启

通过环境变量添加 Celery 配置，让 worker 定期重启。

**在 app_desc.yaml 的 env_variables 中添加：**

```yaml
env_variables:
    # ... 其他环境变量 ...

    # Celery Worker 自动重启配置（防止内存泄露）
    - key: CELERYD_MAX_TASKS_PER_CHILD
      value: 0
      description: threads模式下此参数无效，设为0

    - key: CELERYD_WORKER_MAX_MEMORY_PER_CHILD
      value: 524288
      description: Worker内存超过512MB后重启（单位KB）

    - key: CELERY_WORKER_PREFETCH_MULTIPLIER
      value: 4
      description: 预取倍数，减少内存占用

    - key: CELERY_ACKS_LATE
      value: "True"
      description: 任务完成后才确认，配合内存限制使用
```

### 方案 3：在 config/default.py 中添加全局配置

在 Django 配置文件中添加 Celery 内存管理配置：

```python
# config/default.py

# Celery Worker 内存管理配置（针对 threads 模式）
# 注意：CELERYD_MAX_TASKS_PER_CHILD 在 threads 模式下不生效
# 使用内存限制来触发 worker 重启
CELERYD_WORKER_MAX_MEMORY_PER_CHILD = 524288  # 512MB，单位KB

# 优化内存使用的其他配置
CELERY_WORKER_PREFETCH_MULTIPLIER = 4  # 减少预取任务数
CELERY_ACKS_LATE = True  # 任务完成后才确认
CELERY_RESULT_EXPIRES = 3600  # 结果1小时后过期
CELERY_TASK_IGNORE_RESULT = False  # 如果不需要结果，可设为 True
CELERY_RESULT_BACKEND_MAX_RETRIES = 3

# 连接池管理
BROKER_POOL_LIMIT = 10  # 已配置
BROKER_CONNECTION_MAX_RETRIES = 5

# 序列化配置优化
CELERY_TASK_COMPRESSION = 'gzip'  # 压缩任务数据
CELERY_RESULT_COMPRESSION = 'gzip'  # 压缩结果数据
```

### 方案 4：使用启动脚本定期重启（最保险）

创建一个包装脚本，让 worker 运行一定时间后自动退出并重启。

**创建文件 `bin/celery_with_restart.sh`：**

```bash
#!/bin/bash
# Celery worker 定期重启包装脚本
# 使用方法：./celery_with_restart.sh <celery_args>

# 运行时长（秒），例如 12 小时 = 43200 秒
RESTART_INTERVAL=${CELERY_RESTART_INTERVAL:-43200}

while true; do
    echo "[$(date)] Starting celery worker..."

    # 启动 celery worker 并获取 PID
    celery "$@" &
    WORKER_PID=$!

    # 等待指定时间
    sleep $RESTART_INTERVAL

    # 优雅关闭 worker
    echo "[$(date)] Gracefully stopping worker (PID: $WORKER_PID)..."
    kill -TERM $WORKER_PID

    # 等待 worker 完成当前任务
    wait $WORKER_PID

    echo "[$(date)] Worker stopped, restarting..."
    sleep 5
done
```

**修改 app_desc.yaml 使用脚本：**

```yaml
processes:
    api-er-e:
        command: bash bin/celery_with_restart.sh worker -A blueapps.core.celery -P threads -Q er_execute_api -n api_er_e_worker@%h -c 100 -l info
        plan: 4C1G5R
        replicas: 4
```

**添加环境变量控制重启间隔：**

```yaml
env_variables:
    - key: CELERY_RESTART_INTERVAL
      value: 43200
      description: Celery worker 重启间隔（秒），12小时=43200
```

## 完整的 app_desc.yaml 修改示例

### 对于 default 模块的 dworker

```yaml
dworker:
    command: python manage.py celery worker -Q default -n default@%h -P threads -c 10 -l info --max-memory-per-child 1638400
    plan: 4C2G5R
    replicas: 5
```

### 对于 pipeline 模块的各个 worker

```yaml
# 高并发 worker (c=100, plan: 4C1G5R)
v1-engine:
    command: celery worker -A blueapps.core.celery -P threads -Q api_task_queue_pipeline_priority,api_task_queue_service_schedule_priority,periodic_task_queue_pipeline_priority,periodic_task_queue_service_schedule_priority,pipeline,pipeline_priority,service_schedule,service_schedule_priority -n v1_engine@%h -c 100 -l info --max-memory-per-child 819200
    plan: 4C1G5R
    replicas: 2

api-er-e:
    command: celery worker -A blueapps.core.celery -P threads -Q er_execute_api -n api_er_e_worker@%h -c 100 -l info --max-memory-per-child 819200
    plan: 4C1G5R
    replicas: 4

api-er-s:
    command: celery worker -A blueapps.core.celery -P threads -Q er_schedule_api -n api_er_s_worker@%h -c 100 -l info --max-memory-per-child 819200
    plan: 4C1G5R
    replicas: 4

# 中等并发 worker (c=50)
api-task:
    command: celery worker -A blueapps.core.celery -P threads -Q task_prepare_api -n api_task_worker@%h -c 50 -l info --max-memory-per-child 819200
    plan: 4C1G5R
    replicas: 2

# 低并发 worker (c=6)
cworker:
    command: celery worker -A blueapps.core.celery -P threads -Q pipeline_additional_task,pipeline_additional_task_priority,node_auto_retry,timeout_node_execute,timeout_nodes_record,task_callback -n common_worker@%h -c 6 -l info --max-memory-per-child 819200
    plan: 4C1G5R
    replicas: 2

# 高内存 worker (c=100, plan: 4C2G5R)
er-e:
    command: celery worker -A blueapps.core.celery -P threads -Q er_execute -n er_e_worker@%h -c 100 -l info --max-memory-per-child 1638400
    plan: 4C2G5R
    replicas: 2

er-s:
    command: celery worker -A blueapps.core.celery -P threads -Q er_schedule -n er_s_worker@%h -c 100 -l info --max-memory-per-child 1638400
    plan: 4C2G5R
    replicas: 2

peri-er-e:
    command: celery worker -A blueapps.core.celery -P threads -Q er_execute_periodic_task -n peri_er_e_worker@%h -c 100 -l info --max-memory-per-child 819200
    plan: 4C1G5R
    replicas: 2

peri-er-s:
    command: celery worker -A blueapps.core.celery -P threads -Q er_schedule_periodic_task -n peri_er_s_worker@%h -c 100 -l info --max-memory-per-child 819200
    plan: 4C1G5R
    replicas: 2

stats-worker:
    command: celery worker -A blueapps.core.celery -P threads -Q pipeline_statistics_priority -n default@%h -c 100 -l info --max-memory-per-child 819200
    plan: 4C1G5R
    replicas: 2

cleaner:
    command: celery worker -A blueapps.core.celery -P threads -Q task_data_clean -n cleaner_worker@%h -c 100 -l info --max-memory-per-child 819200
    plan: 4C1G5R
    replicas: 2
```

## 推荐实施步骤

1. **第一步：添加内存限制参数（立即生效）**
   - 在所有 celery worker 命令中添加 `--max-memory-per-child` 参数
   - 根据 plan 配置设置合适的内存阈值

2. **第二步：优化 Celery 配置（减少内存占用）**
   - 在 `config/default.py` 中添加内存优化配置
   - 设置合理的结果过期时间
   - 调整预取倍数

3. **第三步：监控和调优**
   - 部署后观察内存使用情况
   - 根据实际情况调整 `--max-memory-per-child` 的值
   - 确保重启频率合理（不要太频繁影响性能）

4. **第四步（可选）：代码层面优化**
   - 检查任务代码，确保正确释放资源
   - 使用上下文管理器管理文件、连接等资源
   - 避免在任务中缓存大对象

## 验证方法

### 1. 查看 worker 日志

worker 重启时会有日志：
```
[2025-10-20 10:30:15] Warm shutdown (MainProcess)
[2025-10-20 10:30:16] Process 'Worker-1' restarted (exceeded maximum memory per child)
```

### 2. 监控内存使用

```python
# 在任务中添加内存监控
import psutil
import os

@app.task
def my_task():
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / 1024 / 1024
    logger.info(f"Current memory usage: {mem_mb:.2f} MB")
    # ... 任务逻辑
```

### 3. 使用监控工具

- Prometheus + Grafana 监控内存趋势
- 查看 worker 重启频率
- 观察内存是否持续增长

## 注意事项

1. **内存阈值设置**
   - 不要设置太低，避免频繁重启影响性能
   - 建议设置为容器内存的 70-80%
   - 例如：1GB 容器设置为 800MB

2. **优雅关闭**
   - worker 重启时会等待当前任务完成
   - 确保任务有合理的超时设置
   - 避免长时间运行的任务被强制中断

3. **结合使用多种方案**
   - 主要使用 `--max-memory-per-child`
   - 配合 Celery 配置优化
   - 必要时使用定时重启脚本作为兜底

## 参考资料

- [Celery Worker Configuration](https://docs.celeryproject.org/en/stable/userguide/workers.html)
- [Celery Memory Management](https://docs.celeryproject.org/en/stable/userguide/configuration.html#worker-max-memory-per-child)
- [Debugging Memory Issues](https://docs.celeryproject.org/en/stable/userguide/debugging.html)

