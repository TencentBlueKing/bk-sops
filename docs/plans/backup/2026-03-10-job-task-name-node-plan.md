# Job 插件任务名「节点名称+时间戳」实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为 6 个核心 Job 插件新增小版本，默认使用「节点名称 + 毫秒时间戳」作为 job 任务名。

**Architecture:** 在 `pipeline_plugins/components/utils/sites/open/utils.py` 新增 `get_job_task_name(root_pipeline_id, node_id)`，从 PipelineInstance.execution_data 递归查找节点名，sanitize 后拼接时间戳。各插件新版本在构造 job_kwargs 时调用该函数，有返回值则传入 task_name。

**Tech Stack:** Python, Django, pipeline.models.PipelineInstance, pipeline.core.constants.PE

**设计文档:** `docs/plans/2026-03-10-job-task-name-node-design.md`

---

## Task 1: 实现 get_job_task_name 工具函数

**Files:**
- Modify: `pipeline_plugins/components/utils/sites/open/utils.py`
- Create: `pipeline_plugins/tests/utils/sites/open/test_job_task_name.py`

**Step 1: 编写失败用例**

在 `pipeline_plugins/tests/utils/sites/open/test_job_task_name.py` 新建测试文件：

```python
# -*- coding: utf-8 -*-
"""get_job_task_name 单元测试"""
from unittest.mock import MagicMock, patch

import pytest

from pipeline_plugins.components.utils.sites.open.utils import get_job_task_name


class TestGetJobTaskName:
    """测试 get_job_task_name"""

    def test_returns_task_name_when_node_exists(self):
        """节点存在且有名时返回 节点名_时间戳"""
        mock_pipeline = MagicMock()
        mock_pipeline.execution_data = {
            "activities": {
                "node_1": {"name": "执行脚本", "type": "ServiceActivity"},
            }
        }
        with patch("pipeline_plugins.components.utils.sites.open.utils.PipelineInstance") as MockPI:
            MockPI.objects.filter.return_value.first.return_value = mock_pipeline
            with patch("time.time", return_value=1521100521.303):
                result = get_job_task_name("test_root_123", "node_1")
        assert result == "执行脚本_1521100521303"

    def test_returns_none_when_pipeline_not_found(self):
        """PipelineInstance 不存在时返回 None"""
        with patch("pipeline_plugins.components.utils.sites.open.utils.PipelineInstance") as MockPI:
            MockPI.objects.filter.return_value.first.return_value = None
            result = get_job_task_name("nonexistent_pipeline", "node_1")
        assert result is None

    def test_returns_none_when_node_name_empty(self):
        """节点名为空时返回 None"""
        mock_pipeline = MagicMock()
        mock_pipeline.execution_data = {
            "activities": {
                "node_2": {"name": "", "type": "ServiceActivity"},
            }
        }
        with patch("pipeline_plugins.components.utils.sites.open.utils.PipelineInstance") as MockPI:
            MockPI.objects.filter.return_value.first.return_value = mock_pipeline
            result = get_job_task_name("test_root_456", "node_2")
        assert result is None

    def test_sanitizes_special_chars(self):
        """节点名包含非法字符时被去除"""
        mock_pipeline = MagicMock()
        mock_pipeline.execution_data = {
            "activities": {
                "node_3": {"name": "脚本<>$&'\"", "type": "ServiceActivity"},
            }
        }
        with patch("pipeline_plugins.components.utils.sites.open.utils.PipelineInstance") as MockPI:
            MockPI.objects.filter.return_value.first.return_value = mock_pipeline
            with patch("time.time", return_value=1521100521.303):
                result = get_job_task_name("test_root_789", "node_3")
        assert "<" not in result and ">" not in result
        assert result.endswith("_1521100521303")  # int(1521100521.303 * 1000)
```

**Step 2: 运行测试确认失败**

Run: `cd /root/Projects/bk-sops && pytest pipeline_plugins/tests/utils/sites/open/test_job_task_name.py -v`
Expected: FAIL (get_job_task_name 未定义)

**Step 3: 实现 get_job_task_name**

在 `pipeline_plugins/components/utils/sites/open/utils.py` 中：

1. 在文件顶部 import 增加：`import time`、`from pipeline.core.constants import PE`、`from pipeline.models import PipelineInstance`
2. 在 `__all__` 中增加 `"get_job_task_name"`
3. 新增函数（参考 gcloud.utils.strings.standardize_name 做 sanitize）：

```python
def get_job_task_name(root_pipeline_id, node_id):
    """
    生成 job 任务名：节点名称_sanitize + 毫秒时间戳。
    若无法获取节点名则返回 None（调用方不传 task_name，由作业平台自动生成）。
    """
    import re
    JOB_TASK_NAME_NODE_MAX_LEN = 50

    def _sanitize_node_name(name):
        if not name or not isinstance(name, str):
            return ""
        name_str = re.compile(r"[<>$&\'\"]+").sub("", name)
        return name_str.strip()[:JOB_TASK_NAME_NODE_MAX_LEN]

    def _find_node_name(tree, nid):
        activities = tree.get(PE.activities, {})
        if nid in activities:
            return activities[nid].get("name", "")
        for act in activities.values():
            if act.get("type") == PE.SubProcess and PE.pipeline in act:
                found = _find_node_name(act[PE.pipeline], nid)
                if found:
                    return found
        return ""

    try:
        pipeline = PipelineInstance.objects.filter(instance_id=root_pipeline_id).first()
        if not pipeline or not pipeline.execution_data:
            return None
        node_name = _find_node_name(pipeline.execution_data, node_id)
        sanitized = _sanitize_node_name(node_name)
        if not sanitized:
            return None
        return f"{sanitized}_{int(time.time() * 1000)}"
    except Exception:
        return None
```

**Step 4: 运行测试确认通过**

Run: `cd /root/Projects/bk-sops && pytest pipeline_plugins/tests/utils/sites/open/test_job_task_name.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add pipeline_plugins/components/utils/sites/open/utils.py pipeline_plugins/tests/utils/sites/open/test_job_task_name.py
git commit -m "feat: 新增 get_job_task_name 工具函数 --story=xxx"
```

---

## Task 2: 快速执行脚本 v2_1

**Files:**
- Create: `pipeline_plugins/components/collections/sites/open/job/fast_execute_script/v2_1.py`
- Modify: `pipeline_plugins/components/collections/sites/open/job/fast_execute_script/__init__.py`

**Step 1: 创建 v2_1**

复制 `v2_0.py` 为 `v2_1.py`，修改：
- 类名保持 `JobFastExecuteScriptService`
- 在 `job_kwargs` 构造后、调用 `client.jobv3.fast_execute_script` 前增加：

```python
from pipeline_plugins.components.utils import get_job_task_name

# 在 job_kwargs 构造完成后
task_name = get_job_task_name(self.root_pipeline_id, self.id)
if task_name:
    job_kwargs["task_name"] = task_name
```

- Component 的 `version = "v2.1"`，`form` 保持指向 v2_0.js

**Step 2: 注册 v2_1**

在 `fast_execute_script/__init__.py` 中增加对 v2_1 的 import。

**Step 3: 运行相关测试**

Run: `pytest pipeline_plugins/tests/components/collections/sites/open/job_test/ -k fast_execute -v`
Expected: 现有测试通过

**Step 4: Commit**

```bash
git add pipeline_plugins/components/collections/sites/open/job/fast_execute_script/
git commit -m "feat: 快速执行脚本 v2.1 支持节点名+时间戳作为 job 任务名 --story=xxx"
```

---

## Task 3: 快速分发文件 v3_1

**Files:**
- Create: `pipeline_plugins/components/collections/sites/open/job/fast_push_file/v3_1.py`
- Modify: `pipeline_plugins/components/collections/sites/open/job/fast_push_file/__init__.py`

**Step 1: 创建 v3_1**

复制 `v3_0.py` 为 `v3_1.py`。v3_0 使用 `batch_execute_func` 循环调用 `fast_transfer_file`，需在**每次**构造 `params_list` 中每个元素的 `job_kwargs` 时增加 task_name（每次时间戳不同）。

在循环构造 `params_list` 时，为每个 param 增加：
```python
task_name = get_job_task_name(self.root_pipeline_id, self.id)
if task_name:
    param["task_name"] = task_name
```
注意：每次循环调用时 `time.time()` 会不同，若需同一批次相同前缀可先生成 base_name，再在循环内拼接 `base_name + "_" + str(i)` 或每次重新调用 get_job_task_name（会得到不同时间戳，保证唯一）。

**推荐**：每次循环内调用 `get_job_task_name`，因为时间戳会变，保证每个 job 实例名唯一。

**Step 2: 注册 v3_1**

在 `fast_push_file/__init__.py` 中增加对 v3_1 的 import。

**Step 3: 运行相关测试**

Run: `pytest pipeline_plugins/tests/components/collections/sites/open/job_test/ -k fast_push -v`
Expected: 现有测试通过

**Step 4: Commit**

```bash
git add pipeline_plugins/components/collections/sites/open/job/fast_push_file/
git commit -m "feat: 快速分发文件 v3.1 支持节点名+时间戳作为 job 任务名 --story=xxx"
```

---

## Task 4: 执行作业 v2_1

**Files:**
- Create: `pipeline_plugins/components/collections/sites/open/job/execute_task/v2_1.py`
- Modify: `pipeline_plugins/components/collections/sites/open/job/execute_task/__init__.py`

**Step 1: 创建 v2_1**

复制 `v2_0.py` 为 `v2_1.py`。execute_task 使用 `execute_task_base.py` 的 `plugin_execute`，需在 base 或 v2_1 中注入 task_name。

查看 `execute_task_base.py`：job_kwargs 在 base 中构造，v2_0 继承 base。因此有两种方式：
- A) 修改 `execute_task_base.py` 增加 task_name 逻辑（会影响所有继承 base 的版本）
- B) 在 v2_1 中 override `plugin_execute`，先调用 super，再在调用 API 前修改 job_kwargs

**推荐 B**：v2_1 单独 override，在调用 `client.jobv3.execute_job_plan` 前，给 job_kwargs 增加 task_name。但 base 的 plugin_execute 直接调用了 API，v2_1 若只继承无法插入。因此需要：
- 在 base 的 `plugin_execute` 中，构造 `job_kwargs` 后、调用 `execute_job_plan` 前，增加一个可被子类 override 的 hook，例如 `_inject_job_task_name(self, job_kwargs)`，默认空实现。v2_1 override 该方法注入 task_name。
- 或：在 base 中直接调用 `get_job_task_name` 并注入。但这会使所有版本都使用新逻辑。

**设计文档约定**：仅新版本使用。因此采用：v2_1 继承 v2_0，override `plugin_execute`，复制 base 逻辑并在 job_kwargs 构造后增加 task_name 注入，再调用 API。这样改动最小。

实际上 v2_0 继承 execute_task_base，没有 override plugin_execute。所以 v2_1 需要 override plugin_execute，在 base 逻辑基础上，仅增加 task_name 注入。可以这样：v2_1 继承 v2_0，override plugin_execute，先 `job_kwargs = ...` 构造（复制 base 中的构造逻辑），然后 `task_name = get_job_task_name(...); if task_name: job_kwargs["task_name"] = task_name`，最后调用 API。这样会重复 base 的很多代码。

**更优**：在 execute_task_base 中增加一个方法 `def _get_job_task_name(self): return get_job_task_name(self.root_pipeline_id, self.id)`，然后在 base 的 job_kwargs 构造后增加：
```python
task_name = self._get_job_task_name() if getattr(self, "_use_node_task_name", False) else None
if task_name:
    job_kwargs["task_name"] = task_name
```
v2_1 设置 `_use_node_task_name = True`。这样 base 只需加几行，v2_1 只加一个类属性。

**最简单**：在 execute_task_base 的 job_kwargs 构造后直接加：
```python
task_name = get_job_task_name(self.root_pipeline_id, self.id)
if task_name:
    job_kwargs["task_name"] = task_name
```
这样所有继承 base 的版本都会使用。但设计文档说「仅新版本」。若严格要求仅 v2_1，则需用 hook 或 override。

**折中**：在 base 中加，所有版本都受益（legacy、v1_0、v1_1、v1_2、v2_0、v2_1）。用户若想用旧行为，可继续用旧版本。设计文档说「6 个核心插件新增小版本」，意味着是新版本才有。但「新增小版本」也可以理解为「在新版本中默认开启」，旧版本保持不变。为减少改动，**在 execute_task_base 中直接加**，这样 v2_1 只需继承 v2_0 即可（v2_0 已继承 base，base 改了，v2_0 和 v2_1 都会生效）。但这样 v2_0 也会变，可能不符合「仅新版本」的预期。

**明确设计**：仅 v2_1 有该行为。因此 v2_1 必须 override plugin_execute。可以写一个 mixin：`NodeTaskNameMixin`，提供 `_inject_task_name(job_kwargs)`，v2_1 继承 v2_0 和该 mixin，在 plugin_execute 中调用。但 plugin_execute 是 base 的，v2_1 继承 v2_0，v2_0 没有 override plugin_execute，所以 v2_1 若 override plugin_execute 会完全重写。可以这样：v2_1 的 plugin_execute 调用 `super().plugin_execute(data, parent_data)` 无法在中间插入逻辑。所以必须修改 base，增加一个可选逻辑。用类属性 `inject_node_task_name = False`，base 中 if self.inject_node_task_name: ...。v2_1 设置 inject_node_task_name = True。这样只需改 base 和新增 v2_1。

**最终方案**：在 execute_task_base 的 job_kwargs 构造后增加：
```python
if getattr(self, "use_node_task_name", False):
    task_name = get_job_task_name(self.root_pipeline_id, self.id)
    if task_name:
        job_kwargs["task_name"] = task_name
```
v2_1 设置 `use_node_task_name = True`。v2_1 文件只需继承 v2_0 并加一行类属性，Component version 改为 v2.1。

**Step 2: 修改 execute_task_base**

在 `execute_task_base.py` 的 job_kwargs 构造后、`job_result = client.jobv3.execute_job_plan(job_kwargs)` 前增加上述逻辑。

**Step 3: 创建 v2_1**

v2_1 继承 v2_0，增加 `use_node_task_name = True`，Component version 为 v2.1。

**Step 4: 注册并测试**

**Step 5: Commit**

---

## Task 5: 跨业务快速执行脚本 v1_2

**Files:**
- Create: `pipeline_plugins/components/collections/sites/open/job/all_biz_fast_execute_script/v1_2.py`
- Modify: `pipeline_plugins/components/collections/sites/open/job/all_biz_fast_execute_script/__init__.py`

**逻辑**：all_biz 使用 base_service，在 base 的 job_kwargs 构造后注入 task_name。为保持「仅新版本」，base 增加 `use_node_task_name` 属性，v1_2 设置 True。需修改 base_service。

---

## Task 6: 跨业务快速分发文件 v1_2

**Files:**
- Create: `pipeline_plugins/components/collections/sites/open/job/all_biz_fast_push_file/v1_2.py`
- Modify: `pipeline_plugins/components/collections/sites/open/job/all_biz_fast_push_file/__init__.py`

**逻辑**：同 fast_push_file，batch 调用时每次注入 task_name。

---

## Task 7: 跨业务执行作业 v1_2

**Files:**
- Create: `pipeline_plugins/components/collections/sites/open/job/all_biz_execute_job_plan/v1_2.py`
- Modify: `pipeline_plugins/components/collections/sites/open/job/all_biz_execute_job_plan/__init__.py`

**逻辑**：all_biz_execute_job_plan 有 base_service，在 base 中增加 use_node_task_name，v1_2 设置 True。

---

## 简化说明

为减少重复，建议：
- **execute_task**：在 execute_task_base 增加 `use_node_task_name` 判断，v2_1 设 True
- **all_biz_fast_execute_script**：在 base_service 增加 `use_node_task_name`，v1_2 设 True
- **all_biz_execute_job_plan**：同上
- **fast_execute_script**、**fast_push_file**、**all_biz_fast_push_file**：新版本文件内直接调用 get_job_task_name，不修改 base
