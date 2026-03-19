# 子流程排队执行（互斥执行）方案

> 创建日期: 2026-03-02
> 状态: 待实施

## 背景

用户在使用标准运维时，多个流程（A、B、C）同时引用同一个子流程 D。当 A、B、C 并发执行时，各自创建的子流程 D 实例会同时运行。在某些场景下（如操作同一台主机、写同一份配置），需要子流程 D **按顺序排队执行**，避免并发冲突。

## 现状分析

### 当前子流程执行机制

独立子流程插件 `SubprocessPluginService`（`pipeline_plugins/components/collections/subprocess_plugin/v1_0_0.py`）的执行流程：

1. `plugin_execute`：创建子任务 `TaskFlowInstance` → **立即启动** `task.task_action("start", ...)`
2. 子任务通过 `TaskCallBackRecord` 注册回调
3. 子任务完成后，通过信号处理器 `_check_and_callback` → Celery task `task_callback` → `TaskCallBacker._subprocess_callback` → 回调父节点
4. `plugin_schedule` 被触发，处理子任务执行结果

### 为什么不改代码无法实现

| 现有机制 | 为什么不够 |
|----------|------------|
| Redis 锁（`sc_{node_id}_{version}`） | 仅防止同一节点回调重复，不涉及跨任务互斥 |
| Celery 队列并发控制 | 无法按子流程模板 ID 维度路由，且会阻塞队列上所有任务 |
| ExclusiveGateway（排他网关） | 条件分支用途，不是互斥锁 |
| `TaskConfig` 配置体系 | 仅支持"独立子流程开关"和"重试调参"，无排队配置 |

### 不改代码的变通方案（均有明显局限）

| 方案 | 做法 | 局限 |
|------|------|------|
| 手动协调 | 流程 A/B/C 不同时执行，人工排队 | 完全依赖人工，不可靠 |
| 外部编排层 | 写上层调度脚本，通过 API 监控子流程 D 的状态，按顺序触发 | 需额外开发外部系统，不在 SOPS 体系内 |
| 单 worker 队列 | 为子流程 D 配置 concurrency=1 的专用 Celery 队列 | 引擎不支持按模板维度路由，会阻塞其他任务 |

## 实现方案

### 核心思路

在独立子流程插件中增加基于 **Redis List** 的 FIFO 排队机制，按 **子流程模板 ID** 维度做互斥控制。

### 改动范围

| 文件 | 改动 | 说明 |
|------|------|------|
| `pipeline_plugins/components/collections/subprocess_plugin/v1_0_0.py` | 核心逻辑 | 增加排队等待 + 启动下一个 |
| `gcloud/taskflow3/models.py` | 配置扩展 | `TaskConfig` 增加排队执行配置项 |
| `gcloud/taskflow3/signals/handlers.py` | 边界处理 | 父流程终止时清理队列 |
| `gcloud/taskflow3/migrations/00xx_....py` | DB 迁移 | 无实际 schema 变更，仅扩展 config 选项 |

预估改动量：约 **100 行代码**。

### 执行流程

```
时间轴 →

流程A的子流程D:  [入队(队首)] → [立即启动] → [执行中...] → [完成] → [出队, 启动B的子流程D]
流程B的子流程D:  [入队(第2位)] → [等待...]                          → [启动] → [执行中...] → [完成] → [出队, 启动C的]
流程C的子流程D:  [入队(第3位)] → [等待...] → [等待...]                                      → [启动] → [执行中...] → [完成] → [出队]
```

### 详细实现

#### 1. 扩展 TaskConfig 配置模型

在 `gcloud/taskflow3/models.py` 的 `TaskConfig` 类中增加配置项：

```python
# TaskConfig 类中新增常量
CONFIG_TYPE_EXCLUSIVE_SUBPROCESS = 3
ENABLE_EXCLUSIVE_SUBPROCESS = "enable_exclusive_subprocess"
DISABLE_EXCLUSIVE_SUBPROCESS = "disable_exclusive_subprocess"

# CONFIG_TYPES 增加
CONFIG_TYPES = (
    (CONFIG_TYPE_SUBPROCESS, "subprocess"),
    (CONFIG_TYPE_RETRY_PARAMS, "retry_params"),
    (CONFIG_TYPE_EXCLUSIVE_SUBPROCESS, "exclusive_subprocess"),  # 新增
)

# CONFIG_OPTIONS 增加
CONFIG_OPTIONS = (
    ...
    (ENABLE_EXCLUSIVE_SUBPROCESS, _("启用子流程排队执行")),
    (DISABLE_EXCLUSIVE_SUBPROCESS, _("禁用子流程排队执行")),
)
```

在 `TaskConfigManager` 中新增查询方法：

```python
def enable_exclusive_subprocess(self, template_id) -> bool:
    """是否启用子流程排队执行"""
    return self.filter(
        scope=TaskConfig.SCOPE_TYPE_TEMPLATE,
        scope_id=template_id,
        config_type=TaskConfig.CONFIG_TYPE_EXCLUSIVE_SUBPROCESS,
        config_value=TaskConfig.ENABLE_EXCLUSIVE_SUBPROCESS,
    ).exists()
```

#### 2. 修改 SubprocessPluginService

**文件：** `pipeline_plugins/components/collections/subprocess_plugin/v1_0_0.py`

##### 2.1 新增辅助方法

```python
class SubprocessPluginService(BasePluginService):
    __need_schedule__ = True
    runtime = BambooDjangoRuntime()

    QUEUE_KEY_PREFIX = "subprocess_exclusive_queue"
    QUEUE_TTL = 86400  # 24小时，防止异常情况下队列永不清空

    def _is_exclusive(self, template_id):
        """检查该子流程模板是否启用排队执行"""
        return TaskConfig.objects.enable_exclusive_subprocess(template_id)

    def _get_queue_key(self, template_id):
        return f"{self.QUEUE_KEY_PREFIX}:{template_id}"

    def _enqueue_and_check_head(self, template_id, child_task_id):
        """
        原子操作：入队并检查自己是否是队首。
        返回 True 表示自己是队首（可以立即启动），False 表示需要等待。
        """
        queue_key = self._get_queue_key(template_id)
        queue_item = json.dumps({
            "child_task_id": child_task_id,
            "node_id": self.id,
            "node_version": self.version,
        })
        pipe = settings.redis_inst.pipeline()
        pipe.rpush(queue_key, queue_item)
        pipe.lindex(queue_key, 0)
        pipe.expire(queue_key, self.QUEUE_TTL)
        _, first_item, _ = pipe.execute()

        first = json.loads(first_item)
        return first["child_task_id"] == child_task_id

    def _dequeue_and_start_next(self, template_id):
        """出队当前任务，启动下一个等待中的子任务"""
        queue_key = self._get_queue_key(template_id)
        settings.redis_inst.lpop(queue_key)

        next_item = settings.redis_inst.lindex(queue_key, 0)
        if not next_item:
            return

        next_info = json.loads(next_item)
        try:
            next_task = TaskFlowInstance.objects.get(id=next_info["child_task_id"])
            parent_relation = TaskFlowRelation.objects.get(task_id=next_task.id)
            parent_task = TaskFlowInstance.objects.get(id=parent_relation.parent_task_id)
            next_task.task_action("start", parent_task.executor)
            self.logger.info(
                f"[exclusive] started queued subprocess {next_task.id} "
                f"for template {template_id}"
            )
        except Exception as e:
            self.logger.exception(
                f"[exclusive] failed to start queued subprocess: {e}"
            )
            # 当前任务无法启动，跳过，尝试启动下一个
            self._dequeue_and_start_next(template_id)
```

##### 2.2 修改 plugin_execute

在 `plugin_execute` 方法中，将原来直接启动子任务的代码改为带排队逻辑：

```python
def plugin_execute(self, data, parent_data):
    # ... 现有代码（第66~209行）不变，创建子任务 task ...

    # === 排队逻辑（替换原来的直接启动） ===
    exclusive = self._is_exclusive(subprocess.template_id)
    if exclusive:
        is_head = self._enqueue_and_check_head(subprocess.template_id, task.id)
        if is_head:
            task.task_action("start", parent_task.executor)
            self.logger.info(
                f"[exclusive] subprocess {task.id} is queue head, started immediately"
            )
        else:
            self.logger.info(
                f"[exclusive] subprocess {task.id} queued, waiting for turn"
            )
    else:
        # 非排队模式，保持原有行为：直接启动
        task.task_action("start", parent_task.executor)

    data.set_outputs("task_id", task.id)
    data.set_outputs("task_url", task.url)
    data.set_outputs("task_name", task.name)
    data.set_outputs("exclusive_template_id", subprocess.template_id if exclusive else "")

    # ... 现有的操作流水记录代码不变 ...
    return True
```

##### 2.3 修改 plugin_schedule

在子流程完成后，出队并启动下一个等待者：

```python
def plugin_schedule(self, data, parent_data, callback_data=None):
    task_success = callback_data.get("task_success", False)
    task_id = data.get_one_of_outputs("task_id")
    self.finish_schedule()

    # === 排队出队 + 启动下一个（无论成功失败都要执行） ===
    exclusive_template_id = data.get_one_of_outputs("exclusive_template_id")
    if exclusive_template_id:
        try:
            self._dequeue_and_start_next(exclusive_template_id)
        except Exception as e:
            self.logger.exception(f"[exclusive] dequeue error: {e}")

    if not task_success:
        data.set_outputs("ex_data", "子流程执行失败，请检查失败节点")
        return False

    # ... 现有的输出传递代码不变 ...
```

#### 3. 处理父流程终止的边界情况

**文件：** `gcloud/taskflow3/signals/handlers.py`

当父流程被终止（REVOKED）时，需要清理队列中该节点的残留项，并启动下一个等待者：

```python
@receiver(post_set_state)
def bamboo_engine_eri_post_set_state_handler(sender, node_id, to_state, version, root_id, parent_id, loop, **kwargs):
    # ... 现有代码 ...

    elif to_state == bamboo_engine_states.REVOKED and node_id == root_id:
        # ... 现有的终止处理 ...

        # 清理该流程下所有子流程的排队项
        try:
            _cleanup_exclusive_queue_on_revoke(root_id)
        except Exception:
            logger.exception("cleanup exclusive queue on revoke error")


def _cleanup_exclusive_queue_on_revoke(root_pipeline_id):
    """父流程终止时，清理其子流程在排队队列中的残留项"""
    from gcloud.taskflow3.models import TaskFlowInstance, TaskFlowRelation

    task = TaskFlowInstance.objects.filter(pipeline_instance__instance_id=root_pipeline_id).first()
    if not task:
        return

    child_relations = TaskFlowRelation.objects.filter(parent_task_id=task.id)
    child_task_ids = set(child_relations.values_list("task_id", flat=True))
    if not child_task_ids:
        return

    prefix = "subprocess_exclusive_queue:*"
    for key in settings.redis_inst.scan_iter(match=prefix):
        queue_items = settings.redis_inst.lrange(key, 0, -1)
        for item in queue_items:
            info = json.loads(item)
            if info["child_task_id"] in child_task_ids:
                settings.redis_inst.lrem(key, 1, item)
                # 如果移除的是队首，需要启动新的队首
                new_head = settings.redis_inst.lindex(key, 0)
                if new_head:
                    _trigger_queued_subprocess(json.loads(new_head))


def _trigger_queued_subprocess(task_info):
    """启动排队中的下一个子任务"""
    from gcloud.taskflow3.models import TaskFlowInstance, TaskFlowRelation

    try:
        next_task = TaskFlowInstance.objects.get(id=task_info["child_task_id"])
        parent_relation = TaskFlowRelation.objects.get(task_id=next_task.id)
        parent_task = TaskFlowInstance.objects.get(id=parent_relation.parent_task_id)
        next_task.task_action("start", parent_task.executor)
    except Exception:
        logger.exception(f"trigger queued subprocess {task_info['child_task_id']} failed")
```

### 配置方式

管理员可通过 Django Admin 或直接数据库操作，对需要排队的子流程模板开启配置：

```python
from gcloud.taskflow3.models import TaskConfig

# 开启排队执行
TaskConfig.objects.create(
    scope=TaskConfig.SCOPE_TYPE_TEMPLATE,
    scope_id=<子流程D的模板ID>,
    config_type=TaskConfig.CONFIG_TYPE_EXCLUSIVE_SUBPROCESS,
    config_value=TaskConfig.ENABLE_EXCLUSIVE_SUBPROCESS,
)

# 关闭排队执行
TaskConfig.objects.filter(
    scope=TaskConfig.SCOPE_TYPE_TEMPLATE,
    scope_id=<子流程D的模板ID>,
    config_type=TaskConfig.CONFIG_TYPE_EXCLUSIVE_SUBPROCESS,
).delete()
```

### Redis 数据结构

```
Key:    subprocess_exclusive_queue:{template_id}
Type:   List (FIFO)
TTL:    86400 (24小时)
Value:  [
          '{"child_task_id": 101, "node_id": "nxxx1", "node_version": "v1"}',  ← 队首（正在执行）
          '{"child_task_id": 102, "node_id": "nxxx2", "node_version": "v1"}',  ← 等待中
          '{"child_task_id": 103, "node_id": "nxxx3", "node_version": "v1"}',  ← 等待中
        ]
```

### 边界情况处理

| 场景 | 处理方式 |
|------|----------|
| 子流程执行失败 | `plugin_schedule` 中无论成功失败都执行出队+启动下一个 |
| 父流程被终止 | `post_set_state` REVOKED 信号处理中清理队列残留项 |
| Redis 队列残留 | 队列 Key 设置 24 小时 TTL，自动过期清理 |
| SOPS 服务重启 | Redis 队列数据持久化，已入队的子任务关系仍存在于 DB，可通过 management command 定期扫描恢复 |
| 子任务启动失败 | `_dequeue_and_start_next` 递归跳过失败项，尝试下一个 |
| 同一模板在不同项目中排队 | 当前方案按 template_id 全局排队；如需按项目隔离，queue key 可改为 `{template_id}:{project_id}` |

### 测试要点

1. **基本排队**：A/B/C 三个流程并发启动，验证子流程 D 串行执行
2. **队首执行失败**：验证失败后自动启动下一个
3. **父流程终止**：验证队列残留被清理，不阻塞后续排队者
4. **非排队模式**：未配置排队的子流程模板行为不变
5. **Redis 异常**：Redis 不可用时回退到直接启动（不阻塞业务）
6. **并发入队**：多个流程同时到达入队点，验证 Redis pipeline 原子性

### 后续扩展

- **前端配置入口**：在模板编辑页的子流程节点属性中增加"排队执行"开关
- **项目级隔离**：queue key 增加 project_id 维度，不同项目的排队互不影响
- **排队超时**：增加最大等待时间配置，超时自动失败
- **排队状态可视化**：在任务详情页展示当前排队位置和前方等待数量
