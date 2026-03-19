# Celery 自动重启方案 - 最终配置说明

## 当前配置特点

### ✅ 设计理念

1. **长周期重启**：默认 7 天重启一次，避免频繁重启影响服务
2. **立即启动**：第一次启动时所有 worker 立即启动，无延迟
3. **随机重启**：运行中的重启时间随机分散，避免同时重启
4. **优雅关闭**：给 worker 10 分钟时间完成当前任务后再关闭

### 📊 脚本参数

| 参数 | 默认值 | 说明 |
|-----|--------|------|
| `CELERY_RESTART_INTERVAL` | 604800 (7天) | 基础重启间隔 |
| `CELERY_RESTART_RANDOM_PERCENT` | 10 (±10%) | 随机偏移百分比 |
| ~~`CELERY_INITIAL_RANDOM_DELAY`~~ | ~~已删除~~ | 不再使用初始延迟 |

## 实际运行效果

### 启动行为

```
部署时（t=0）：
├─ Worker 1: 立即启动 ✓
├─ Worker 2: 立即启动 ✓
├─ Worker 3: 立即启动 ✓
├─ Worker 4: 立即启动 ✓
└─ Worker 5: 立即启动 ✓

所有 worker 同时启动，快速上线服务
```

### 重启行为

```
运行 7 天后（首次重启）：
├─ Worker 1: 6.3天后重启 (±10% → 约6.3-7.7天)
├─ Worker 2: 7.4天后重启
├─ Worker 3: 6.8天后重启
├─ Worker 4: 7.2天后重启
└─ Worker 5: 6.5天后重启

重启分散在约 1.4 天的时间窗口内
```

### 时间分布计算

```
基础间隔：7 天 = 604800 秒
随机偏移：±10%

最短间隔：604800 × (1 - 0.10) = 544320 秒 ≈ 6.3 天
最长间隔：604800 × (1 + 0.10) = 665280 秒 ≈ 7.7 天

时间窗口：7.7 - 6.3 = 1.4 天
```

## 配置示例

### 在 app_desc.yaml 中的配置

```yaml
modules:
    pipeline:
        env_variables:
            # Celery 自动重启配置
            - key: CELERY_RESTART_INTERVAL
              value: 604800
              description: Celery worker 基础重启间隔（秒），7天

            - key: CELERY_RESTART_RANDOM_PERCENT
              value: 10
              description: 重启间隔随机偏移百分比（±10%），避免同时重启

        processes:
            v1-engine:
                command: bash bin/celery_auto_restart.sh worker -A blueapps.core.celery -P threads -Q api_task_queue_pipeline_priority,api_task_queue_service_schedule_priority,periodic_task_queue_pipeline_priority,periodic_task_queue_service_schedule_priority,pipeline,pipeline_priority,service_schedule,service_schedule_priority -n v1_engine@%h -c 100 -l info
                plan: 4C1G5R
                replicas: 2
```

**注意：** 不再需要 `CELERY_INITIAL_RANDOM_DELAY` 环境变量

## 不同场景的推荐配置

### 场景 1：默认配置（推荐）

**适用：** 内存泄露较轻，服务稳定

```yaml
env_variables:
    - key: CELERY_RESTART_INTERVAL
      value: 604800  # 7 天

    - key: CELERY_RESTART_RANDOM_PERCENT
      value: 10  # ±10%，分布在 6.3-7.7 天
```

**效果：**
- 每周重启一次，内存定期清理
- 对服务影响最小
- 适合生产环境长期运行

### 场景 2：内存泄露明显

**适用：** 监控发现内存持续增长，但不严重

```yaml
env_variables:
    - key: CELERY_RESTART_INTERVAL
      value: 259200  # 3 天

    - key: CELERY_RESTART_RANDOM_PERCENT
      value: 15  # ±15%，分布在 2.55-3.45 天
```

**效果：**
- 每 3 天左右重启
- 防止内存占用过高
- 保持较好的稳定性

### 场景 3：内存泄露严重

**适用：** 内存快速增长，需要频繁重启

```yaml
env_variables:
    - key: CELERY_RESTART_INTERVAL
      value: 86400  # 1 天

    - key: CELERY_RESTART_RANDOM_PERCENT
      value: 15  # ±15%，分布在 20.4-27.6 小时
```

**效果：**
- 每天重启一次
- 及时释放内存
- 需要同步排查代码问题

### 场景 4：高可用要求（多副本）

**适用：** 有 5 个以上副本，需要更分散的重启

```yaml
env_variables:
    - key: CELERY_RESTART_INTERVAL
      value: 604800  # 7 天

    - key: CELERY_RESTART_RANDOM_PERCENT
      value: 20  # ±20%，分布在 5.6-8.4 天
```

**效果：**
- 重启窗口扩大到 2.8 天
- 多副本时重启更分散
- 降低同时重启概率

## 优雅关闭机制

### 关闭流程

```
收到重启信号（timeout 超时）
    ↓
发送 TERM 信号给 celery worker
    ↓
Worker 停止接收新任务
    ↓
等待当前任务完成（最多 10 分钟）
    ↓
如果 10 分钟后仍未完成
    ↓
强制 KILL 进程
```

### 配置参数

```bash
# 在脚本中设置（已修改）
timeout --foreground --kill-after=600 ${ACTUAL_INTERVAL}s \
    celery ${CELERY_ARGS} || true
```

- `--kill-after=600`：在发送 TERM 信号后，如果 10 分钟内没有退出，则强制 KILL
- 适合执行时间较长的任务

### 建议

| 任务平均执行时间 | kill-after 设置 |
|----------------|----------------|
| < 1 分钟 | 60 秒 |
| 1-5 分钟 | 300 秒（5分钟） |
| 5-10 分钟 | 600 秒（10分钟）✓ 当前设置 |
| > 10 分钟 | 1200 秒（20分钟） |

## 日志示例

### 正常启动日志

```log
[2025-10-20 10:00:00] Celery auto-restart wrapper started
[2025-10-20 10:00:00] Base restart interval: 604800 seconds
[2025-10-20 10:00:00] Random offset: ±10%
[2025-10-20 10:00:00] Celery args: worker -A blueapps.core.celery -P threads -Q default -n default@api-er-e-0 -c 100 -l info
[2025-10-20 10:00:00] First startup: immediate (no initial delay)
[2025-10-20 10:00:00] Starting celery worker...
[2025-10-20 10:00:00] This cycle restart interval: 628320 seconds (base: 604800, offset: +23520)
```

### 7 天后重启日志

```log
[2025-10-27 13:16:00] Worker reached restart interval, restarting...
[2025-10-27 13:16:02] Starting celery worker...
[2025-10-27 13:16:02] This cycle restart interval: 581760 seconds (base: 604800, offset: -23040)
```

### 优雅关闭日志（来自 celery）

```log
[2025-10-27 13:16:00] [INFO/MainProcess] Received signal: SIGTERM
[2025-10-27 13:16:00] [INFO/MainProcess] Warm shutdown (MainProcess)
[2025-10-27 13:16:00] [INFO/MainProcess] Waiting for active tasks to complete...
[2025-10-27 13:16:15] [INFO/MainProcess] All tasks completed, shutting down
```

## 监控和验证

### 验证启动行为

```bash
# 查看所有 worker 的启动时间
kubectl get pods -l app=bk-sops -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.startTime}{"\n"}{end}'

# 预期：所有 pod 的启动时间应该非常接近（几秒内）
api-er-e-0    2025-10-20T10:00:00Z
api-er-e-1    2025-10-20T10:00:01Z
api-er-e-2    2025-10-20T10:00:00Z
api-er-e-3    2025-10-20T10:00:02Z
```

### 验证重启间隔

```bash
# 查看计划的重启间隔
kubectl logs <pod-name> | grep "restart interval"

# 预期：每个 pod 的间隔不同（随机偏移）
This cycle restart interval: 628320 seconds (base: 604800, offset: +23520)
This cycle restart interval: 581760 seconds (base: 604800, offset: -23040)
This cycle restart interval: 604800 seconds (base: 604800, offset: 0)
```

### 监控内存趋势

```bash
# 监控 7 天内的内存使用情况
kubectl top pods -l app=bk-sops --containers | grep worker

# 预期：内存逐渐增长，重启后下降
api-er-e-0  celery  256Mi    # Day 1
api-er-e-0  celery  512Mi    # Day 3
api-er-e-0  celery  768Mi    # Day 5
api-er-e-0  celery  128Mi    # Day 7 (重启后)
```

## 调优建议

### 根据内存增长速度调整

1. **监控 7 天内的内存增长**
   ```bash
   # 查看内存使用趋势
   kubectl top pods -l app=bk-sops --containers
   ```

2. **评估是否需要调整间隔**
   - 如果 7 天内内存增长 < 50%：保持 7 天间隔 ✓
   - 如果 7 天内内存增长 50-80%：改为 3-5 天间隔
   - 如果 7 天内内存增长 > 80%：改为 1-2 天间隔

3. **评估随机偏移范围**
   - 副本数 1-2：保持 10% ✓
   - 副本数 3-5：增加到 15%
   - 副本数 6+：增加到 20%

### 平衡重启频率和稳定性

```
重启过于频繁：
❌ 增加系统开销
❌ 可能中断长时间任务
❌ 影响服务稳定性

重启过于稀疏：
❌ 内存可能溢出
❌ OOM 风险
❌ 性能下降

当前配置（7天）：
✅ 平衡内存管理和稳定性
✅ 适合大多数场景
✅ 降低运维成本
```

## 故障排查

### 问题：Worker 在 7 天前就 OOM 了

**原因：** 内存泄露速度超出预期

**解决：**
```yaml
# 缩短重启间隔
CELERY_RESTART_INTERVAL: 259200  # 改为 3 天
```

### 问题：任务执行到一半被中断

**原因：** 任务执行时间超过 10 分钟

**解决：**
1. 修改脚本中的 `--kill-after` 参数
2. 或者优化任务，拆分为多个小任务

### 问题：重启时仍有多个 worker 同时重启

**原因：** 随机偏移太小

**解决：**
```yaml
# 增大随机偏移
CELERY_RESTART_RANDOM_PERCENT: 20  # 改为 ±20%
```

## 总结

### 当前配置特点

| 特性 | 说明 | 优势 |
|-----|------|------|
| 7 天重启周期 | 每周重启一次 | 稳定性高，对服务影响小 |
| 立即启动 | 第一次启动无延迟 | 快速上线，适合发版场景 |
| ±10% 随机偏移 | 重启分散在 1.4 天内 | 避免同时重启，高可用 |
| 10 分钟优雅关闭 | 等待任务完成再关闭 | 不丢失任务，数据安全 |

### 适用场景

✅ **推荐使用：**
- 内存泄露较轻（每天增长 < 100MB）
- 服务稳定性要求高
- 生产环境长期运行
- 有多个副本保证高可用

⚠️ **需要调整：**
- 内存泄露严重（每天增长 > 500MB）→ 缩短重启间隔
- 单副本服务 → 不需要随机偏移
- 长时间任务（> 10 分钟）→ 增加 kill-after 时间

### 后续优化

1. **监控内存使用情况**，根据实际情况调整重启间隔
2. **排查代码中的内存泄露**，从根本上解决问题
3. **优化 Celery 配置**，减少不必要的内存占用
4. **考虑添加内存监控模块**（可选），在内存超限时主动重启

---

## 快速参考

### 当前脚本默认值

```bash
RESTART_INTERVAL=604800           # 7 天
RESTART_RANDOM_PERCENT=10         # ±10%
--kill-after=600                  # 10 分钟
```

### 环境变量（只需 2 个）

```yaml
- key: CELERY_RESTART_INTERVAL
  value: 604800

- key: CELERY_RESTART_RANDOM_PERCENT
  value: 10
```

### 使用方法

```yaml
command: bash bin/celery_auto_restart.sh worker -A blueapps.core.celery -P threads -Q default -n worker@%h -c 100 -l info
```

就这么简单！🎉

