# 标准运维操作审计一期补漏及 API Server 上报实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不新增蓝鲸审计动作和资源的前提下，补齐标准运维页面与 API Server 的一期 P0 操作审计，并为 API Server 灰度配置 `BK_AUDIT_DATA_TOKEN` 做好代码与验证准备。

**Architecture:** 保留 `bk_audit_add_event` 作为最终发送入口，在其上增加事务提交后发送、脱敏快照和统一动作映射。页面与 API Server 只在业务明确成功后调用统一入口；批量操作按实际成功实例逐条上报，没有准确资源映射的插件网关和包源接口继续延期。

**Tech Stack:** Python 3、Django 3.2、Django REST Framework、pytest、`bk-audit` SDK、TAPD 需求 `136920805`。

## Global Constraints

- 设计依据：`docs/specs/2026-08-07-operation-audit-phase1-design.md`。
- TAPD：[136920805 标准运维操作审计一期补漏及 API Server 上报](https://tapd.woa.com/10131351/prong/stories/view/1010131351136920805)。
- 所有提交信息追加 `--story=136920805`。
- 只使用现有 `project`、`flow`、`task`、`common_flow`、`mini_app`、`periodic_task`、`clocked_task` 七类资源及现有动作。
- 业务失败、权限失败、参数失败、异步投递失败和事务回滚不得产生成功审计事件。
- 修改事件只携带脱敏后的前后快照；不得记录密码、Token、密钥、变量值、流程树全文、插件输入输出和日志正文。
- `BK_AUDIT_DATA_TOKEN`、`BK_AUDIT_ENDPOINT` 只由部署环境提供，仓库不写入默认值和真实密钥。
- 不修改 API 请求参数、响应结构、HTTP 状态码和 APIGW schema。
- `plugin_gateway_create_run`、`plugin_gateway_cancel_run`、包源管理/同步、流程市场标签及高频只读接口不在一期接入。
- 当前 `master` 工作区包含用户未提交内容；执行时必须先用独立 worktree 从最新 `upstream/master` 创建功能分支，禁止把现有脏文件带入提交。

---

## 文件结构与职责

**新增文件**

- `gcloud/contrib/audit/mappings.py`：集中维护任务创建、周期任务创建、模板资源/动作选择。
- `gcloud/contrib/audit/operations.py`：按导入/删除结果中的真实成功 ID 逐条注册模板事件。
- `gcloud/tests/contrib/audit/__init__.py`、`test_utils.py`、`test_mappings.py`、`test_page_events.py`：审计底座、映射和页面事件测试。
- `gcloud/tests/template_base/apis/drf/test_template_audit.py`：页面导入和批量删除测试。

**底座修改**

- `gcloud/contrib/audit/utils.py`：事务安全入口、固定错误日志、快照开关短路。
- `gcloud/contrib/audit/instances.py`：支持明确的前后快照输入并保持旧调用兼容。
- `gcloud/contrib/audit/serializers.py`：收紧审计字段，移除敏感和大字段。

**页面入口修改**

- `gcloud/core/apis/drf/viewsets/project.py`、`appmaker.py`、`periodic_task.py`、`project_config.py`、`taskflow.py`。
- `gcloud/clocked_task/viewset.py`、`gcloud/periodictask/api.py`。
- `gcloud/taskflow3/apis/django/api.py`、`v4/node_action.py`、`gcloud/taskflow3/apis/drf/viewsets/update_task_constants.py`。
- `gcloud/contrib/function/api.py`、`gcloud/template_base/apis/django/api.py`、`gcloud/template_base/apis/drf/viewsets/template.py`。

**API Server 入口修改**

- 任务：`create_task.py`、`create_and_start_task.py`、`fast_create_task.py`、`start_task.py`、`operate_task.py`、`operate_node.py`、`node_callback.py`、`modify_constants_for_task.py`。
- 调度：`create_periodic_task.py`、`set_periodic_task_enabled.py`、`modify_cron_for_periodic_task.py`、`modify_constants_for_periodic_task.py`、`create_clocked_task.py`。
- 流程/项目：`create_template.py`、`import_project_template.py`、`import_common_template.py`、`copy_template_across_project.py`、`register_project.py`、`claim_functionalization_task.py`、`apply_webhook_configs.py`、`modify_project_executor_proxy.py`、`modify_template_notify.py`、`modify_template_executor_proxy.py`。
- API Server 测试文件在 Task 5-7 的 Files 段逐项列出；当前不存在的文件按对应接口名创建。

---

### Task 1: 建立事务安全、脱敏且向后兼容的审计底座

**Files:**

- Create: `gcloud/tests/contrib/audit/__init__.py`
- Create: `gcloud/tests/contrib/audit/test_utils.py`
- Modify: `gcloud/contrib/audit/utils.py`
- Modify: `gcloud/contrib/audit/instances.py`
- Modify: `gcloud/contrib/audit/serializers.py`

**Interfaces:**

- Produces: `sanitize_audit_data(data: Any) -> Any`
- Produces: `AuditSnapshot(dict)`，用于标记已经由审计序列化器生成并脱敏的修改前数据。
- Produces: `get_audit_snapshot(resource_id: str, instance: Model, data: dict = None) -> Optional[dict]`
- Produces: `bk_audit_add_event_on_commit(username: str, action_id: str, resource_id: str = None, instance: Model = None, origin_data: dict = None, data: dict = None) -> None`
- Preserves: `bk_audit_add_event(username, action_id, resource_id=None, instance=None, origin_data=None, *args, **kwargs)`

- [ ] **Step 1: 写开关、事务和异常隔离失败测试**

```python
from unittest import mock

from django.test import TestCase, override_settings

from gcloud.contrib.audit import utils


class AuditEventOnCommitTestCase(TestCase):
    @override_settings(ENABLE_BK_AUDIT=False)
    @mock.patch("gcloud.contrib.audit.utils.build_instance")
    def test_disabled_does_not_build_or_register_event(self, build_instance):
        utils.bk_audit_add_event_on_commit("admin", "task_edit", "task", mock.Mock(id=1))
        build_instance.assert_not_called()

    @override_settings(ENABLE_BK_AUDIT=True)
    @mock.patch("gcloud.contrib.audit.utils.bk_audit_add_event")
    def test_commit_sends_once(self, add_event):
        with self.captureOnCommitCallbacks(execute=True):
            utils.bk_audit_add_event_on_commit("admin", "task_edit", "task", mock.Mock(id=1))
        add_event.assert_called_once()

    @override_settings(ENABLE_BK_AUDIT=True)
    @mock.patch("gcloud.contrib.audit.utils.bk_audit_add_event")
    def test_rollback_does_not_send(self, add_event):
        from django.db import transaction

        try:
            with transaction.atomic():
                utils.bk_audit_add_event_on_commit("admin", "task_edit", "task", mock.Mock(id=1))
                raise RuntimeError("rollback")
        except RuntimeError:
            pass
        add_event.assert_not_called()
```

再增加客户端抛异常用例，断言调用方不抛异常且日志包含 `bk_audit_add_event_failed action_id=task_edit resource_id=task instance_id=1`，日志中不包含请求体和 Token。

- [ ] **Step 2: 运行底座测试确认失败**

Run: `pytest -q gcloud/tests/contrib/audit/test_utils.py`

Expected: FAIL，原因是三个新接口尚不存在。

- [ ] **Step 3: 实现开关短路、事务提交后发送和安全日志**

```python
from functools import partial

from django.db import transaction


def bk_audit_add_event_on_commit(
    username, action_id, resource_id=None, instance=None, origin_data=None, data=None
):
    if not settings.ENABLE_BK_AUDIT:
        return
    transaction.on_commit(
        partial(
            bk_audit_add_event,
            username=username,
            action_id=action_id,
            resource_id=resource_id,
            instance=instance,
            origin_data=origin_data,
            data=data,
        )
    )
```

`bk_audit_add_event` 继续吞掉 SDK 异常，但日志只输出 action/resource/instance ID 和异常栈，不再格式化整个实例。

```python
instance_id = getattr(instance, "id", None)
try:
    audit_instance = build_instance(resource_id, instance, origin_data=origin_data, data=data)
    bk_audit_client.add_event(
        action=Action(action_id),
        resource_type=ResourceType(resource_id) if resource_id else None,
        audit_context=AuditContext(username=username),
        instance=audit_instance,
    )
except Exception:
    logger.exception(
        "bk_audit_add_event_failed action_id=%s resource_id=%s instance_id=%s",
        action_id,
        resource_id,
        instance_id,
    )
```

- [ ] **Step 4: 实现快照覆盖和递归脱敏**

`BaseInstance` 新增可选 `data`；未传时保持旧序列化行为。`get_audit_snapshot` 返回 `AuditSnapshot`；各资源的 `prepare_origin_data` 遇到该标记时直接使用其中的安全字段，只有旧调用传入普通 dict 时才继续走原有请求 serializer 校验。这样新快照不会被 `UpdatePeriodicTaskSerializer` 等旧请求格式再次校验，旧调用也不改变语义。

`sanitize_audit_data` 对 `pipeline_tree`、`constants`、`form`、`task_parameters`、`inputs`、`outputs`、`headers`、`extra_info` 整项移除，对 key 名含 `password`、`token`、`secret`、`credential` 的值替换为 `******`，对列表和嵌套字典递归处理。`get_audit_snapshot` 在开关关闭时直接返回 `None`，开启时读取实例审计序列化数据、脱敏并包装为 `AuditSnapshot`。

- [ ] **Step 5: 收紧资源序列化字段**

将 `TaskSerializer` 从 `fields = "__all__"` 改为明确字段：`id`、`name`、`project`、`category`、`template_id`、`template_source`、`create_method`、`creator_name`、`executor_name`、`flow_type`、`current_flow`、`is_started`、`is_finished`、`is_revoked`、`create_time`、`start_time`、`finish_time`。从 `PeriodicTaskSerializer` 移除 `form`，计划任务审计数据移除 `task_parameters`。

测试构造含 password、Authorization header、constants 和 pipeline_tree 的嵌套数据，断言事件与日志均不含对应值。

- [ ] **Step 6: 运行底座测试并提交**

Run: `pytest -q gcloud/tests/contrib/audit/test_utils.py`

Expected: PASS，事务提交一次、回滚零次、开关关闭零次、SDK 异常不影响调用方。

```bash
git add gcloud/contrib/audit/utils.py gcloud/contrib/audit/instances.py gcloud/contrib/audit/serializers.py gcloud/tests/contrib/audit
git commit -m "feat(audit): add transaction-safe event delivery --story=136920805"
```

---

### Task 2: 集中现有动作和资源映射

**Files:**

- Create: `gcloud/contrib/audit/mappings.py`
- Create: `gcloud/tests/contrib/audit/test_mappings.py`
- Modify: `gcloud/core/apis/drf/viewsets/taskflow.py`
- Modify: `gcloud/core/apis/drf/viewsets/periodic_task.py`

**Interfaces:**

- Produces: `get_task_create_action(template_source: str, create_method: str = None) -> Optional[str]`
- Produces: `get_periodic_task_create_action(template_source: str) -> Optional[str]`
- Produces: `get_template_audit_meta(template_model_cls: type) -> Tuple[str, str, str]`，依次返回 create/delete/resource ID。

- [ ] **Step 1: 写完整映射失败测试**

```python
import pytest

from gcloud.common_template.models import CommonTemplate
from gcloud.constants import COMMON, ONETIME, PROJECT
from gcloud.iam_auth import IAMMeta
from gcloud.tasktmpl3.models import TaskTemplate

from gcloud.contrib.audit.mappings import (
    get_periodic_task_create_action,
    get_task_create_action,
    get_template_audit_meta,
)


@pytest.mark.parametrize(
    "source,method,expected",
    [
        (PROJECT, None, IAMMeta.FLOW_CREATE_TASK_ACTION),
        (COMMON, None, IAMMeta.COMMON_FLOW_CREATE_TASK_ACTION),
        (ONETIME, None, IAMMeta.PROJECT_FAST_CREATE_TASK_ACTION),
        (PROJECT, "app_maker", IAMMeta.MINI_APP_CREATE_TASK_ACTION),
        ("unknown", None, None),
    ],
)
def test_task_create_action(source, method, expected):
    assert get_task_create_action(source, method) == expected


def test_template_meta_uses_existing_resources():
    assert get_template_audit_meta(TaskTemplate) == (
        IAMMeta.FLOW_CREATE_ACTION,
        IAMMeta.FLOW_DELETE_ACTION,
        IAMMeta.FLOW_RESOURCE,
    )
    assert get_template_audit_meta(CommonTemplate) == (
        IAMMeta.COMMON_FLOW_CREATE_ACTION,
        IAMMeta.COMMON_FLOW_DELETE_ACTION,
        IAMMeta.COMMON_FLOW_RESOURCE,
    )
```

同时断言 PROJECT/COMMON 周期任务分别映射到 `FLOW_CREATE_PERIODIC_TASK_ACTION` 和 `COMMON_FLOW_CREATE_PERIODIC_TASK_ACTION`；未知来源返回 `None`。

- [ ] **Step 2: 运行映射测试确认失败**

Run: `pytest -q gcloud/tests/contrib/audit/test_mappings.py`

Expected: FAIL，模块尚不存在。

- [ ] **Step 3: 实现映射并替换页面重复字典**

`mappings.py` 只依赖 constants、IAMMeta 和模板模型，不访问请求或数据库。页面任务创建与周期任务创建改为调用映射函数；返回 `None` 时跳过审计并记录 warning，不能回退到项目流程动作。

- [ ] **Step 4: 运行测试并提交**

Run: `pytest -q gcloud/tests/contrib/audit/test_mappings.py gcloud/tests/core/apis/drf/views_set/test_task_instance_view.py`

Expected: PASS。

```bash
git add gcloud/contrib/audit/mappings.py gcloud/tests/contrib/audit/test_mappings.py gcloud/core/apis/drf/viewsets/taskflow.py gcloud/core/apis/drf/viewsets/periodic_task.py
git commit -m "refactor(audit): centralize existing action mappings --story=136920805"
```

---

### Task 3: 修正首版页面审计时机并补齐页面任务类 P0

**Files:**

- Create: `gcloud/tests/contrib/audit/test_page_events.py`
- Modify: `gcloud/core/apis/drf/viewsets/project.py`、`appmaker.py`、`taskflow.py`
- Modify: `gcloud/taskflow3/apis/django/api.py`、`v4/node_action.py`
- Modify: `gcloud/taskflow3/apis/drf/viewsets/update_task_constants.py`
- Modify: `gcloud/contrib/function/api.py`

**Interfaces:**

- Consumes: `get_audit_snapshot`、`bk_audit_add_event_on_commit`。
- Produces: 页面任务操作只有 `result is True` 时发送现有动作事件。

- [ ] **Step 1: 写成功/失败及时序回归测试**

逐一 patch 所在模块的 `bk_audit_add_event_on_commit`：

| 入口 | 成功动作 | 失败断言 |
| --- | --- | --- |
| `ProjectSetViewSet.update` | `project_edit/project`，带修改前快照 | serializer 抛错时零次 |
| `AppmakerListViewSet.destroy` | `mini_app_delete/mini_app` | 删除抛错时零次 |
| `task_action` | `task_operate/task` | `ctx["result"] is False` 时零次 |
| `nodes_action`、V4 `node_action`、`spec_nodes_timer_reset` | `task_operate/task` | 模型返回失败时零次 |
| `UpdateTaskConstantsView.post` | `task_edit/task` | `set_result["result"] is False` 时零次 |
| `FunctionTaskClaimantTransferView.post` | `task_claim/task` | 权限/认领人不匹配时零次 |
| `convert_to_common_task` | `task_edit/task` | creator/current_flow 校验失败时零次 |
| `task_func_claim` | `task_claim/task` | `ctx["result"] is False` 时零次 |

成功测试使用 `captureOnCommitCallbacks(execute=True)`，断言 username、action、resource、instance 和调用次数。项目、任务参数和职能任务转换断言 origin 存在且不含变量值。

- [ ] **Step 2: 运行页面任务测试确认失败**

Run: `pytest -q gcloud/tests/contrib/audit/test_page_events.py`

Expected: FAIL，现有项目/删除事件提前发送，节点和参数入口缺少事件，任务操作失败仍发送。

- [ ] **Step 3: 将已有调用移动到成功结果之后**

- `ProjectSetViewSet.update`：父类调用前捕获 origin，成功返回后取得当前实例并注册 `project_edit`。
- `AppmakerListViewSet.destroy`：先执行删除；成功后使用删除前实例注册 `mini_app_delete`。
- `task_action`、`task_func_claim`：仅在 `ctx.get("result") is True` 时注册。

- [ ] **Step 4: 为节点、参数和职能任务增加成功事件**

```python
ctx = task.nodes_action(action, node_id, username, **kwargs)
if ctx.get("result") is True:
    bk_audit_add_event_on_commit(
        username=request.user.username,
        action_id=IAMMeta.TASK_OPERATE_ACTION,
        resource_id=IAMMeta.TASK_RESOURCE,
        instance=task,
    )
return JsonResponse(ctx)
```

任务参数修改在 `set_task_constants` 前捕获快照，成功后上报 `task_edit`。职能任务转交通过 FunctionTask 找到关联 task 后上报 `task_claim`，不能把 FunctionTask ID 当作 task ID。`convert_to_common_task` 的注册放在 `transaction.atomic()` 内并依赖 on-commit。

- [ ] **Step 5: 运行测试并提交**

Run: `pytest -q gcloud/tests/contrib/audit/test_page_events.py gcloud/tests/taskflow3/test_api.py`

Expected: PASS。

```bash
git add gcloud/core/apis/drf/viewsets/project.py gcloud/core/apis/drf/viewsets/appmaker.py gcloud/core/apis/drf/viewsets/taskflow.py gcloud/taskflow3/apis/django/api.py gcloud/taskflow3/apis/django/v4/node_action.py gcloud/taskflow3/apis/drf/viewsets/update_task_constants.py gcloud/contrib/function/api.py gcloud/tests/contrib/audit/test_page_events.py
git commit -m "feat(audit): cover page task operations after success --story=136920805"
```

---

### Task 4: 补齐页面计划任务、周期任务、项目代理和流程批量操作

**Files:**

- Modify: `gcloud/clocked_task/viewset.py`
- Modify: `gcloud/periodictask/api.py`
- Modify: `gcloud/core/apis/drf/viewsets/periodic_task.py`、`project_config.py`
- Modify: `gcloud/template_base/apis/django/api.py`、`gcloud/template_base/apis/drf/viewsets/template.py`
- Create: `gcloud/contrib/audit/operations.py`
- Modify: `gcloud/tests/clocked_task/test_clocked_task_api.py`、`gcloud/tests/periodictask/models/test_periodic_task.py`
- Create: `gcloud/tests/template_base/apis/drf/test_template_audit.py`

**Interfaces:**

- Consumes: 事务安全入口和模板动作映射。
- Produces: `audit_imported_templates(username, template_model_cls, import_result) -> None`，只遍历 `import_result["data"]["flows"]` 中的真实落库 ID。
- Produces: `audit_deleted_templates(username, template_model_cls, instances_by_id, success_ids) -> None`。

- [ ] **Step 1: 写调度、项目配置和模板批量测试**

- 计划任务：create=`flow_create_clocked_task`、retrieve=`clocked_task_view`、update=`clocked_task_edit`、destroy=`clocked_task_delete`，资源均为 `clocked_task`；update/destroy 失败零事件，update origin 不含 `task_parameters`。
- 页面周期任务：启停、Cron、constants 修改成功均发送 `periodic_task_edit/periodic_task`，失败零次；destroy 在删除成功后发送；创建动作按 template_source 区分项目/公共流程。
- 项目执行代理：`ProjectConfigViewSet.update` 成功发送 `project_edit/project`，data 只含 `executor_proxy`、`executor_proxy_exempts`。
- 页面导入：项目/公共模板分别发送 `flow_create/flow`、`common_flow_create/common_flow`，只查询 flows 返回 ID。
- 批量删除：只对 `result["data"]["success"]` 中的删除前实例发送对应 delete 动作；fail 列表、Webhook 清理失败和 manager 失败均零事件。

- [ ] **Step 2: 运行测试确认失败**

Run: `pytest -q gcloud/tests/clocked_task/test_clocked_task_api.py gcloud/tests/periodictask/models/test_periodic_task.py gcloud/tests/template_base/apis/drf/test_template_audit.py`

Expected: FAIL，目标入口尚未完整接入事务安全审计。

- [ ] **Step 3: 实现按实际成功实例上报**

在 `operations.py` 实现两个批量助手。导入助手先检查 `import_result.get("result") is True`，再把 `flows.keys()` 转为整数并查询目标模型；删除助手只遍历 success ID。两个助手都通过 `get_template_audit_meta` 取得现有动作/资源，不能接受调用方任意传 action。

```python
def audit_imported_templates(username, template_model_cls, import_result):
    if import_result.get("result") is not True:
        return
    create_action, _, resource_id = get_template_audit_meta(template_model_cls)
    template_ids = [int(template_id) for template_id in import_result["data"]["flows"]]
    for instance in template_model_cls.objects.filter(id__in=template_ids):
        bk_audit_add_event_on_commit(
            username=username,
            action_id=create_action,
            resource_id=resource_id,
            instance=instance,
        )
```

批量删除在 manager 调用前保存 `{instance.id: instance}`，成功后只遍历 success ID；导入事件使用 flows keys 查询导入后模板，不使用导入文件旧 ID。项目执行代理用 Project 作审计实例，手工构造代理与豁免用户前后小快照。

```python
for template_id in result["data"]["success"]:
    instance = instances[template_id]
    bk_audit_add_event_on_commit(
        username=request.user.username,
        action_id=delete_action,
        resource_id=resource_id,
        instance=instance,
        origin_data=get_audit_snapshot(resource_id, instance),
        data={"id": template_id, "is_deleted": True},
    )
```

- [ ] **Step 4: 运行测试并提交**

Run: `pytest -q gcloud/tests/clocked_task/test_clocked_task_api.py gcloud/tests/periodictask/models/test_periodic_task.py gcloud/tests/template_base/apis/drf/test_template_audit.py`

Expected: PASS。

```bash
git add gcloud/contrib/audit/operations.py gcloud/clocked_task/viewset.py gcloud/periodictask/api.py gcloud/core/apis/drf/viewsets/periodic_task.py gcloud/core/apis/drf/viewsets/project_config.py gcloud/template_base/apis/django/api.py gcloud/template_base/apis/drf/viewsets/template.py gcloud/tests/clocked_task/test_clocked_task_api.py gcloud/tests/periodictask/models/test_periodic_task.py gcloud/tests/template_base/apis/drf/test_template_audit.py
git commit -m "feat(audit): cover page schedules and template batches --story=136920805"
```

---

### Task 5: 补齐 API Server 任务生命周期 P0

**Files:**

- Modify: `gcloud/apigw/views/create_task.py`、`create_and_start_task.py`、`fast_create_task.py`、`start_task.py`
- Modify: `gcloud/apigw/views/operate_task.py`、`operate_node.py`、`node_callback.py`、`modify_constants_for_task.py`
- Modify: `gcloud/tests/apigw/views/test_create_task.py`、`test_create_and_start_task.py`、`test_start_task.py`、`test_operate_task.py`、`test_operate_node.py`、`test_node_callback.py`
- Create: `gcloud/tests/apigw/views/test_fast_create_task.py`、`test_modify_constants_for_task.py`

**Interfaces:**

- Consumes: `get_task_create_action`、`get_audit_snapshot`、`bk_audit_add_event_on_commit`。
- Produces: 任务事件均使用实际 `TaskFlowInstance.id`，scope 使用已解析的 `request.project`。

- [ ] **Step 1: 为八个任务接口写审计断言**

| 接口 | action/resource | 成功条件 |
| --- | --- | --- |
| `create_task` | project/common 对应 create-task，`task` | task 已创建 |
| `create_and_start_task` | create-task + `task_operate`，`task` | task 落库，`apply_async` 返回后各一次 |
| `fast_create_task` | `project_fast_create_task/task` | task 已创建 |
| `start_task` | `task_operate/task` | `apply_async` 成功返回 |
| `operate_task` | `task_operate/task` | start 投递成功或其他分支 `ctx.result=True` |
| `operate_node` | `task_operate/task` | `result.result=True` |
| `node_callback` | `task_operate/task` | callback `result=True` |
| `modify_constants_for_task` | `task_edit/task` | reset `result=True` |

失败测试覆盖模板/任务不存在、任务已启动、模型返回 `result=False`、`apply_async` 抛异常。`create_and_start_task` 投递失败允许记录已完成的创建事件，但不得记录 `task_operate`。

`create_task` 和 `start_task` 各增加两组 project-inject 用例：路由传 CMDB 业务 ID 与传内部项目 ID 时，审计实例都必须是注入后查询得到的 TaskFlowInstance，不能把原始路由值当作资源 ID。

- [ ] **Step 2: 运行任务测试确认失败**

Run: `pytest -q gcloud/tests/apigw/views/test_create_task.py gcloud/tests/apigw/views/test_create_and_start_task.py gcloud/tests/apigw/views/test_start_task.py gcloud/tests/apigw/views/test_operate_task.py gcloud/tests/apigw/views/test_operate_node.py gcloud/tests/apigw/views/test_node_callback.py`

Expected: FAIL，审计调用尚未补齐。

- [ ] **Step 3: 在真实成功点注册事件**

创建事件紧跟 TaskFlowInstance 持久化；启动事件紧跟各文件中现有的 `prepare_and_start_task.apply_async` 调用成功返回；模型业务方法必须检查 `result.get("result") is True`。`create_and_start_task` 注册创建和启动两个事件。constants 修改前捕获 origin，不能把请求 constants 传给审计。

- [ ] **Step 4: 补缺失测试文件并运行全部任务测试**

创建 `test_fast_create_task.py` 和 `test_modify_constants_for_task.py`；验证 action/resource/instance/call-count 和失败零事件。

Run: `pytest -q gcloud/tests/apigw/views/test_create_task.py gcloud/tests/apigw/views/test_create_and_start_task.py gcloud/tests/apigw/views/test_fast_create_task.py gcloud/tests/apigw/views/test_start_task.py gcloud/tests/apigw/views/test_operate_task.py gcloud/tests/apigw/views/test_operate_node.py gcloud/tests/apigw/views/test_node_callback.py gcloud/tests/apigw/views/test_modify_constants_for_task.py`

Expected: PASS，原请求/响应断言不变。

- [ ] **Step 5: 提交**

```bash
git add gcloud/apigw/views/create_task.py gcloud/apigw/views/create_and_start_task.py gcloud/apigw/views/fast_create_task.py gcloud/apigw/views/start_task.py gcloud/apigw/views/operate_task.py gcloud/apigw/views/operate_node.py gcloud/apigw/views/node_callback.py gcloud/apigw/views/modify_constants_for_task.py gcloud/tests/apigw/views
git commit -m "feat(audit): cover api server task operations --story=136920805"
```

---

### Task 6: 补齐 API Server 周期任务和计划任务 P0

**Files:**

- Modify: `gcloud/apigw/views/create_periodic_task.py`、`set_periodic_task_enabled.py`
- Modify: `gcloud/apigw/views/modify_cron_for_periodic_task.py`、`modify_constants_for_periodic_task.py`
- Modify: `gcloud/apigw/views/create_clocked_task.py`
- Modify: `gcloud/tests/apigw/views/test_create_periodic_task.py`、`test_set_periodic_task_enabled.py`、`test_modify_cron_for_periodic_task.py`、`test_modify_constants_for_periodic_task.py`
- Create: `gcloud/tests/apigw/views/test_create_clocked_task.py`

**Interfaces:**

- Consumes: 周期任务创建映射、快照、on-commit 发送。

- [ ] **Step 1: 写调度接口成功和失败测试**

- `create_periodic_task`：project/common 分别断言 `flow_create_periodic_task`/`common_flow_create_periodic_task`，资源 `periodic_task`。
- 启停、Cron、constants 修改：断言 `periodic_task_edit/periodic_task`，模型异常或业务失败零次。
- `create_clocked_task`：断言 `flow_create_clocked_task/clocked_task`；模板不存在和 serializer 失败零次。
- constants 与计划任务参数不得出现在 origin/current。

- [ ] **Step 2: 运行调度测试确认失败**

Run: `pytest -q gcloud/tests/apigw/views/test_create_periodic_task.py gcloud/tests/apigw/views/test_set_periodic_task_enabled.py gcloud/tests/apigw/views/test_modify_cron_for_periodic_task.py gcloud/tests/apigw/views/test_modify_constants_for_periodic_task.py gcloud/tests/apigw/views/test_create_clocked_task.py`

Expected: FAIL；若最后一个测试文件当前不存在，先创建同名 APITest 文件。

- [ ] **Step 3: 在调度持久化成功后注册事件**

修改类在调用模型方法前取快照，成功后注册 `periodic_task_edit`；创建类只传实际创建实例。`request.project.id` 只用于 scope，审计实例 ID 使用 PeriodicTask/ClockedTask 自身 ID。

- [ ] **Step 4: 运行测试并提交**

Run: `pytest -q gcloud/tests/apigw/views/test_create_periodic_task.py gcloud/tests/apigw/views/test_set_periodic_task_enabled.py gcloud/tests/apigw/views/test_modify_cron_for_periodic_task.py gcloud/tests/apigw/views/test_modify_constants_for_periodic_task.py gcloud/tests/apigw/views/test_create_clocked_task.py`

Expected: PASS。

```bash
git add gcloud/apigw/views/create_periodic_task.py gcloud/apigw/views/set_periodic_task_enabled.py gcloud/apigw/views/modify_cron_for_periodic_task.py gcloud/apigw/views/modify_constants_for_periodic_task.py gcloud/apigw/views/create_clocked_task.py gcloud/tests/apigw/views
git commit -m "feat(audit): cover api server scheduled tasks --story=136920805"
```

---

### Task 7: 补齐 API Server 流程、项目和配置 P0

**Files:**

- Modify: `gcloud/apigw/views/create_template.py`、`import_project_template.py`、`import_common_template.py`、`copy_template_across_project.py`
- Modify: `gcloud/apigw/views/register_project.py`、`claim_functionalization_task.py`、`apply_webhook_configs.py`、`modify_project_executor_proxy.py`
- Modify: `gcloud/apigw/views/modify_template_notify.py`、`modify_template_executor_proxy.py`
- Modify: `gcloud/tests/apigw/views/test_import_common_template.py`、`test_apply_webhook_configs.py`、`test_modify_template_notify.py`、`test_modify_template_executor_proxy.py`
- Create: `gcloud/tests/apigw/views/test_create_template.py`、`test_import_project_template.py`、`test_copy_template_across_project.py`、`test_register_project.py`、`test_claim_functionalization_task.py`、`test_modify_project_executor_proxy.py`

**Interfaces:**

- Consumes: 模板映射、快照、批量成功实例逻辑、on-commit 发送。
- Produces: Webhook 快照只含模板 ID、enable 状态和事件类型集合。

- [ ] **Step 1: 写流程导入/复制和已有入口回归测试**

- 项目导入/跨项目复制只对 `flows` 目标 ID 发送 `flow_create/flow`；公共导入发送 `common_flow_create/common_flow`。
- import `result=False` 或异常时零事件。
- `create_template`、`modify_template_notify`、`modify_template_executor_proxy` 保持原 action/resource，改为 on-commit；失败零事件，修改有 origin。

- [ ] **Step 2: 写项目、认领、Webhook 和执行代理测试**

| 接口 | action/resource | 数据限制 |
| --- | --- | --- |
| `register_project` | `project_edit/project` | 新建/恢复后的内部 Project |
| `claim_functionalization_task` | `task_claim/task` | 仅 `task_claim().result=True` |
| `apply_webhook_configs` | 每个受影响模板 `flow_edit/flow` | 不含 endpoint、headers、extra_info |
| `modify_project_executor_proxy` | `project_edit/project` | 仅代理与豁免用户前后值 |

Webhook disable-all 使用真实模板 ID 集合；创建/更新使用最终受影响 scope_code 查询 TaskTemplate。事务回滚时零事件。

- [ ] **Step 3: 运行流程/项目测试确认失败**

Run: `pytest -q gcloud/tests/apigw/views/test_import_project_template.py gcloud/tests/apigw/views/test_import_common_template.py gcloud/tests/apigw/views/test_copy_template_across_project.py gcloud/tests/apigw/views/test_apply_webhook_configs.py gcloud/tests/apigw/views/test_modify_template_notify.py gcloud/tests/apigw/views/test_modify_template_executor_proxy.py`

Expected: FAIL；创建当前缺失的 `test_copy_template_across_project.py`、`test_register_project.py`、`test_claim_functionalization_task.py`、`test_modify_project_executor_proxy.py`。

- [ ] **Step 4: 实现批量成功实例和安全 Webhook 快照**

导入/复制根据 `flows.keys()` 查询目标模型，不使用源 ID。Webhook 只构造以下数据：

```python
data = {
    "template_id": template.id,
    "webhook_enabled": enabled,
    "event_types": sorted(event_types),
}
```

禁止传 endpoint、headers、extra_info。项目注册必须在 CC 查询、项目保存和配置初始化均成功后注册事件。

- [ ] **Step 5: 运行测试并提交**

Run: `pytest -q gcloud/tests/apigw/views/test_import_project_template.py gcloud/tests/apigw/views/test_import_common_template.py gcloud/tests/apigw/views/test_copy_template_across_project.py gcloud/tests/apigw/views/test_register_project.py gcloud/tests/apigw/views/test_claim_functionalization_task.py gcloud/tests/apigw/views/test_apply_webhook_configs.py gcloud/tests/apigw/views/test_modify_project_executor_proxy.py gcloud/tests/apigw/views/test_modify_template_notify.py gcloud/tests/apigw/views/test_modify_template_executor_proxy.py`

Expected: PASS。

```bash
git add gcloud/apigw/views gcloud/tests/apigw/views
git commit -m "feat(audit): cover api server flow and project writes --story=136920805"
```

---

### Task 8: 全局回归、延期边界和 Token 灰度验收

**Files:**

- Modify: `docs/specs/2026-08-07-operation-audit-phase1-design.md`（只追加 TAPD 与最终验证结果）
- Verify only: `config/default.py`、`gcloud/apigw/management/commands/data/api-resources.yml`、插件网关与包源路径

**Interfaces:**

- Produces: 测试证据和 API Server Token 灰度检查单。

- [ ] **Step 1: 运行一期定向回归**

```bash
pytest -q \
  gcloud/tests/contrib/audit \
  gcloud/tests/clocked_task/test_clocked_task_api.py \
  gcloud/tests/apigw/views/test_create_task.py \
  gcloud/tests/apigw/views/test_create_and_start_task.py \
  gcloud/tests/apigw/views/test_start_task.py \
  gcloud/tests/apigw/views/test_operate_task.py \
  gcloud/tests/apigw/views/test_operate_node.py \
  gcloud/tests/apigw/views/test_node_callback.py \
  gcloud/tests/apigw/views/test_create_periodic_task.py \
  gcloud/tests/apigw/views/test_set_periodic_task_enabled.py \
  gcloud/tests/apigw/views/test_modify_cron_for_periodic_task.py \
  gcloud/tests/apigw/views/test_modify_constants_for_periodic_task.py \
  gcloud/tests/apigw/views/test_import_common_template.py \
  gcloud/tests/apigw/views/test_apply_webhook_configs.py \
  gcloud/tests/apigw/views/test_modify_template_notify.py \
  gcloud/tests/apigw/views/test_modify_template_executor_proxy.py
```

Expected: 全部 PASS。

- [ ] **Step 2: 运行格式、静态与差异检查**

```bash
black --check gcloud/contrib/audit gcloud/apigw/views gcloud/clocked_task gcloud/periodictask gcloud/taskflow3/apis gcloud/tests/contrib/audit gcloud/tests/apigw/views
flake8 --config=.flake8 gcloud/contrib/audit gcloud/apigw/views gcloud/clocked_task gcloud/periodictask gcloud/taskflow3/apis gcloud/tests/contrib/audit gcloud/tests/apigw/views
git diff --check
```

Expected: 三条命令均退出 0。

- [ ] **Step 3: 核对无 schema 变化、无错误映射、无密钥**

```bash
git diff --exit-code upstream/master -- gcloud/apigw/management/commands/data/api-resources.yml
git diff upstream/master -- gcloud/apigw/views/plugin_gateway.py gcloud/core/apis/drf/viewsets/package_source.py gcloud/core/apis/drf/viewsets/sync_task.py
if git diff upstream/master | rg -n "BK_AUDIT_DATA_TOKEN\s*=\s*['\"][^'\"]+|BK_AUDIT_ENDPOINT\s*=\s*['\"]https?://|plugin_gateway_(create|cancel).*bk_audit|package_source.*bk_audit"; then exit 1; fi
```

Expected: APIGW YAML 无差异；延期文件无审计改动；最后一条无匹配。真实 Token 不进入终端输出、fixture 或提交。

- [ ] **Step 4: 记录代码验证结果并提交文档**

在设计文档末尾追加 TAPD `136920805`、实际测试命令及通过数量；预发布/生产标记为“待环境灰度”，不能把单元测试写成审计中心实收证明。

```bash
git add docs/specs/2026-08-07-operation-audit-phase1-design.md docs/plans/2026-08-07-operation-audit-phase1.md
git commit -m "docs(audit): record phase one verification plan --story=136920805"
```

- [ ] **Step 5: 代码合入和部署后执行 API Server Token 灰度**

1. Token 为空部署一期代码，确认业务行为与现状一致。
2. 预发布 API Server 配置 `BK_AUDIT_ENDPOINT` 与 `BK_AUDIT_DATA_TOKEN`，滚动重启。
3. 对任务创建、任务操作、周期任务修改、流程导入、项目代理修改分别执行一次成功和一次失败请求。
4. 在审计中心核对成功事件，确认失败请求无成功事件；抽样核对 username、action ID、resource ID、instance ID。
5. 搜索 `bk_audit_add_event_failed`，确认无 Token、请求体和敏感值。
6. 生产只在少量 API Server 实例配置 Token；对照访问日志与审计中心事件数量后再全量。
7. 页面模块和 Worker 的 Token 状态分别核验，不能以 API Server 已开启代替全站已开启。

Expected: 预发布实收与访问日志抽样一致后才允许生产灰度；异常时回退环境变量并保留代码，不提交密钥变更。
