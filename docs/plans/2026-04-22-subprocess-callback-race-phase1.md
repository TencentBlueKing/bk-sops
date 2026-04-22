# 独立子流程 Callback 竞态一期修复 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复独立子流程节点成功 callback 因 `schedule lock` 冲突被静默丢弃的问题，并提供专用排查与安全恢复工具。

**Architecture:** 在 `bamboo-engine` 的 `CALLBACK` 锁冲突分支增加一个默认关闭的 service 级重试扩展点，一期仅让 `subprocess_plugin` 对 `task_success=True` 开启该能力。`bk-sops` 增加离线竞态分析命令和安全重放命令，所有人工恢复都必须回到正式 callback 链路。

**Tech Stack:** Python 3.6, Django management command, bamboo-engine runtime, pytest, Django test

**Spec:** `docs/specs/2026-04-22-subprocess-callback-race-phase1-design.md`

---

## File Structure

| 文件 | 操作 | 职责 |
|------|------|------|
| `../bamboo-engine/runtime/bamboo-pipeline/pipeline/core/flow/activity/service_activity.py` | 修改 | 新增 service 级 callback 锁冲突重试扩展点 |
| `../bamboo-engine/bamboo_engine/engine.py` | 修改 | 在 `schedule lock` 冲突分支增加“受控 callback 重试”逻辑 |
| `../bamboo-engine/tests/engine/test_engine_schedule.py` | 修改 | 覆盖可重试 callback、重试上限和非重试节点行为 |
| `pipeline_plugins/components/collections/subprocess_plugin/v1_0_0.py` | 修改 | 仅对独立子流程成功 callback 开启锁冲突重试能力 |
| `pipeline_plugins/tests/components/collections/subprocess_plugin/test_v1_0_0.py` | 新增 | 验证 `callback_lock_retryable` 语义 |
| `gcloud/taskflow3/management/commands/analyze_subprocess_callback_race.py` | 新增 | 识别导出数据中的独立子流程 callback 竞态 |
| `gcloud/taskflow3/management/commands/replay_subprocess_success_callback.py` | 新增 | 对符合条件的独立子流程节点进行安全重放 |
| `gcloud/tests/taskflow3/commands/test_analyze_subprocess_callback_race.py` | 新增 | 验证竞态识别输出 |
| `gcloud/tests/taskflow3/commands/test_replay_subprocess_success_callback.py` | 新增 | 验证安全检查和重放路径 |

---

### Task 1: 为 `bamboo-engine` 增加 service 级 callback 锁重试扩展点

**Files:**
- Modify: `../bamboo-engine/runtime/bamboo-pipeline/pipeline/core/flow/activity/service_activity.py`
- Test: `../bamboo-engine/tests/engine/test_engine_schedule.py`

- [x] **Step 1: 在 `Service` 基类中新增默认实现**

```python
    def callback_lock_retryable(self, callback_data=None):
        return False
```

- [x] **Step 2: 运行现有 engine 相关测试确认无基础回归**

Run: `PYTHONPATH=../bamboo-engine python -m pytest ../bamboo-engine/tests/engine/test_engine_schedule.py -k 'lock_get_failed_but_not_retry' -q`
Expected: PASS

- [x] **Step 3: 提交到工作区，等待后续 Task 2 一起回归**

本任务不单独提交，和 Task 2 一起形成 engine 补丁。

---

### Task 2: 在 `Engine.schedule` 的锁冲突分支增加受控 callback 重试

**Files:**
- Modify: `../bamboo-engine/bamboo_engine/engine.py`
- Test: `../bamboo-engine/tests/engine/test_engine_schedule.py`

- [x] **Step 1: 先写失败测试，覆盖“可重试 callback”场景**

新增测试：

```python
def test_schedule__lock_get_failed_and_retry_enabled_callback(...):
    runtime = Mock()
    runtime.apply_schedule_lock.return_value = False
    runtime.get_callback_data.return_value = Mock(id=1, data={"task_success": True})
    runtime.get_node.return_value = Mock(code="subprocess_plugin", version="1.0.0", name="subprocess")
    runtime.get_service.return_value = Mock(callback_lock_retryable=Mock(return_value=True))

    Engine(runtime).schedule(...)

    runtime.set_next_schedule.assert_called_once()
```

- [x] **Step 2: 再写达到重试上限的测试**

新增测试：

```python
def test_schedule__lock_get_failed_and_retry_enabled_callback_reaches_retry_limit(...):
    headers = {Engine.CALLBACK_LOCK_RETRY_HEADER: Engine.CALLBACK_LOCK_RETRY_LIMIT}
    ...
    runtime.set_next_schedule.assert_not_called()
```

- [x] **Step 3: 实现最小补丁**

核心逻辑：

```python
if not lock_get:
    callback_data = None
    should_retry = schedule.type is ScheduleType.MULTIPLE_CALLBACK
    if not should_retry:
        callback_data, should_retry = self._callback_lock_retry_context(node_id, callback_data_id)
        retry_count = self._schedule_lock_retry_count(headers)
        if should_retry and retry_count >= self.CALLBACK_LOCK_RETRY_LIMIT:
            logger.error(...)
            return

    if not should_retry:
        logger.info(...)
        return

    retry_headers = dict(headers or {})
    if schedule.type is ScheduleType.CALLBACK:
        retry_headers[self.CALLBACK_LOCK_RETRY_HEADER] = self._schedule_lock_retry_count(headers) + 1
    self.runtime.set_next_schedule(...)
    return
```

- [x] **Step 4: 跑聚焦 engine 回归**

Run: `PYTHONPATH=../bamboo-engine python -m pytest ../bamboo-engine/tests/engine/test_engine_schedule.py -k 'lock_get_failed_and_retry_enabled_callback or lock_get_failed_but_not_retry' -q`
Expected: `3 passed`

- [ ] **Step 5: 提交 engine 补丁**

```bash
git -C ../bamboo-engine add runtime/bamboo-pipeline/pipeline/core/flow/activity/service_activity.py bamboo_engine/engine.py tests/engine/test_engine_schedule.py
git -C ../bamboo-engine commit -m "fix: retry subprocess success callback on schedule lock conflict"
```

---

### Task 3: 仅让独立子流程成功 callback 开启该能力

**Files:**
- Modify: `pipeline_plugins/components/collections/subprocess_plugin/v1_0_0.py`
- Test: `pipeline_plugins/tests/components/collections/subprocess_plugin/test_v1_0_0.py`

- [x] **Step 1: 写测试**

```python
class SubprocessPluginServiceTestCase(SimpleTestCase):
    def test_callback_lock_retryable_only_for_success_callback(self):
        service = SubprocessPluginService()
        assert service.callback_lock_retryable({"task_success": True}) is True
        assert service.callback_lock_retryable({"task_success": False}) is False
        assert service.callback_lock_retryable({}) is False
```

- [x] **Step 2: 实现最小代码**

```python
def callback_lock_retryable(self, callback_data=None):
    return bool(callback_data and callback_data.get("task_success") is True)
```

- [x] **Step 3: 跑聚焦测试**

Run: `python manage.py test pipeline_plugins.tests.components.collections.subprocess_plugin.test_v1_0_0 -v 2`
Expected: `OK`

- [ ] **Step 4: 提交 `bk-sops` 侧插件适配**

```bash
git add pipeline_plugins/components/collections/subprocess_plugin/v1_0_0.py pipeline_plugins/tests/components/collections/subprocess_plugin/test_v1_0_0.py
git commit -m "test: cover subprocess callback lock retry policy"
```

---

### Task 4: 新增离线竞态识别命令

**Files:**
- Create: `gcloud/taskflow3/management/commands/analyze_subprocess_callback_race.py`
- Test: `gcloud/tests/taskflow3/commands/test_analyze_subprocess_callback_race.py`

- [x] **Step 1: 写失败测试**

测试目标：

- 同一 `node_id + version` 下同时存在 `task_success=False/True`
- `callback_data_count > schedule_times`
- 节点仍有活跃 schedule
- 输出候选并标记 `safe_to_replay`

- [x] **Step 2: 实现命令**

核心输出字段包括：

- `callback_record_id`
- `node_id`
- `version`
- `active_schedule_ids`
- `latest_failed_callback_data_id`
- `latest_success_callback_data_id`
- `safe_to_replay`
- `replay_blockers`

- [x] **Step 3: 运行聚焦测试**

Run: `python manage.py test gcloud.tests.taskflow3.commands.test_analyze_subprocess_callback_race -v 2`
Expected: `OK`

- [ ] **Step 4: 提交**

```bash
git add gcloud/taskflow3/management/commands/analyze_subprocess_callback_race.py gcloud/tests/taskflow3/commands/test_analyze_subprocess_callback_race.py
git commit -m "feat: add subprocess callback race analyzer"
```

---

### Task 5: 新增安全重放命令

**Files:**
- Create: `gcloud/taskflow3/management/commands/replay_subprocess_success_callback.py`
- Test: `gcloud/tests/taskflow3/commands/test_replay_subprocess_success_callback.py`

- [x] **Step 1: 写失败测试**

测试目标：

- `inspect_candidate` 能识别一个处于 `FAILED` 的独立子流程节点且找到最新成功 callback
- `apply_replay` 在节点为 `FAILED` 时先恢复 `schedule/state`，再走正式 callback dispatch

- [x] **Step 2: 实现 `inspect_candidate`**

安全检查项：

- engine v2
- 节点是 `subprocess_plugin`
- `state` 是 `RUNNING / FAILED`
- `schedule` 未 finished
- root pipeline 一致
- 存在最新成功 callback data

- [x] **Step 3: 实现 `apply_replay`**

```python
if candidate["state"] == bamboo_states.FAILED:
    DBSchedule.objects.filter(id=candidate["schedule_id"]).update(expired=False)
    runtime.set_state(... READY)
    runtime.set_state(... RUNNING)

dispatcher = NodeCommandDispatcher(...)
dispatcher.dispatch(command="callback", operator="system", version=..., data=...)
```

- [x] **Step 4: 跑聚焦测试**

Run: `python manage.py test gcloud.tests.taskflow3.commands.test_replay_subprocess_success_callback -v 2`
Expected: `OK`

- [ ] **Step 5: 提交**

```bash
git add gcloud/taskflow3/management/commands/replay_subprocess_success_callback.py gcloud/tests/taskflow3/commands/test_replay_subprocess_success_callback.py
git commit -m "feat: add safe replay for subprocess success callback"
```

---

### Task 6: 做一期联调回归并准备回修发布

**Files:**
- Verify: `../bamboo-engine/tests/engine/test_engine_schedule.py`
- Verify: `pipeline_plugins/tests/components/collections/subprocess_plugin/test_v1_0_0.py`
- Verify: `gcloud/tests/taskflow3/commands/test_analyze_subprocess_callback_race.py`
- Verify: `gcloud/tests/taskflow3/commands/test_replay_subprocess_success_callback.py`

- [x] **Step 1: 跑 engine 聚焦测试**

Run: `PYTHONPATH=../bamboo-engine python -m pytest ../bamboo-engine/tests/engine/test_engine_schedule.py -k 'lock_get_failed_and_retry_enabled_callback or lock_get_failed_but_not_retry' -q`
Expected: `3 passed`

- [x] **Step 2: 跑 `bk-sops` 聚焦测试**

Run: `python manage.py test pipeline_plugins.tests.components.collections.subprocess_plugin.test_v1_0_0 gcloud.tests.taskflow3.commands.test_analyze_subprocess_callback_race gcloud.tests.taskflow3.commands.test_replay_subprocess_success_callback -v 2`
Expected: `OK`

- [ ] **Step 3: 输出回修说明**

需要在发布说明里明确：

- 该补丁依赖 `bamboo-engine` 与 `bk-sops` 同步回修
- 默认只影响独立子流程成功 callback 的锁冲突处理
- 仍保留现有 callback / version / state 门禁

- [ ] **Step 4: 按版本策略发布**

```bash
# 先在对应线上 tag 完成 bamboo-engine 回修
# 再回修 bk-sops
# 通过灰度验证后再同步到主干和最新维护分支
```
