# Audit Proxy Extend Data Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在可信 PO 委托审计事件中，将任务代理执行人 B 上报为 `extend_data.proxy_username`，同时保持审计操作人 A、IAM 权限主体 B 和任务执行人 B 的现有语义。

**Architecture:** 保留 `get_audit_username(request)` 作为唯一委托信任判断，新建 `get_audit_event_kwargs(request)` 组合标准 `username` 与可选 `extend_data`。审计通用入口显式接收、脱敏并透传 `extend_data`，三个已支持 PO 委托的 APIGW 写入口统一解包该事件参数。

**Tech Stack:** Python 3.6、Django 3.2、bk-audit 1.1.1、unittest/mock、pre-commit。

## Global Constraints

- 设计规格：`docs/specs/2026-08-11-audit-proxy-extend-data-design.md`。
- 仅可信委托生效、代理执行人非空且 A 与 B 不同时生成 `extend_data.proxy_username`。
- 普通调用、回退调用及 A 与 B 相同的调用不携带代理字段。
- 不修改 PO Facade Header 协议、IAM 权限主体、任务执行人、审计动作或资源。
- `extend_data` 必须经过现有 `sanitize_audit_data` 脱敏。
- 所有提交关联 TAPD 需求 `136920805`。

---

### Task 1: 生成委托审计事件身份参数

**Files:**
- Modify: `gcloud/contrib/audit/utils.py:65-100`
- Test: `gcloud/tests/contrib/audit/test_utils.py:12-59`

**Interfaces:**
- Consumes: `get_audit_username(request) -> str`，继续负责应用白名单、应用认证和委托用户名格式校验。
- Produces: `get_audit_event_kwargs(request) -> dict`，固定返回 `username` 和 `extend_data` 两个键。

- [ ] **Step 1: 写入会捕获“可信委托未携带代理字段”的失败测试**

在 `DelegatedAuditUsernameTestCase` 中新增：

```python
@override_settings(BK_AUDIT_DELEGATED_OPERATOR_APPS={"bk-sops-facade"})
def test_event_kwargs_include_proxy_for_passwordless_trusted_delegation(self):
    self.assertEqual(
        utils.get_audit_event_kwargs(
            self.request(operator="alice", proxy="executor", verified=False)
        ),
        {
            "username": "alice",
            "extend_data": {"proxy_username": "executor"},
        },
    )

@override_settings(BK_AUDIT_DELEGATED_OPERATOR_APPS={"bk-sops-facade"})
def test_event_kwargs_omit_proxy_without_effective_delegation(self):
    cases = (
        (
            self.request(operator=None, proxy="executor"),
            {"username": "executor", "extend_data": {}},
        ),
        (
            self.request(app_code="other-app", operator="alice", proxy="executor"),
            {"username": "executor", "extend_data": {}},
        ),
        (
            self.request(operator="executor", proxy="executor"),
            {"username": "executor", "extend_data": {}},
        ),
        (
            self.request(operator="alice", proxy=""),
            {"username": "alice", "extend_data": {}},
        ),
    )
    for request, expected in cases:
        with self.subTest(request=request):
            self.assertEqual(utils.get_audit_event_kwargs(request), expected)
```

第一个测试防止可信免登录委托丢失 B；第二个测试防止普通或回退操作被误标记成代理操作。预期值中的 `extend_data` 使用手写字面量，不复用生产构造逻辑。

- [ ] **Step 2: 运行测试并确认因接口不存在而失败**

Run:

```bash
set -a
source /Users/dengyh/Projects/bk-sops/.env
set +a
PYTHONPATH=/Users/dengyh/Projects/bk-sops \
  /Users/dengyh/.pyenv/versions/3.6.15/bin/python manage.py test \
  gcloud.tests.contrib.audit.test_utils.DelegatedAuditUsernameTestCase -v 2
```

Expected: FAIL，错误包含 `AttributeError: module 'gcloud.contrib.audit.utils' has no attribute 'get_audit_event_kwargs'`。

- [ ] **Step 3: 写入最小实现**

在 `get_audit_username` 后新增：

```python
def get_audit_event_kwargs(request):
    username = get_audit_username(request)
    proxy_username = getattr(getattr(request, "user", None), "username", "")
    extend_data = {}
    if proxy_username and username != proxy_username:
        extend_data["proxy_username"] = proxy_username
    return {"username": username, "extend_data": extend_data}
```

该实现不重复信任校验，只根据 `get_audit_username` 已接受的最终结果判断 A/B 是否分离。

- [ ] **Step 4: 运行委托身份测试并确认通过**

Run: 使用 Step 2 的相同命令。

Expected: `DelegatedAuditUsernameTestCase` 全部 PASS。

- [ ] **Step 5: 提交身份参数实现**

```bash
git add gcloud/contrib/audit/utils.py gcloud/tests/contrib/audit/test_utils.py
git commit -m "feat: 生成委托审计代理执行人参数 --story=136920805"
```

---

### Task 2: 脱敏并透传审计扩展数据

**Files:**
- Modify: `gcloud/contrib/audit/utils.py:165-220`
- Test: `gcloud/tests/contrib/audit/test_utils.py:61-204`

**Interfaces:**
- Consumes: 可选字典 `extend_data`，内容由调用方提供。
- Produces: `bk_audit_add_event_on_commit(..., extend_data=None)` 和 `bk_audit_add_event(..., extend_data=None)`；最终 SDK 参数包含脱敏后的 `extend_data`。

- [ ] **Step 1: 写入事务回调和 SDK 边界的失败测试**

在 `AuditUtilsTestCase` 中新增 SDK 边界测试：

```python
@override_settings(ENABLE_BK_AUDIT=True)
@mock.patch("gcloud.contrib.audit.utils.bk_audit_client.add_event")
@mock.patch("gcloud.contrib.audit.utils.build_instance", return_value="audit-instance")
def test_event_sanitizes_and_forwards_extend_data(self, build_instance, add_event):
    utils.bk_audit_add_event(
        "alice",
        "task_operate",
        "task",
        mock.Mock(id=1),
        extend_data={
            "proxy_username": "executor",
            "access_token": "sensitive-value",
        },
    )

    self.assertEqual(
        add_event.call_args[1]["extend_data"],
        {
            "proxy_username": "executor",
            "access_token": "******",
        },
    )
```

在 `AuditTransactionTestCase` 中新增事务透传测试：

```python
@override_settings(ENABLE_BK_AUDIT=True)
@mock.patch("gcloud.contrib.audit.utils.bk_audit_add_event")
def test_commit_forwards_extend_data(self, add_event):
    with self.captureOnCommitCallbacks(execute=True):
        utils.bk_audit_add_event_on_commit(
            username="alice",
            action_id="task_operate",
            resource_id="task",
            instance=mock.Mock(id=1),
            extend_data={"proxy_username": "executor"},
        )

    self.assertEqual(
        add_event.call_args[1]["extend_data"],
        {"proxy_username": "executor"},
    )
```

这两个测试分别捕获 SDK 参数遗漏和 `transaction.on_commit` 延迟回调丢字段。

- [ ] **Step 2: 运行新增测试并确认按预期失败**

Run:

```bash
set -a
source /Users/dengyh/Projects/bk-sops/.env
set +a
PYTHONPATH=/Users/dengyh/Projects/bk-sops \
  /Users/dengyh/.pyenv/versions/3.6.15/bin/python manage.py test \
  gcloud.tests.contrib.audit.test_utils.AuditUtilsTestCase.test_event_sanitizes_and_forwards_extend_data \
  gcloud.tests.contrib.audit.test_utils.AuditTransactionTestCase.test_commit_forwards_extend_data -v 2
```

Expected: 两个测试 FAIL；SDK 测试缺少 `extend_data` 调用参数，事务测试的延迟调用也缺少该参数。

- [ ] **Step 3: 显式接收并透传扩展数据**

将两个入口签名调整为：

```python
def bk_audit_add_event_on_commit(
    username,
    action_id,
    resource_id=None,
    instance=None,
    origin_data=None,
    *args,
    data=None,
    extend_data=None,
    **kwargs
):
```

```python
def bk_audit_add_event(
    username,
    action_id,
    resource_id=None,
    instance=None,
    origin_data=None,
    *args,
    data=None,
    extend_data=None,
    **kwargs
):
```

在 `transaction.on_commit(partial(...))` 中加入：

```python
extend_data=extend_data,
```

在 `bk_audit_add_event` 中与资源快照一起脱敏：

```python
safe_extend_data = sanitize_audit_data(extend_data)
```

并在 SDK 调用中加入：

```python
extend_data=safe_extend_data,
```

- [ ] **Step 4: 运行审计工具测试并确认通过**

Run:

```bash
set -a
source /Users/dengyh/Projects/bk-sops/.env
set +a
PYTHONPATH=/Users/dengyh/Projects/bk-sops \
  /Users/dengyh/.pyenv/versions/3.6.15/bin/python manage.py test \
  gcloud.tests.contrib.audit.test_utils -v 2
```

Expected: 全部 PASS，既有禁用、异常隔离、回滚和资源脱敏测试不回归。

- [ ] **Step 5: 提交扩展字段上报实现**

```bash
git add gcloud/contrib/audit/utils.py gcloud/tests/contrib/audit/test_utils.py
git commit -m "feat: 透传审计代理执行人扩展字段 --story=136920805"
```

---

### Task 3: 三个 PO 写入口统一上报代理执行人

**Files:**
- Modify: `gcloud/apigw/views/create_task.py:38,246-253`
- Modify: `gcloud/apigw/views/operate_task.py:25,83-104`
- Modify: `gcloud/apigw/views/operate_node.py:23,80-86`
- Test: `gcloud/tests/apigw/views/test_create_task.py:54-87`
- Test: `gcloud/tests/apigw/views/test_operate_task.py:46-77`
- Test: `gcloud/tests/apigw/views/test_operate_node.py:50-87`

**Interfaces:**
- Consumes: Task 1 产生的 `get_audit_event_kwargs(request) -> {"username": str, "extend_data": dict}`。
- Produces: 创建任务、操作任务和操作节点成功事件均把该字典解包给 `bk_audit_add_event_on_commit`。

- [ ] **Step 1: 将三个现有身份隔离测试改为要求扩展字段**

`test_create_task_uses_proxy_for_business_and_delegated_operator_for_audit` 把 `get_audit_username` mock 替换为：

```python
with mock.patch(
    "gcloud.apigw.views.create_task.get_audit_event_kwargs",
    return_value={
        "username": "alice",
        "extend_data": {"proxy_username": "executor"},
    },
    create=True,
) as get_audit_event_kwargs:
```

`test_start_uses_proxy_for_business_and_delegated_operator_for_audit` 把 `get_audit_username` mock 替换为：

```python
with mock.patch(
    "gcloud.apigw.views.operate_task.get_audit_event_kwargs",
    return_value={
        "username": "alice",
        "extend_data": {"proxy_username": "executor"},
    },
    create=True,
) as get_audit_event_kwargs:
```

`test_operate_node_uses_proxy_for_business_and_delegated_operator_for_audit` 把 `get_audit_username` mock 替换为：

```python
with patch(
    "gcloud.apigw.views.operate_node.get_audit_event_kwargs",
    return_value={
        "username": "alice",
        "extend_data": {"proxy_username": "executor"},
    },
    create=True,
) as get_audit_event_kwargs:
```

三个测试保留对业务执行人 `executor` 的现有断言，并统一增加：

```python
get_audit_event_kwargs.assert_called_once()
self.assertEqual(add_event.call_args[1]["username"], "alice")
self.assertEqual(
    add_event.call_args[1]["extend_data"],
    {"proxy_username": "executor"},
)
```

这些测试会在错误地继续调用旧 helper、遗漏某个入口或误把 B 改成业务操作人时失败。

- [ ] **Step 2: 运行三个 APIGW 测试并确认旧代码失败**

Run:

```bash
set -a
source /Users/dengyh/Projects/bk-sops/.env
set +a
PYTHONPATH=/Users/dengyh/Projects/bk-sops \
  /Users/dengyh/.pyenv/versions/3.6.15/bin/python manage.py test \
  gcloud.tests.apigw.views.test_create_task.CreateTaskAPITest.test_create_task_uses_proxy_for_business_and_delegated_operator_for_audit \
  gcloud.tests.apigw.views.test_operate_task.OperateTaskAPITest.test_start_uses_proxy_for_business_and_delegated_operator_for_audit \
  gcloud.tests.apigw.views.test_operate_node.OperateNodeAPITest.test_operate_node_uses_proxy_for_business_and_delegated_operator_for_audit -v 2
```

Expected: 三个测试 FAIL；`get_audit_event_kwargs` 未被调用，且旧上报参数不含 `extend_data`。

- [ ] **Step 3: 替换三个入口的统一事件参数**

三个文件的导入均改为：

```python
from gcloud.contrib.audit.utils import bk_audit_add_event_on_commit, get_audit_event_kwargs
```

每个成功事件调用统一改成以下形态，`**` 必须放在参数列表最后以兼容 Python 3.6：

```python
bk_audit_add_event_on_commit(
    action_id=action_id,
    resource_id=IAMMeta.TASK_RESOURCE,
    instance=task,
    **get_audit_event_kwargs(request)
)
```

`operate_task` 和 `operate_node` 的 `action_id` 继续使用 `IAMMeta.TASK_OPERATE_ACTION`。不要修改传给 `prepare_and_start_task`、`task.task_action` 或 `task.nodes_action` 的 `username`，这些业务调用必须继续使用 B。

- [ ] **Step 4: 运行三个入口的完整测试文件**

Run:

```bash
set -a
source /Users/dengyh/Projects/bk-sops/.env
set +a
PYTHONPATH=/Users/dengyh/Projects/bk-sops \
  /Users/dengyh/.pyenv/versions/3.6.15/bin/python manage.py test \
  gcloud.tests.apigw.views.test_create_task \
  gcloud.tests.apigw.views.test_operate_task \
  gcloud.tests.apigw.views.test_operate_node -v 2
```

Expected: 三个测试文件全部 PASS。

- [ ] **Step 5: 提交三个入口的接入修改**

```bash
git add \
  gcloud/apigw/views/create_task.py \
  gcloud/apigw/views/operate_task.py \
  gcloud/apigw/views/operate_node.py \
  gcloud/tests/apigw/views/test_create_task.py \
  gcloud/tests/apigw/views/test_operate_task.py \
  gcloud/tests/apigw/views/test_operate_node.py
git commit -m "feat: PO 审计上报代理执行人 --story=136920805"
```

---

### Task 4: 完整回归和提交前检查

**Files:**
- Verify: `gcloud/contrib/audit/utils.py`
- Verify: `gcloud/apigw/views/create_task.py`
- Verify: `gcloud/apigw/views/operate_task.py`
- Verify: `gcloud/apigw/views/operate_node.py`
- Verify: 上述对应测试文件及设计、计划文档

**Interfaces:**
- Consumes: Task 1-3 的所有实现和测试。
- Produces: 可提交评审的验证结果，不产生新的运行时接口。

- [ ] **Step 1: 运行相关完整回归测试**

Run:

```bash
set -o pipefail
set -a
source /Users/dengyh/Projects/bk-sops/.env
set +a
PYTHONPATH=/Users/dengyh/Projects/bk-sops \
  /Users/dengyh/.pyenv/versions/3.6.15/bin/python manage.py test \
  gcloud.tests.contrib.audit.test_utils \
  gcloud.tests.apigw.views.test_plugin_gateway \
  gcloud.tests.apigw.views.test_create_task \
  gcloud.tests.apigw.views.test_operate_task \
  gcloud.tests.apigw.views.test_operate_node -v 2
```

Expected: 全部测试 PASS，测试数至少为基线 63 加本计划新增用例。

- [ ] **Step 2: 运行格式和静态检查**

Run:

```bash
/Users/dengyh/.local/bin/pre-commit run black --files \
  gcloud/contrib/audit/utils.py \
  gcloud/apigw/views/create_task.py \
  gcloud/apigw/views/operate_task.py \
  gcloud/apigw/views/operate_node.py \
  gcloud/tests/contrib/audit/test_utils.py \
  gcloud/tests/apigw/views/test_create_task.py \
  gcloud/tests/apigw/views/test_operate_task.py \
  gcloud/tests/apigw/views/test_operate_node.py
/Users/dengyh/.local/bin/pre-commit run isort --files \
  gcloud/contrib/audit/utils.py \
  gcloud/apigw/views/create_task.py \
  gcloud/apigw/views/operate_task.py \
  gcloud/apigw/views/operate_node.py \
  gcloud/tests/contrib/audit/test_utils.py \
  gcloud/tests/apigw/views/test_create_task.py \
  gcloud/tests/apigw/views/test_operate_task.py \
  gcloud/tests/apigw/views/test_operate_node.py
/Users/dengyh/.local/bin/pre-commit run flake8 --files \
  gcloud/contrib/audit/utils.py \
  gcloud/apigw/views/create_task.py \
  gcloud/apigw/views/operate_task.py \
  gcloud/apigw/views/operate_node.py \
  gcloud/tests/contrib/audit/test_utils.py \
  gcloud/tests/apigw/views/test_create_task.py \
  gcloud/tests/apigw/views/test_operate_task.py \
  gcloud/tests/apigw/views/test_operate_node.py
git diff --check upstream/master...HEAD
```

Expected: Black、isort、Flake8 和 `git diff --check` 全部退出码为 0。

- [ ] **Step 3: 核对最终差异和身份边界**

Run:

```bash
git status --short --branch
git diff --stat upstream/master...HEAD
git diff upstream/master...HEAD -- \
  gcloud/contrib/audit/utils.py \
  gcloud/apigw/views/create_task.py \
  gcloud/apigw/views/operate_task.py \
  gcloud/apigw/views/operate_node.py
```

Expected:

- 工作区无未提交代码；
- `username` 仍为 A；
- `extend_data.proxy_username` 为 B；
- 业务调用继续使用原 `request.user.username`；
- 没有审计动作、资源、Header 协议或依赖版本变化。

- [ ] **Step 4: 按 `superpowers:finishing-a-development-branch` 提供集成选项**

基线分支固定为 `upstream/master`。不要直接推送或创建 PR；先向用户提供本地合并、推送创建 PR、保留分支三个选项，并按用户选择执行。
