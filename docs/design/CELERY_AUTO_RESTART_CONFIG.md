# Celery 自动重启脚本配置说明

## 随机重启机制

为避免所有 worker 同时重启导致服务中断，脚本实现了两层随机机制：

### 1. 初始启动随机延迟

在进程首次启动时，添加 0 到 N 秒的随机延迟，避免所有进程同时启动。

**默认值：** 0-600 秒（10 分钟）

**环境变量：** `CELERY_INITIAL_RANDOM_DELAY`

### 2. 重启间隔随机偏移

在每次重启时，基于基础重启间隔添加 ±X% 的随机偏移。

**默认值：** ±10%

**环境变量：** `CELERY_RESTART_RANDOM_PERCENT`

## 配置参数说明

### 1. CELERY_RESTART_INTERVAL

**说明：** 基础重启间隔（秒）

**默认值：** 43200 秒（12 小时）

**推荐值：**
- 内存占用小的 worker：43200（12 小时）
- 内存占用大的 worker：28800（8 小时）
- 内存泄露严重的 worker：21600（6 小时）

### 2. CELERY_RESTART_RANDOM_PERCENT

**说明：** 重启间隔的随机偏移百分比（±%）

**默认值：** 10（表示 ±10%）

**推荐值：**
- 少量副本（1-2 个）：5-10%
- 中等副本（3-5 个）：10-15%
- 大量副本（5+ 个）：15-20%

**计算示例：**
```bash
# 基础间隔 12 小时 = 43200 秒
# 随机偏移 ±10%

最短间隔 = 43200 - (43200 × 10%) = 38880 秒 (10.8 小时)
最长间隔 = 43200 + (43200 × 10%) = 47520 秒 (13.2 小时)

# 实际重启时间分布在 10.8 - 13.2 小时之间
```

### 3. CELERY_INITIAL_RANDOM_DELAY

**说明：** 初始启动时的随机延迟上限（秒）

**默认值：** 600 秒（10 分钟）

**推荐值：**
- 测试环境：60-300 秒（1-5 分钟）
- 生产环境：300-600 秒（5-10 分钟）
- 大规模部署：600-1200 秒（10-20 分钟）

**作用：**
- 避免应用重启/发版时所有 worker 同时启动
- 将启动时间分散到 N 分钟内
- 减少瞬时资源消耗

## 在 app_desc.yaml 中的配置

### 完整配置示例

```yaml
modules:
    default:
        env_variables:
            # Celery 自动重启配置
            - key: CELERY_RESTART_INTERVAL
              value: 43200
              description: Celery worker 基础重启间隔（秒），12小时

            - key: CELERY_RESTART_RANDOM_PERCENT
              value: 15
              description: 重启间隔随机偏移百分比（±%），避免同时重启

            - key: CELERY_INITIAL_RANDOM_DELAY
              value: 600
              description: 初始启动随机延迟上限（秒），10分钟内随机启动

        processes:
            dworker:
                command: bash bin/celery_auto_restart.sh worker -Q default -n default@%h -P threads -c 10 -l info
                plan: 4C2G5R
                replicas: 5

    pipeline:
        env_variables:
            # Celery 自动重启配置（高频重启场景）
            - key: CELERY_RESTART_INTERVAL
              value: 28800
              description: Celery worker 基础重启间隔（秒），8小时（内存占用较大）

            - key: CELERY_RESTART_RANDOM_PERCENT
              value: 20
              description: 重启间隔随机偏移百分比（±20%），副本多时增大随机范围

            - key: CELERY_INITIAL_RANDOM_DELAY
              value: 900
              description: 初始启动随机延迟上限（秒），15分钟（副本多时延长）

        processes:
            v1-engine:
                command: bash bin/celery_auto_restart.sh worker -A blueapps.core.celery -P threads -Q api_task_queue_pipeline_priority,api_task_queue_service_schedule_priority,periodic_task_queue_pipeline_priority,periodic_task_queue_service_schedule_priority,pipeline,pipeline_priority,service_schedule,service_schedule_priority -n v1_engine@%h -c 100 -l info
                plan: 4C1G5R
                replicas: 2

            api-er-e:
                command: bash bin/celery_auto_restart.sh worker -A blueapps.core.celery -P threads -Q er_execute_api -n api_er_e_worker@%h -c 100 -l info
                plan: 4C1G5R
                replicas: 4
```

### 针对不同场景的配置建议

#### 场景 1：少量副本（replicas: 1-2）

```yaml
env_variables:
    - key: CELERY_RESTART_INTERVAL
      value: 43200  # 12 小时

    - key: CELERY_RESTART_RANDOM_PERCENT
      value: 10  # ±10% = 10.8-13.2 小时

    - key: CELERY_INITIAL_RANDOM_DELAY
      value: 300  # 5 分钟
```

**效果：**
- 重启间隔：10.8 - 13.2 小时
- 初始启动：0-5 分钟内随机
- 2 个副本几乎不会同时重启

#### 场景 2：中等副本（replicas: 3-5）

```yaml
env_variables:
    - key: CELERY_RESTART_INTERVAL
      value: 43200  # 12 小时

    - key: CELERY_RESTART_RANDOM_PERCENT
      value: 15  # ±15% = 10.2-13.8 小时

    - key: CELERY_INITIAL_RANDOM_DELAY
      value: 600  # 10 分钟
```

**效果：**
- 重启间隔：10.2 - 13.8 小时（3.6 小时跨度）
- 初始启动：0-10 分钟内随机
- 5 个副本分散在 3.6 小时窗口内

#### 场景 3：大量副本（replicas: 5+）

```yaml
env_variables:
    - key: CELERY_RESTART_INTERVAL
      value: 43200  # 12 小时

    - key: CELERY_RESTART_RANDOM_PERCENT
      value: 20  # ±20% = 9.6-14.4 小时

    - key: CELERY_INITIAL_RANDOM_DELAY
      value: 900  # 15 分钟
```

**效果：**
- 重启间隔：9.6 - 14.4 小时（4.8 小时跨度）
- 初始启动：0-15 分钟内随机
- 多个副本分散在 4.8 小时窗口内

#### 场景 4：内存泄露严重（需要频繁重启）

```yaml
env_variables:
    - key: CELERY_RESTART_INTERVAL
      value: 21600  # 6 小时

    - key: CELERY_RESTART_RANDOM_PERCENT
      value: 15  # ±15% = 5.1-6.9 小时

    - key: CELERY_INITIAL_RANDOM_DELAY
      value: 600  # 10 分钟
```

**效果：**
- 重启间隔：5.1 - 6.9 小时
- 更频繁的重启，防止内存占用过高
- 仍然保持随机性，避免同时重启

## 实际运行效果示例

### 日志输出示例

```log
# Worker 1 启动
[2025-10-20 10:00:00] Celery auto-restart wrapper started
[2025-10-20 10:00:00] Base restart interval: 43200 seconds
[2025-10-20 10:00:00] Random offset: ±10%
[2025-10-20 10:00:00] Initial random delay: 247 seconds (to avoid simultaneous startup)
[2025-10-20 10:04:07] Starting celery worker...
[2025-10-20 10:04:07] This cycle restart interval: 44856 seconds (base: 43200, offset: +1656)

# Worker 2 启动（不同的随机延迟）
[2025-10-20 10:00:00] Celery auto-restart wrapper started
[2025-10-20 10:00:00] Base restart interval: 43200 seconds
[2025-10-20 10:00:00] Random offset: ±10%
[2025-10-20 10:00:00] Initial random delay: 512 seconds (to avoid simultaneous startup)
[2025-10-20 10:08:32] Starting celery worker...
[2025-10-20 10:08:32] This cycle restart interval: 41234 seconds (base: 43200, offset: -1966)

# 重启时的日志
[2025-10-20 22:30:23] Worker reached restart interval, restarting...
[2025-10-20 22:30:25] Starting celery worker...
[2025-10-20 22:30:25] This cycle restart interval: 45123 seconds (base: 43200, offset: +1923)
```

### 时间分布可视化

假设 5 个副本，基础间隔 12 小时，±15% 随机：

```
副本 1: |-------- 10.5 小时 --------|重启
副本 2: |-------- 11.2 小时 --------|重启
副本 3: |-------- 12.8 小时 --------|重启
副本 4: |-------- 13.1 小时 --------|重启
副本 5: |-------- 11.7 小时 --------|重启

时间轴: 0h -------- 6h -------- 12h -------- 18h
        [所有副本分散在这个时间窗口内重启]
```

## 验证和监控

### 1. 查看启动时的随机延迟

```bash
# 查看所有 worker 的启动日志
kubectl logs -l app=bk-sops --tail=20 | grep "Initial random delay"

# 示例输出
api-er-e-0: Initial random delay: 234 seconds
api-er-e-1: Initial random delay: 512 seconds
api-er-e-2: Initial random delay: 89 seconds
api-er-e-3: Initial random delay: 445 seconds
```

### 2. 监控重启间隔分布

```bash
# 查看实际的重启间隔
kubectl logs -l app=bk-sops | grep "restart interval"

# 示例输出
This cycle restart interval: 44856 seconds (base: 43200, offset: +1656)
This cycle restart interval: 41234 seconds (base: 43200, offset: -1966)
This cycle restart interval: 45123 seconds (base: 43200, offset: +1923)
```

### 3. 验证不会同时重启

```bash
# 监控 worker 重启事件
watch -n 60 'kubectl get pods -l app=bk-sops | grep -E "(Running|Terminating|ContainerCreating)"'

# 正常情况应该看到重启是分散的，不会同时出现多个 Terminating
```

## 调优建议

### 1. 根据副本数量调整随机范围

| 副本数 | 推荐随机百分比 | 时间分布范围 |
|--------|----------------|--------------|
| 1-2    | 5-10%          | 1-2.4 小时   |
| 3-5    | 10-15%         | 2.4-3.6 小时 |
| 6-10   | 15-20%         | 3.6-4.8 小时 |
| 10+    | 20-25%         | 4.8-6 小时   |

### 2. 根据内存泄露程度调整基础间隔

- **轻度泄露**（<100MB/天）：12-24 小时
- **中度泄露**（100-500MB/天）：8-12 小时
- **重度泄露**（>500MB/天）：4-8 小时

### 3. 平衡重启频率和服务稳定性

```
重启过于频繁的问题：
- 任务可能被中断
- 增加系统开销
- 影响服务稳定性

重启过于稀疏的问题：
- 内存可能溢出
- OOM 风险增加
- 性能下降

最佳实践：
- 监控实际内存增长速度
- 设置在内存达到 80% 前重启
- 保持足够的随机范围避免同时重启
```

## 注意事项

### 1. 安全下限

脚本内置了安全机制，确保重启间隔不小于 1 小时：

```bash
# 确保间隔不小于 1 小时
if [ $ACTUAL_INTERVAL -lt 3600 ]; then
    ACTUAL_INTERVAL=3600
fi
```

### 2. 随机数种子

Bash 的 `$RANDOM` 会自动使用进程 ID 和时间作为种子，确保每个进程的随机序列不同。

### 3. 优雅关闭

Worker 收到 TERM 信号后会：
1. 停止接收新任务
2. 完成当前正在执行的任务
3. 然后退出

如果 30 秒后仍未退出，会被强制 KILL。

### 4. 与 Kubernetes/容器编排配合

脚本退出后，容器编排系统会自动重启容器，形成完整的重启循环。

## 故障排查

### 问题 1：所有 worker 仍然同时重启

**可能原因：**
- 随机范围设置太小
- 所有 worker 同时部署

**解决方法：**
```yaml
# 增大随机百分比
CELERY_RESTART_RANDOM_PERCENT: 20  # 改为 20%

# 增大初始延迟
CELERY_INITIAL_RANDOM_DELAY: 1200  # 改为 20 分钟
```

### 问题 2：Worker 重启过于频繁

**可能原因：**
- 基础间隔设置太短
- 随机偏移导致实际间隔过短

**解决方法：**
```yaml
# 增加基础间隔
CELERY_RESTART_INTERVAL: 57600  # 改为 16 小时

# 检查日志中的实际间隔
kubectl logs pod-name | grep "restart interval"
```

### 问题 3：初始延迟太长，启动慢

**可能原因：**
- CELERY_INITIAL_RANDOM_DELAY 设置过大

**解决方法：**
```yaml
# 减小初始延迟（仅在副本数少时）
CELERY_INITIAL_RANDOM_DELAY: 180  # 改为 3 分钟
```

## 总结

通过两层随机机制：
1. ✅ **初始启动随机延迟**：避免部署时所有进程同时启动
2. ✅ **重启间隔随机偏移**：避免运行中所有进程同时重启

实现效果：
- 在大规模部署（多副本）场景下，重启时间自然分散
- 不会出现"所有 worker 同时重启导致服务中断"的情况
- 配置灵活，可根据实际情况调整随机范围

