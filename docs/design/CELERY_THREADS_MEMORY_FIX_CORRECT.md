# Celery Threads 模式内存泄露修复方案（更正版）

## 重要声明 ⚠️

经过验证，以下参数**在 threads 模式下均不生效**：
- ❌ `--max-tasks-per-child` (仅支持 prefork 模式)
- ❌ `--max-memory-per-child` (仅支持 prefork 模式)

这两个参数都是为多进程 (prefork) 模式设计的，在 threads 模式下**完全无效**。

## 为什么不切换到 prefork 模式？

threads 模式的优势：
- ✅ 更低的内存占用（进程间不复制内存）
- ✅ 更适合 I/O 密集型任务
- ✅ 线程间通信更快
- ✅ 适合需要共享状态的场景

但缺点是：
- ❌ 无法利用 Celery 内置的内存限制重启机制
- ❌ 受 Python GIL 限制（CPU 密集型任务性能差）

## 真正有效的解决方案

### 方案 1：使用 Supervisor/Systemd 定时重启 ⭐⭐⭐⭐⭐

**这是 threads 模式下最可靠的方案**

#### 方案 1.1：使用自定义重启脚本

创建一个包装脚本，定时重启 worker 进程。

**步骤 1：创建重启脚本**

```bash
# bin/celery_auto_restart.sh
#!/bin/bash
set -e

# 从环境变量读取重启间隔（秒），默认 12 小时
RESTART_INTERVAL=${CELERY_RESTART_INTERVAL:-43200}

# 获取 celery 命令参数
CELERY_ARGS="$@"

echo "[$(date)] Celery auto-restart wrapper started"
echo "[$(date)] Restart interval: ${RESTART_INTERVAL} seconds"
echo "[$(date)] Celery args: ${CELERY_ARGS}"

while true; do
    echo "[$(date)] Starting celery worker..."

    # 使用 timeout 命令限制运行时间
    # --foreground: 前台运行，确保信号传递
    # --kill-after=30: 如果 TERM 信号无效，30秒后强制 KILL
    timeout --foreground --kill-after=30 ${RESTART_INTERVAL}s \
        celery ${CELERY_ARGS} || true

    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 124 ]; then
        # 124 是 timeout 的正常退出码
        echo "[$(date)] Worker reached restart interval, restarting..."
    elif [ $EXIT_CODE -eq 0 ]; then
        echo "[$(date)] Worker exited normally, restarting..."
    else
        echo "[$(date)] Worker exited with error code $EXIT_CODE, waiting 10s before restart..."
        sleep 10
    fi

    # 短暂延迟，避免频繁重启
    sleep 2
done
```

**步骤 2：修改 app_desc.yaml**

```yaml
modules:
    pipeline:
        env_variables:
            # 添加重启间隔配置（秒）
            - key: CELERY_RESTART_INTERVAL
              value: 43200  # 12小时
              description: Celery worker 自动重启间隔（秒）

        processes:
            v1-engine:
                command: bash bin/celery_auto_restart.sh worker -A blueapps.core.celery -P threads -Q api_task_queue_pipeline_priority,api_task_queue_service_schedule_priority,periodic_task_queue_pipeline_priority,periodic_task_queue_service_schedule_priority,pipeline,pipeline_priority,service_schedule,service_schedule_priority -n v1_engine@%h -c 100 -l info
                plan: 4C1G5R
                replicas: 2

            api-er-e:
                command: bash bin/celery_auto_restart.sh worker -A blueapps.core.celery -P threads -Q er_execute_api -n api_er_e_worker@%h -c 100 -l info
                plan: 4C1G5R
                replicas: 4

            # ... 其他 worker 类似修改
```

**优点：**
- ✅ 保证定时重启，防止内存持续增长
- ✅ 优雅重启，不会丢失任务
- ✅ 简单可靠，易于维护
- ✅ 可以通过环境变量灵活调整重启间隔

#### 方案 1.2：改进版脚本（带内存监控）

```bash
# bin/celery_auto_restart_with_monitor.sh
#!/bin/bash
set -e

RESTART_INTERVAL=${CELERY_RESTART_INTERVAL:-43200}
MAX_MEMORY_MB=${CELERY_MAX_MEMORY_MB:-1024}  # 默认 1GB
CHECK_INTERVAL=${CELERY_MEMORY_CHECK_INTERVAL:-60}  # 默认每60秒检查一次

CELERY_ARGS="$@"

echo "[$(date)] Celery auto-restart wrapper with memory monitor started"
echo "[$(date)] Restart interval: ${RESTART_INTERVAL} seconds"
echo "[$(date)] Max memory: ${MAX_MEMORY_MB} MB"
echo "[$(date)] Memory check interval: ${CHECK_INTERVAL} seconds"

while true; do
    echo "[$(date)] Starting celery worker..."

    # 启动 celery worker 在后台
    celery ${CELERY_ARGS} &
    WORKER_PID=$!

    echo "[$(date)] Worker started with PID: ${WORKER_PID}"

    # 记录启动时间
    START_TIME=$(date +%s)

    # 监控循环
    while kill -0 $WORKER_PID 2>/dev/null; do
        CURRENT_TIME=$(date +%s)
        ELAPSED=$((CURRENT_TIME - START_TIME))

        # 检查是否达到重启间隔
        if [ $ELAPSED -ge $RESTART_INTERVAL ]; then
            echo "[$(date)] Reached restart interval (${ELAPSED}s), restarting worker..."
            kill -TERM $WORKER_PID
            break
        fi

        # 检查内存使用
        if command -v ps &> /dev/null; then
            # 获取进程内存使用（RSS，单位 KB）
            MEM_KB=$(ps -o rss= -p $WORKER_PID 2>/dev/null || echo "0")
            MEM_MB=$((MEM_KB / 1024))

            if [ $MEM_MB -gt $MAX_MEMORY_MB ]; then
                echo "[$(date)] Memory usage ($MEM_MB MB) exceeded limit ($MAX_MEMORY_MB MB), restarting worker..."
                kill -TERM $WORKER_PID
                break
            fi

            # 每10次检查输出一次内存信息
            if [ $((ELAPSED % (CHECK_INTERVAL * 10))) -eq 0 ]; then
                echo "[$(date)] Worker memory: ${MEM_MB} MB, uptime: ${ELAPSED}s"
            fi
        fi

        sleep $CHECK_INTERVAL
    done

    # 等待 worker 完全退出
    wait $WORKER_PID 2>/dev/null || true

    echo "[$(date)] Worker stopped, restarting in 5 seconds..."
    sleep 5
done
```

**配置：**

```yaml
env_variables:
    - key: CELERY_RESTART_INTERVAL
      value: 43200
      description: 定时重启间隔（秒），12小时

    - key: CELERY_MAX_MEMORY_MB
      value: 800
      description: 内存上限（MB），超过后触发重启

    - key: CELERY_MEMORY_CHECK_INTERVAL
      value: 60
      description: 内存检查间隔（秒）
```

### 方案 2：使用 Python 脚本监控并重启 ⭐⭐⭐⭐

在应用代码中实现内存监控和自动重启。

**创建监控模块：**

```python
# gcloud/celery_monitor.py
import os
import sys
import time
import psutil
import logging
from celery import signals

logger = logging.getLogger(__name__)

# 从环境变量读取配置
MAX_MEMORY_MB = int(os.getenv('CELERY_MAX_MEMORY_MB', 1024))
MAX_TASKS = int(os.getenv('CELERY_MAX_TASKS_BEFORE_CHECK', 100))
CHECK_AFTER_N_TASKS = int(os.getenv('CELERY_CHECK_AFTER_N_TASKS', 50))

# 全局计数器
task_counter = 0


@signals.task_postrun.connect
def check_memory_after_task(sender=None, **kwargs):
    """任务执行后检查内存使用"""
    global task_counter
    task_counter += 1

    # 每执行 N 个任务检查一次内存
    if task_counter % CHECK_AFTER_N_TASKS != 0:
        return

    try:
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024

        logger.info(f"[Memory Monitor] PID: {os.getpid()}, "
                   f"Tasks: {task_counter}, "
                   f"Memory: {memory_mb:.2f} MB / {MAX_MEMORY_MB} MB")

        if memory_mb > MAX_MEMORY_MB:
            logger.warning(f"[Memory Monitor] Memory limit exceeded! "
                         f"{memory_mb:.2f} MB > {MAX_MEMORY_MB} MB")
            logger.warning(f"[Memory Monitor] Triggering worker restart...")

            # 优雅退出，让进程管理器重启
            # 使用 SIGTERM 信号让 celery 优雅关闭
            os.kill(os.getpid(), 15)  # SIGTERM

    except Exception as e:
        logger.error(f"[Memory Monitor] Error checking memory: {e}")


@signals.worker_ready.connect
def worker_ready(**kwargs):
    """Worker 启动时记录信息"""
    try:
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        logger.info(f"[Memory Monitor] Worker ready. "
                   f"PID: {os.getpid()}, "
                   f"Initial memory: {memory_mb:.2f} MB, "
                   f"Limit: {MAX_MEMORY_MB} MB")
    except Exception as e:
        logger.error(f"[Memory Monitor] Error in worker_ready: {e}")


@signals.worker_shutdown.connect
def worker_shutdown(**kwargs):
    """Worker 关闭时记录信息"""
    global task_counter
    try:
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        logger.info(f"[Memory Monitor] Worker shutting down. "
                   f"PID: {os.getpid()}, "
                   f"Total tasks: {task_counter}, "
                   f"Final memory: {memory_mb:.2f} MB")
    except Exception as e:
        logger.error(f"[Memory Monitor] Error in worker_shutdown: {e}")
```

**在 Celery app 配置中导入：**

```python
# config/default.py 或 blueapps/core/celery.py

# 导入内存监控模块（会自动注册信号处理器）
try:
    import gcloud.celery_monitor
    logger.info("Celery memory monitor enabled")
except ImportError as e:
    logger.warning(f"Failed to import celery memory monitor: {e}")
```

**添加依赖：**

```bash
# requirements.txt
psutil>=5.8.0
```

**配置环境变量：**

```yaml
env_variables:
    - key: CELERY_MAX_MEMORY_MB
      value: 800
      description: Worker 内存上限（MB），超过后自动退出重启

    - key: CELERY_CHECK_AFTER_N_TASKS
      value: 50
      description: 每执行多少个任务检查一次内存
```

**优点：**
- ✅ 在应用层面精确控制
- ✅ 可以记录详细的内存使用日志
- ✅ 灵活的检查策略
- ✅ 依赖容器编排自动重启

### 方案 3：优化代码减少内存泄露 ⭐⭐⭐⭐⭐

**最根本的解决方案是找出并修复内存泄露的源头**

#### 3.1 常见内存泄露原因

```python
# ❌ 错误示例 1：全局变量累积
GLOBAL_CACHE = {}  # 永远不清理，会一直增长

@app.task
def bad_task():
    GLOBAL_CACHE[uuid.uuid4()] = large_data  # 内存泄露！

# ✅ 正确做法：使用 Redis 或限制大小
from cachetools import TTLCache

task_cache = TTLCache(maxsize=1000, ttl=3600)  # 限制大小和过期时间

@app.task
def good_task():
    task_cache[task_id] = data


# ❌ 错误示例 2：未关闭的数据库连接
@app.task
def bad_db_task():
    conn = get_db_connection()
    # 忘记关闭
    return conn.query()

# ✅ 正确做法：使用上下文管理器
@app.task
def good_db_task():
    with get_db_connection() as conn:
        return conn.query()


# ❌ 错误示例 3：大对象保留引用
@app.task
def bad_large_data_task():
    large_data = load_large_file()
    process_data(large_data)
    # large_data 在函数结束前一直占用内存
    return "done"

# ✅ 正确做法：及时释放
@app.task
def good_large_data_task():
    large_data = load_large_file()
    result = process_data(large_data)
    del large_data  # 显式删除
    import gc
    gc.collect()  # 强制垃圾回收
    return result


# ❌ 错误示例 4：循环引用
class Task:
    def __init__(self):
        self.callback = lambda: self.process()  # 循环引用

# ✅ 正确做法：使用弱引用
import weakref

class Task:
    def __init__(self):
        self_ref = weakref.ref(self)
        self.callback = lambda: self_ref().process() if self_ref() else None
```

#### 3.2 内存泄露检测工具

```python
# 在任务中添加内存分析
import tracemalloc
import psutil
import os

@app.task
def memory_intensive_task():
    # 开始跟踪
    tracemalloc.start()
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / 1024 / 1024

    try:
        # 执行任务
        result = do_work()

        # 检查内存增长
        mem_after = process.memory_info().rss / 1024 / 1024
        mem_increase = mem_after - mem_before

        # 获取内存占用最多的代码位置
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')

        logger.info(f"Memory increase: {mem_increase:.2f} MB")
        logger.info("Top 10 memory consumers:")
        for stat in top_stats[:10]:
            logger.info(stat)

        return result

    finally:
        tracemalloc.stop()
```

### 方案 4：Celery 配置优化 ⭐⭐⭐

在 `config/default.py` 中添加优化配置：

```python
# config/default.py

# ===== Celery 内存优化配置 =====

# 1. 任务结果后端优化
CELERY_RESULT_BACKEND = 'redis://...'
CELERY_RESULT_EXPIRES = 3600  # 结果1小时后过期，及时清理
CELERY_RESULT_BACKEND_MAX_RETRIES = 3
CELERY_RESULT_PERSISTENT = False  # 不持久化结果（如果不需要）

# 2. 如果不需要结果，可以禁用
CELERY_TASK_IGNORE_RESULT = False  # 根据需求设置
CELERY_TASK_STORE_ERRORS_EVEN_IF_IGNORED = True

# 3. 任务序列化优化
CELERY_TASK_SERIALIZER = 'pickle'  # 或 'json'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ['pickle', 'json']
CELERY_TASK_COMPRESSION = 'gzip'  # 压缩大任务
CELERY_RESULT_COMPRESSION = 'gzip'

# 4. 预取优化（减少内存中的任务数）
CELERY_WORKER_PREFETCH_MULTIPLIER = 4  # 默认是4，可以设置为1-2
CELERYD_PREFETCH_MULTIPLIER = 4

# 5. 任务确认优化
CELERY_ACKS_LATE = True  # 任务完成后才确认
CELERY_REJECT_ON_WORKER_LOST = True  # Worker 丢失时拒绝任务

# 6. Broker 连接池优化
BROKER_POOL_LIMIT = 10  # 已有配置
BROKER_CONNECTION_MAX_RETRIES = 5
BROKER_CONNECTION_TIMEOUT = 10

# 7. 禁用不需要的功能
CELERY_SEND_EVENTS = False  # 如果不需要事件监控
CELERY_SEND_TASK_SENT_EVENT = False

# 8. 任务超时设置
CELERYD_TASK_TIME_LIMIT = 3600  # 任务硬超时：1小时
CELERYD_TASK_SOFT_TIME_LIMIT = 3300  # 任务软超时：55分钟

# 9. 内存和性能相关
CELERYD_MAX_TASKS_PER_CHILD = 0  # threads 模式下无效，设为 0
CELERYD_WORKER_LOST_WAIT = 10  # Worker 丢失等待时间
```

## 完整实施方案推荐

### 推荐组合：方案 1.2 + 方案 2 + 方案 3 + 方案 4

1. **使用带内存监控的重启脚本**（方案 1.2）
   - 保证最多 12 小时重启一次
   - 内存超过阈值时立即重启

2. **在代码中添加内存监控**（方案 2）
   - 记录详细的内存使用日志
   - 双重保护机制

3. **排查并修复代码中的内存泄露**（方案 3）
   - 使用内存分析工具找出泄露源头
   - 修复根本问题

4. **优化 Celery 配置**（方案 4）
   - 减少不必要的内存占用
   - 优化任务处理流程

## 具体修改步骤

### 步骤 1：创建脚本文件

```bash
chmod +x bin/celery_auto_restart_with_monitor.sh
```

### 步骤 2：修改 app_desc.yaml

```yaml
modules:
    default:
        env_variables:
            # ... 现有配置 ...
            - key: CELERY_RESTART_INTERVAL
              value: 43200
              description: Celery worker 定时重启间隔（秒），12小时
            - key: CELERY_MAX_MEMORY_MB
              value: 1600
              description: Celery worker 内存上限（MB），4C2G容器用1600MB

        processes:
            dworker:
                command: bash bin/celery_auto_restart_with_monitor.sh worker -Q default -n default@%h -P threads -c 10 -l info
                plan: 4C2G5R
                replicas: 5

    pipeline:
        env_variables:
            # ... 现有配置 ...
            - key: CELERY_RESTART_INTERVAL
              value: 43200
              description: Celery worker 定时重启间隔（秒），12小时
            - key: CELERY_MAX_MEMORY_MB
              value: 800
              description: Celery worker 内存上限（MB），4C1G容器用800MB

        processes:
            v1-engine:
                command: bash bin/celery_auto_restart_with_monitor.sh worker -A blueapps.core.celery -P threads -Q api_task_queue_pipeline_priority,api_task_queue_service_schedule_priority,periodic_task_queue_pipeline_priority,periodic_task_queue_service_schedule_priority,pipeline,pipeline_priority,service_schedule,service_schedule_priority -n v1_engine@%h -c 100 -l info
                plan: 4C1G5R
                replicas: 2

            # 其他 worker 类似...
```

### 步骤 3：添加内存监控代码

创建 `gcloud/celery_monitor.py`（见方案 2）

### 步骤 4：修改配置文件

在 `config/default.py` 中添加优化配置（见方案 4）

### 步骤 5：添加 psutil 依赖

```txt
# requirements.txt
psutil>=5.8.0
```

## 监控和验证

### 查看重启日志

```bash
# 查看 worker 日志
tail -f logs/celery.log | grep -E "Memory|restart|shutdown"
```

### 内存使用趋势监控

建议使用 Prometheus + Grafana 监控：
- Worker 内存使用趋势
- Worker 重启频率
- 任务执行耗时

## 总结

**threads 模式下没有内置的内存限制机制，必须通过外部手段实现：**

1. ✅ **定时重启**：最可靠的方案
2. ✅ **内存监控 + 主动退出**：精确控制
3. ✅ **修复代码**：根本解决
4. ✅ **优化配置**：减少内存占用

**不要依赖 `--max-memory-per-child` 和 `--max-tasks-per-child`，它们在 threads 模式下完全无效！**

