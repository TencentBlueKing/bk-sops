# Celery Threads 模式内存泄露完整解决方案

## 问题描述

项目中的 celery worker 使用 `-P threads` 模式长时间运行时出现内存泄露，需要在不改变进程模式的情况下修复。

## 核心问题

在 threads 模式下：
- ❌ `--max-tasks-per-child` **不生效**（仅支持 prefork 模式）
- ❌ `--max-memory-per-child` **不生效**（仅支持 prefork 模式）
- ✅ 必须通过**重启整个进程**来释放内存

## 完整解决方案

### 🎯 方案：定时自动重启 + 随机机制

通过包装脚本实现：
1. ✅ 定时自动重启（防止内存持续增长）
2. ✅ 随机延迟机制（避免所有进程同时重启）
3. ✅ 优雅关闭（不丢失任务）
4. ✅ 灵活配置（通过环境变量调整）

---

## 实施步骤

### 步骤 1：确认脚本文件已创建 ✅

脚本位置：`bin/celery_auto_restart.sh`

该脚本已实现：
- 定时重启机制
- 初始启动随机延迟（避免部署时同时启动）
- 重启间隔随机偏移（避免运行时同时重启）
- 优雅关闭和错误处理

### 步骤 2：修改 app_desc.yaml

#### 2.1 添加环境变量

在需要使用自动重启的模块中添加环境变量：

```yaml
modules:
    default:
        env_variables:
            # ... 保留原有配置 ...

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
```

#### 2.2 修改 worker 命令

将原来的 celery worker 命令用脚本包装：

**修改前：**
```yaml
dworker:
    command: python manage.py celery worker -Q default -n default@%h -P threads -c 10 -l info
    plan: 4C2G5R
    replicas: 5
```

**修改后：**
```yaml
dworker:
    command: bash bin/celery_auto_restart.sh worker -Q default -n default@%h -P threads -c 10 -l info
    plan: 4C2G5R
    replicas: 5
```

> **注意：**
> - 脚本会自动添加 `celery` 命令和 `manage.py`
> - 只需传递原命令中 `celery` 后面的参数

### 步骤 3：确保脚本有执行权限

```bash
chmod +x bin/celery_auto_restart.sh
```

### 步骤 4：提交代码并部署

```bash
git add bin/celery_auto_restart.sh
git add app_desc.yaml
git commit -m "feat: add celery auto-restart with random delay to prevent memory leak"
git push
```

---

## 配置参数详解

### 参数 1：CELERY_RESTART_INTERVAL

**含义：** 基础重启间隔（秒）

**默认值：** 43200（12 小时）

**推荐配置：**

| 内存泄露程度 | 推荐间隔 | 说明 |
|-------------|---------|------|
| 轻度 (<100MB/天) | 43200-86400 (12-24h) | 内存增长缓慢 |
| 中度 (100-500MB/天) | 28800-43200 (8-12h) | 需要定期清理 |
| 重度 (>500MB/天) | 21600-28800 (6-8h) | 频繁重启防止 OOM |

### 参数 2：CELERY_RESTART_RANDOM_PERCENT

**含义：** 重启间隔的随机偏移百分比（±%）

**默认值：** 10（±10%）

**推荐配置：**

| 副本数量 | 推荐偏移 | 时间分布范围（12h 基础） |
|---------|---------|------------------------|
| 1-2 副本 | 5-10% | 1-2.4 小时 |
| 3-5 副本 | 10-15% | 2.4-3.6 小时 |
| 6-10 副本 | 15-20% | 3.6-4.8 小时 |
| 10+ 副本 | 20-25% | 4.8-6 小时 |

**计算示例：**
```
基础间隔：12 小时 = 43200 秒
随机偏移：±15%

最短：43200 × (1 - 0.15) = 36720 秒 (10.2 小时)
最长：43200 × (1 + 0.15) = 49680 秒 (13.8 小时)

结果：重启时间分布在 10.2-13.8 小时之间（3.6 小时跨度）
```

### 参数 3：CELERY_INITIAL_RANDOM_DELAY

**含义：** 初始启动时的随机延迟上限（秒）

**默认值：** 600（10 分钟）

**推荐配置：**

| 场景 | 推荐延迟 | 说明 |
|-----|---------|------|
| 测试环境 | 60-300 秒 | 快速启动，方便测试 |
| 生产环境（少量副本） | 300-600 秒 | 5-10 分钟内启动 |
| 生产环境（大量副本） | 600-1200 秒 | 10-20 分钟内启动 |

---

## 不同场景的完整配置示例

### 场景 1：default 模块（5 副本，2GB 内存）

```yaml
modules:
    default:
        env_variables:
            - key: CELERY_RESTART_INTERVAL
              value: 43200  # 12 小时

            - key: CELERY_RESTART_RANDOM_PERCENT
              value: 15  # ±15%，分布在 10.2-13.8 小时

            - key: CELERY_INITIAL_RANDOM_DELAY
              value: 600  # 0-10 分钟随机启动

        processes:
            dworker:
                command: bash bin/celery_auto_restart.sh worker -Q default -n default@%h -P threads -c 10 -l info
                plan: 4C2G5R
                replicas: 5
```

**效果：**
- 5 个副本在 10.2-13.8 小时内分散重启
- 部署时在 10 分钟内分散启动
- 不会同时重启导致服务中断

### 场景 2：pipeline 模块（多个 worker，1GB 内存）

```yaml
modules:
    pipeline:
        env_variables:
            - key: CELERY_RESTART_INTERVAL
              value: 28800  # 8 小时（内存小，重启更频繁）

            - key: CELERY_RESTART_RANDOM_PERCENT
              value: 20  # ±20%，分布在 6.4-9.6 小时

            - key: CELERY_INITIAL_RANDOM_DELAY
              value: 900  # 0-15 分钟随机启动

        processes:
            api-er-e:
                command: bash bin/celery_auto_restart.sh worker -A blueapps.core.celery -P threads -Q er_execute_api -n api_er_e_worker@%h -c 100 -l info
                plan: 4C1G5R
                replicas: 4

            api-er-s:
                command: bash bin/celery_auto_restart.sh worker -A blueapps.core.celery -P threads -Q er_schedule_api -n api_er_s_worker@%h -c 100 -l info
                plan: 4C1G5R
                replicas: 4
```

**效果：**
- 每个 worker 在 6.4-9.6 小时内重启
- 4 个副本分散在 3.2 小时窗口内
- 更频繁的重启，防止 1GB 内存不足

---

## 验证方法

### 1. 查看启动日志

```bash
# 查看初始随机延迟
kubectl logs <pod-name> | grep "Initial random delay"

# 预期输出（每个 pod 不同）
[2025-10-20 10:00:00] Initial random delay: 247 seconds
[2025-10-20 10:00:00] Initial random delay: 512 seconds
[2025-10-20 10:00:00] Initial random delay: 89 seconds
```

### 2. 查看重启间隔

```bash
# 查看实际的重启间隔
kubectl logs <pod-name> | grep "restart interval"

# 预期输出（每次重启间隔不同）
[2025-10-20 10:04:07] This cycle restart interval: 44856 seconds (base: 43200, offset: +1656)
[2025-10-20 22:30:25] This cycle restart interval: 41234 seconds (base: 43200, offset: -1966)
```

### 3. 监控重启事件

```bash
# 实时监控 pod 状态
watch -n 10 'kubectl get pods -l app=bk-sops'

# 正常情况：不会看到多个 pod 同时 Terminating
```

### 4. 验证内存释放

```bash
# 查看内存使用趋势
kubectl top pods -l app=bk-sops

# 预期：重启后内存使用明显下降
```

---

## 完整的日志示例

### 启动日志

```log
[2025-10-20 10:00:00] Celery auto-restart wrapper started
[2025-10-20 10:00:00] Base restart interval: 43200 seconds
[2025-10-20 10:00:00] Random offset: ±15%
[2025-10-20 10:00:00] Celery args: worker -A blueapps.core.celery -P threads -Q default -n default@api-er-e-0 -c 100 -l info
[2025-10-20 10:00:00] Initial random delay: 247 seconds (to avoid simultaneous startup)
[2025-10-20 10:04:07] Starting celery worker...
[2025-10-20 10:04:07] This cycle restart interval: 44856 seconds (base: 43200, offset: +1656)
```

### 重启日志

```log
[2025-10-20 22:30:23] Worker reached restart interval, restarting...
[2025-10-20 22:30:25] Starting celery worker...
[2025-10-20 22:30:25] This cycle restart interval: 41234 seconds (base: 43200, offset: -1966)
```

### 错误处理日志

```log
[2025-10-20 15:30:15] Worker exited with error code 1, waiting 10s before restart...
[2025-10-20 15:30:25] Starting celery worker...
[2025-10-20 15:30:25] This cycle restart interval: 45123 seconds (base: 43200, offset: +1923)
```

---

## 监控和告警

### 推荐监控指标

1. **内存使用率**
   - 监控每个 worker 的内存使用趋势
   - 设置告警：内存使用 > 80%

2. **重启频率**
   - 统计每小时的 worker 重启次数
   - 设置告警：同一时间超过 2 个 worker 重启

3. **任务执行情况**
   - 监控任务队列长度
   - 监控任务执行成功率
   - 设置告警：队列长度异常增长

4. **Worker 可用性**
   - 监控活跃 worker 数量
   - 设置告警：可用 worker < 最小副本数

### Prometheus 查询示例

```promql
# 内存使用率
container_memory_usage_bytes{pod=~".*worker.*"} / container_spec_memory_limit_bytes * 100

# Worker 重启次数
rate(kube_pod_container_status_restarts_total{pod=~".*worker.*"}[1h])

# 任务队列长度
celery_queue_length{queue="default"}
```

---

## 故障排查

### 问题 1：所有 worker 仍然同时重启

**症状：** 观察到多个 worker 在相近时间重启

**可能原因：**
- 随机范围设置太小
- 所有容器同时部署

**解决方法：**
```yaml
# 增大随机百分比
CELERY_RESTART_RANDOM_PERCENT: 20  # 从 10% 改为 20%

# 增大初始延迟
CELERY_INITIAL_RANDOM_DELAY: 1200  # 从 10 分钟改为 20 分钟
```

### 问题 2：Worker 重启过于频繁

**症状：** Worker 在很短时间内就重启

**可能原因：**
- 基础间隔设置太短
- 随机偏移导致最短间隔过小

**解决方法：**
```yaml
# 增加基础间隔
CELERY_RESTART_INTERVAL: 57600  # 从 12h 改为 16h

# 查看实际间隔
kubectl logs <pod> | grep "restart interval"
```

### 问题 3：内存仍然持续增长

**症状：** 即使重启了，内存使用仍然很高

**可能原因：**
- 重启间隔太长
- 内存泄露速度快于预期
- 代码层面的内存泄露

**解决方法：**
```yaml
# 缩短重启间隔
CELERY_RESTART_INTERVAL: 21600  # 改为 6 小时

# 同时需要排查代码中的内存泄露
```

### 问题 4：任务执行中被中断

**症状：** 日志显示任务执行到一半被终止

**可能原因：**
- 任务执行时间超过重启间隔
- Worker 没有正确处理 TERM 信号

**解决方法：**
```yaml
# 增加重启间隔
CELERY_RESTART_INTERVAL: 86400  # 改为 24 小时

# 或在任务中添加优雅退出处理
```

---

## 进阶优化（可选）

### 1. 添加内存监控

创建 `gcloud/celery_monitor.py`（详见 `CELERY_THREADS_MEMORY_FIX_CORRECT.md`）

### 2. 优化 Celery 配置

在 `config/default.py` 中添加：

```python
# 任务结果过期时间
CELERY_RESULT_EXPIRES = 3600  # 1 小时

# 减少预取任务数
CELERY_WORKER_PREFETCH_MULTIPLIER = 4

# 任务完成后才确认
CELERY_ACKS_LATE = True

# 压缩任务数据
CELERY_TASK_COMPRESSION = 'gzip'
```

### 3. 排查代码中的内存泄露

使用 `tracemalloc` 和 `psutil` 分析内存使用（详见文档）

---

## 回滚方案

如果遇到问题需要回滚，只需将 `app_desc.yaml` 中的命令改回原来的即可：

**回滚：**
```yaml
dworker:
    command: python manage.py celery worker -Q default -n default@%h -P threads -c 10 -l info
    plan: 4C2G5R
    replicas: 5
```

**删除环境变量：**
```yaml
# 注释或删除这 3 个环境变量
# - key: CELERY_RESTART_INTERVAL
# - key: CELERY_RESTART_RANDOM_PERCENT
# - key: CELERY_INITIAL_RANDOM_DELAY
```

---

## 总结

### ✅ 已实现的功能

1. **定时自动重启**：防止内存持续增长
2. **随机延迟机制**：避免所有进程同时重启
3. **优雅关闭**：不丢失正在执行的任务
4. **灵活配置**：通过环境变量轻松调整
5. **错误处理**：异常退出时自动重启
6. **详细日志**：便于监控和排查问题

### 📊 预期效果

- ✅ 内存使用控制在合理范围内
- ✅ 不会出现 OOM（内存溢出）
- ✅ 服务稳定性提升（不会因所有 worker 同时重启导致服务中断）
- ✅ 运维成本降低（自动化管理，无需手动重启）

### 📚 相关文档

- `bin/celery_auto_restart.sh` - 重启脚本
- `CELERY_AUTO_RESTART_CONFIG.md` - 详细配置说明
- `app_desc_celery_restart_example.yaml` - 完整配置示例
- `CELERY_THREADS_MEMORY_FIX_CORRECT.md` - 其他可选方案

---

## 快速开始

### 最简单的实施步骤

1. **确认脚本存在**
   ```bash
   ls -l bin/celery_auto_restart.sh
   ```

2. **修改 app_desc.yaml**
   - 添加 3 个环境变量（复制上面的示例）
   - 修改 worker 命令（添加脚本包装）

3. **部署**
   ```bash
   git add .
   git commit -m "feat: add celery auto-restart"
   git push
   ```

4. **验证**
   ```bash
   # 查看日志确认生效
   kubectl logs <pod-name> | grep -E "auto-restart|Initial random delay"
   ```

就这么简单！🎉

