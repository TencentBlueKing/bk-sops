# 委托审计操作人 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 PO 登录用户 A 成为标准运维审计中心的最终操作人，同时保持 PO 业务执行代理人 B 负责内部网关认证、IAM 校验和任务执行。

**Architecture:** PO Facade 以 B 创建 BKAPI 客户端，并在三个写入口中由后端添加 `X-BkSops-Audit-Operator: A`。标准运维从已验证的 `request.app`、原始 APIGW JWT 用户验证状态和专用 app code 白名单中建立可信边界，只在审计调用处使用 A；所有业务调用继续使用 `request.user.username == B`。

**Tech Stack:** Python 3.6/3.10、Django 2.2/3.2、BKAPI Client Core、APIGW Manager、`bk-audit==1.1.1`、pytest/Django TestCase、TAPD 需求 `136920805`。

## Global Constraints

- 设计规格：`docs/specs/2026-08-10-delegated-audit-operator-design.md`。
- 标准运维基线：最新 `upstream/master`，分支 `feat/delegated-audit-operator`。
- PO Facade 基线：`origin/release`，独立分支 `ai/delegated-audit-operator`。
- 不新增审计动作、资源、公开请求 body 字段、响应字段或 operationId。
- `request.user.username` 始终保留为 B，只有审计事件 username 可以解析为 A。
- 专用可信应用配置默认空集合；不硬编码 PO 内部 app code。
- 非可信、未验证、缺失或非法委托身份必须回退 B，且不得阻断业务。
- Facade 不能透传浏览器提供的同名头，必须由后端认证用户重新生成。
- 所有生产代码必须先有预期失败的测试，再写最小实现。

---

### Task 1: 标准运维委托审计身份解析底座

**Files:**
- Modify: `/Users/dengyh/Projects/bk-sops/.worktrees/operation-audit-phase1/env.py`
- Modify: `/Users/dengyh/Projects/bk-sops/.worktrees/operation-audit-phase1/config/default.py`
- Modify: `/Users/dengyh/Projects/bk-sops/.worktrees/operation-audit-phase1/gcloud/contrib/audit/utils.py`
- Modify: `/Users/dengyh/Projects/bk-sops/.worktrees/operation-audit-phase1/gcloud/tests/contrib/audit/test_utils.py`

**Interfaces:**
- Consumes: Django request with `request.user.username`, verified `request.app`, `_apigw_jwt_user_verified`, `META`, and optional `trace_id`.
- Produces: `get_audit_username(request) -> str` and deployment setting `BK_AUDIT_DELEGATED_OPERATOR_APPS: Set[str]`.

- [ ] **Step 1: Write failing resolver tests**

Append a focused test class to `gcloud/tests/contrib/audit/test_utils.py`. Build requests with `SimpleNamespace`, use `override_settings`, and assert literal results:

```python
class DelegatedAuditUsernameTestCase(SimpleTestCase):
    def request(
        self,
        app_code="bk-sops-facade",
        app_verified=True,
        proxy="executor",
        operator=None,
        verified=True,
    ):
        meta = {}
        if operator is not None:
            meta["HTTP_X_BKSOPS_AUDIT_OPERATOR"] = operator
        return SimpleNamespace(
            user=SimpleNamespace(username=proxy),
            app=SimpleNamespace(bk_app_code=app_code, verified=app_verified),
            META=meta,
            _apigw_jwt_user_verified=verified,
            trace_id="trace-1",
        )

    @override_settings(BK_AUDIT_DELEGATED_OPERATOR_APPS={"bk-sops-facade"})
    def test_trusted_verified_request_uses_delegated_operator(self):
        self.assertEqual(utils.get_audit_username(self.request(operator="alice@tai")), "alice@tai")

    @override_settings(BK_AUDIT_DELEGATED_OPERATOR_APPS={"bk-sops-facade"})
    def test_untrusted_or_unverified_request_falls_back_to_proxy(self):
        self.assertEqual(
            utils.get_audit_username(self.request(app_code="other-app", operator="alice")),
            "executor",
        )
        self.assertEqual(
            utils.get_audit_username(self.request(operator="alice", verified=False)),
            "executor",
        )
        self.assertEqual(
            utils.get_audit_username(self.request(operator="alice", app_verified=False)),
            "executor",
        )

    @override_settings(BK_AUDIT_DELEGATED_OPERATOR_APPS={"bk-sops-facade"})
    def test_missing_or_invalid_operator_falls_back_to_proxy(self):
        for operator in (None, "", "has space", "bad/value", "x" * 65):
            with self.subTest(operator=operator):
                self.assertEqual(utils.get_audit_username(self.request(operator=operator)), "executor")
```

The production mutation caught is accepting an untrusted/unverified or malformed asserted identity, or failing to use a valid trusted A.

- [ ] **Step 2: Run resolver tests and verify RED**

Run:

```bash
pytest -q gcloud/tests/contrib/audit/test_utils.py
```

Expected: FAIL because `gcloud.contrib.audit.utils.get_audit_username` does not exist.

- [ ] **Step 3: Add the deployment setting**

In `env.py`, parse a comma-separated OS environment variable into a set, dropping whitespace and empty entries:

```python
BK_AUDIT_DELEGATED_OPERATOR_APPS = {
    app_code.strip()
    for app_code in os.getenv("BK_AUDIT_DELEGATED_OPERATOR_APPS", "").split(",")
    if app_code.strip()
}
```

In `config/default.py`, expose it through Django settings:

```python
BK_AUDIT_DELEGATED_OPERATOR_APPS = env.BK_AUDIT_DELEGATED_OPERATOR_APPS
```

- [ ] **Step 4: Implement the minimal resolver**

In `gcloud/contrib/audit/utils.py`, add:

```python
DELEGATED_AUDIT_OPERATOR_META_KEY = "HTTP_X_BKSOPS_AUDIT_OPERATOR"
DELEGATED_AUDIT_OPERATOR_PATTERN = re.compile(r"^[A-Za-z0-9_.@-]{1,64}$")


def get_audit_username(request):
    proxy_username = getattr(getattr(request, "user", None), "username", "")
    operator = getattr(request, "META", {}).get(DELEGATED_AUDIT_OPERATOR_META_KEY)
    if not operator:
        return proxy_username

    app = getattr(request, "app", None)
    app_code = getattr(app, settings.APIGW_MANAGER_APP_CODE_KEY, "")
    trusted_apps = getattr(settings, "BK_AUDIT_DELEGATED_OPERATOR_APPS", set())
    trace_id = getattr(request, "trace_id", "")
    if (
        app_code not in trusted_apps
        or getattr(app, "verified", False) is not True
        or getattr(request, "_apigw_jwt_user_verified", False) is not True
    ):
        logger.warning(
            "bk_audit delegated_operator_ignored app_code=%s proxy_username=%s trace_id=%s",
            app_code,
            proxy_username,
            trace_id,
        )
        return proxy_username

    if not DELEGATED_AUDIT_OPERATOR_PATTERN.fullmatch(operator):
        logger.warning(
            "bk_audit delegated_operator_invalid app_code=%s proxy_username=%s trace_id=%s",
            app_code,
            proxy_username,
            trace_id,
        )
        return proxy_username

    logger.info(
        "bk_audit delegated_operator_resolved audit_username=%s proxy_username=%s app_code=%s trace_id=%s",
        operator,
        proxy_username,
        app_code,
        trace_id,
    )
    return operator
```

- [ ] **Step 5: Run resolver tests and verify GREEN**

Run:

```bash
pytest -q gcloud/tests/contrib/audit/test_utils.py
```

Expected: PASS with the new trusted, fallback, and validation cases plus all existing audit utility tests.

- [ ] **Step 6: Commit the resolver**

```bash
git add env.py config/default.py gcloud/contrib/audit/utils.py gcloud/tests/contrib/audit/test_utils.py
git commit -m "feat: 支持可信委托审计操作人 --story=136920805"
```

---

### Task 2: 标准运维三个 PO 写入口分离业务用户和审计用户

**Files:**
- Modify: `/Users/dengyh/Projects/bk-sops/.worktrees/operation-audit-phase1/gcloud/apigw/views/create_task.py`
- Modify: `/Users/dengyh/Projects/bk-sops/.worktrees/operation-audit-phase1/gcloud/apigw/views/operate_task.py`
- Modify: `/Users/dengyh/Projects/bk-sops/.worktrees/operation-audit-phase1/gcloud/apigw/views/operate_node.py`
- Modify: `/Users/dengyh/Projects/bk-sops/.worktrees/operation-audit-phase1/gcloud/tests/apigw/views/test_create_task.py`
- Modify: `/Users/dengyh/Projects/bk-sops/.worktrees/operation-audit-phase1/gcloud/tests/apigw/views/test_operate_task.py`
- Modify: `/Users/dengyh/Projects/bk-sops/.worktrees/operation-audit-phase1/gcloud/tests/apigw/views/test_operate_node.py`

**Interfaces:**
- Consumes: `get_audit_username(request) -> str` from Task 1.
- Produces: task creation/operation behavior under B with audit calls under A.

- [ ] **Step 1: Write failing view wiring tests**

For each view, patch `get_audit_username` to return literal `"alice"` and patch `bk_audit_add_event_on_commit`. Send the business request as `HTTP_BK_USERNAME="executor"`.

Assertions must cover both sides of the split:

```python
create_pipeline_kwargs["creator"] == "executor"
audit_event.call_args.kwargs["username"] == "alice"
```

```python
prepare_and_start_task.apply_async.call_args.kwargs["kwargs"]["username"] == "executor"
audit_event.call_args.kwargs["username"] == "alice"
```

```python
task.nodes_action.assert_called_once_with(
    action,
    node_id,
    "executor",
    data=data,
    inputs=inputs,
    flow_id=flow_id,
)
audit_event.call_args.kwargs["username"] == "alice"
```

Add a real POST success test for `operate_node`; do not reuse the existing misspelled `trest_operate_node__success` GET method because it is not collected and violates `@require_POST`.

The production mutation caught is replacing B with A in business execution, or continuing to report B in audit.

- [ ] **Step 2: Run the three view test files and verify RED**

Run:

```bash
pytest -q \
  gcloud/tests/apigw/views/test_create_task.py \
  gcloud/tests/apigw/views/test_operate_task.py \
  gcloud/tests/apigw/views/test_operate_node.py
```

Expected: FAIL because the views do not import/call `get_audit_username`, and audit still receives B.

- [ ] **Step 3: Implement minimal view changes**

In each view, import `get_audit_username` alongside `bk_audit_add_event_on_commit`. Keep the existing business `username` unchanged and replace only the audit argument. The three audit calls must be:

```python
# create_task.py
bk_audit_add_event_on_commit(
    username=get_audit_username(request),
    action_id=action_id,
    resource_id=IAMMeta.TASK_RESOURCE,
    instance=task,
)

# operate_task.py
bk_audit_add_event_on_commit(
    username=get_audit_username(request),
    action_id=IAMMeta.TASK_OPERATE_ACTION,
    resource_id=IAMMeta.TASK_RESOURCE,
    instance=task,
)

# operate_node.py
bk_audit_add_event_on_commit(
    username=get_audit_username(request),
    action_id=IAMMeta.TASK_OPERATE_ACTION,
    resource_id=IAMMeta.TASK_RESOURCE,
    instance=task,
)
```

Do not change pipeline instance creator, Celery kwargs, `task_action`, `nodes_action`, permission decorators, request/response bodies, or operation records.

- [ ] **Step 4: Run the three view test files and verify GREEN**

Run the same three-file pytest command.

Expected: PASS; tests demonstrate B for business operations and A for audit calls.

- [ ] **Step 5: Run standard-ops audit regression**

Run:

```bash
pytest -q \
  gcloud/tests/contrib/audit \
  gcloud/tests/apigw/views/test_create_task.py \
  gcloud/tests/apigw/views/test_operate_task.py \
  gcloud/tests/apigw/views/test_operate_node.py
```

Expected: PASS with no request/response regressions.

- [ ] **Step 6: Commit the view integration**

```bash
git add \
  gcloud/apigw/views/create_task.py \
  gcloud/apigw/views/operate_task.py \
  gcloud/apigw/views/operate_node.py \
  gcloud/tests/apigw/views/test_create_task.py \
  gcloud/tests/apigw/views/test_operate_task.py \
  gcloud/tests/apigw/views/test_operate_node.py
git commit -m "feat: PO 委托操作使用真实用户审计 --story=136920805"
```

---

### Task 3: 建立 PO Facade 独立工作树和请求头契约

**Files:**
- Create worktree: `/Users/dengyh/Projects/bk-sops-facade/.worktrees/delegated-audit-operator`
- Modify: `backend/utils/bkapi.py`
- Modify: `backend/tests/test_task_create_service.py`

**Interfaces:**
- Consumes: PO authenticated username A.
- Produces: `build_sops_audit_headers(username) -> Dict[str, str]` with exact HTTP header `X-BkSops-Audit-Operator`.

- [ ] **Step 1: Create the isolated Facade branch from production release**

Verify `.worktrees` is ignored, then create:

```bash
git -C /Users/dengyh/Projects/bk-sops-facade check-ignore -q .worktrees
git -C /Users/dengyh/Projects/bk-sops-facade worktree add \
  /Users/dengyh/Projects/bk-sops-facade/.worktrees/delegated-audit-operator \
  -b ai/delegated-audit-operator origin/release
```

Do not modify the existing `ai/saas-create-unexposed-template` worktree or its untracked `docs/.DS_Store`.

- [ ] **Step 2: Write a failing task-create header assertion**

In `CreateSopsTaskServiceTest.test_create_sops_task_updates_record`, assert the real outbound operation receives a backend-generated header:

```python
self.assertEqual(
    create_call[1]["headers"],
    {"X-BkSops-Audit-Operator": "alice"},
)
```

The production mutation caught is dropping A before the internal gateway call.

- [ ] **Step 3: Run the focused Facade test and verify RED**

Run:

```bash
/Users/dengyh/.pyenv/versions/3.6.15/bin/python manage.py test \
  backend.tests.test_task_create_service.CreateSopsTaskServiceTest.test_create_sops_task_updates_record \
  -v 2
```

Expected: FAIL with missing `headers` in the BKAPI operation call.

- [ ] **Step 4: Add the Facade header builder and task-create integration**

In `backend/utils/bkapi.py`, add:

```python
BK_SOPS_AUDIT_OPERATOR_HEADER = "X-BkSops-Audit-Operator"


def build_sops_audit_headers(username):
    return {BK_SOPS_AUDIT_OPERATOR_HEADER: username}
```

Import the helper in `backend/services/task_create.py` and change only the outbound call:

```python
response = client.api.create_task(
    path_params={
        "bk_biz_id": task_record.bk_biz_id,
        "template_id": task_record.bk_sops_template_id,
    },
    json=request_body,
    headers=build_sops_audit_headers(creator),
)
```

Keep `get_sops_client_by_username(business_proxy)` unchanged.

- [ ] **Step 5: Run task-create tests and verify GREEN**

Run:

```bash
/Users/dengyh/.pyenv/versions/3.6.15/bin/python manage.py test \
  backend.tests.test_task_create_service.CreateSopsTaskServiceTest \
  -v 2
```

Expected: PASS; the record still stores A while the client remains B and the outbound header carries A.

- [ ] **Step 6: Commit the Facade task-create contract**

Use the Facade repository's existing commit style and the shared TAPD story:

```bash
git add backend/utils/bkapi.py backend/services/task_create.py backend/tests/test_task_create_service.py
git commit -m "feat: forward delegated audit operator --story=136920805"
```

---

### Task 4: PO Facade 任务与节点操作传递真实操作人

**Files:**
- Modify: `/Users/dengyh/Projects/bk-sops-facade/.worktrees/delegated-audit-operator/backend/views/operate_task.py`
- Modify: `/Users/dengyh/Projects/bk-sops-facade/.worktrees/delegated-audit-operator/backend/views/operate_node.py`
- Create: `/Users/dengyh/Projects/bk-sops-facade/.worktrees/delegated-audit-operator/backend/tests/test_delegated_audit_operator.py`

**Interfaces:**
- Consumes: `build_sops_audit_headers(request.user.username)` from Task 3.
- Produces: task/node BKAPI calls authenticated as B with header asserted from A.

- [ ] **Step 1: Write failing task and node view tests**

Use `RequestFactory`, a real `request.user = SimpleNamespace(username="alice")`, and patch only database/upstream boundaries. Include a spoofed browser header `HTTP_X_BKSOPS_AUDIT_OPERATOR="mallory"` in the request, then assert both outbound calls use literal `alice`:

```python
client.api.operate_task.assert_called_once_with(
    path_params={"task_id": 456, "bk_biz_id": 2},
    json={"action": "pause"},
    headers={"X-BkSops-Audit-Operator": "alice"},
)
```

```python
client.api.operate_node.assert_called_once_with(
    path_params={"task_id": 456, "bk_biz_id": 2},
    json={"node_id": "node-1", "action": "retry"},
    headers={"X-BkSops-Audit-Operator": "alice"},
)
```

Also assert `get_sops_client_by_username` receives literal `"executor"`. These tests catch both identity swapping and browser-header passthrough.

- [ ] **Step 2: Run the new test file and verify RED**

Run:

```bash
/Users/dengyh/.pyenv/versions/3.6.15/bin/python manage.py test \
  backend.tests.test_delegated_audit_operator \
  -v 2
```

Expected: FAIL because `operate_task` and `operate_node` do not pass headers.

- [ ] **Step 3: Implement minimal task/node header forwarding**

Import `build_sops_audit_headers` from `backend.utils.bkapi` in both views and add:

```python
headers=build_sops_audit_headers(request.user.username)
```

to the existing `client.api.operate_task` and `client.api.operate_node` calls. Do not read `HTTP_X_BKSOPS_AUDIT_OPERATOR` from the incoming browser request.

- [ ] **Step 4: Run the new test file and verify GREEN**

Run the same Django test command.

Expected: PASS; spoofed `mallory` is ignored and backend-authenticated `alice` is sent.

- [ ] **Step 5: Run complete Facade backend regression**

Run:

```bash
/Users/dengyh/.pyenv/versions/3.6.15/bin/python manage.py test backend.tests -v 2
```

Expected: PASS with no PO task creation, approval, query, task operation, or node operation regressions.

- [ ] **Step 6: Commit the Facade operation integration**

```bash
git add backend/views/operate_task.py backend/views/operate_node.py backend/tests/test_delegated_audit_operator.py
git commit -m "feat: forward task audit operator --story=136920805"
```

---

### Task 5: Cross-repository verification and delivery

**Files:**
- Verify all files committed in both feature branches.
- No new production files beyond Tasks 1-4.

**Interfaces:**
- Consumes: Facade `X-BkSops-Audit-Operator` contract and standard-ops resolver.
- Produces: two independently reviewable branches with a matching identity contract.

- [ ] **Step 1: Run standard-ops format and tests**

```bash
black --check \
  gcloud/contrib/audit/utils.py \
  gcloud/apigw/views/create_task.py \
  gcloud/apigw/views/operate_task.py \
  gcloud/apigw/views/operate_node.py \
  gcloud/tests/contrib/audit/test_utils.py \
  gcloud/tests/apigw/views/test_create_task.py \
  gcloud/tests/apigw/views/test_operate_task.py \
  gcloud/tests/apigw/views/test_operate_node.py
isort --check-only \
  gcloud/contrib/audit/utils.py \
  gcloud/apigw/views/create_task.py \
  gcloud/apigw/views/operate_task.py \
  gcloud/apigw/views/operate_node.py \
  gcloud/tests/contrib/audit/test_utils.py \
  gcloud/tests/apigw/views/test_create_task.py \
  gcloud/tests/apigw/views/test_operate_task.py \
  gcloud/tests/apigw/views/test_operate_node.py
flake8 \
  gcloud/contrib/audit/utils.py \
  gcloud/apigw/views/create_task.py \
  gcloud/apigw/views/operate_task.py \
  gcloud/apigw/views/operate_node.py \
  gcloud/tests/contrib/audit/test_utils.py \
  gcloud/tests/apigw/views/test_create_task.py \
  gcloud/tests/apigw/views/test_operate_task.py \
  gcloud/tests/apigw/views/test_operate_node.py
pytest -q \
  gcloud/tests/contrib/audit \
  gcloud/tests/apigw/views/test_create_task.py \
  gcloud/tests/apigw/views/test_operate_task.py \
  gcloud/tests/apigw/views/test_operate_node.py
```

Expected: all commands exit 0.

- [ ] **Step 2: Run Facade format and tests**

Use the repository's configured formatter/linter if available, then run:

```bash
/Users/dengyh/.pyenv/versions/3.6.15/bin/python manage.py test backend.tests -v 2
```

Expected: all backend tests pass.

- [ ] **Step 3: Verify the exact cross-repo contract**

Confirm both repositories use the exact case-insensitive wire header spelling `X-BkSops-Audit-Operator`, corresponding to Django META key `HTTP_X_BKSOPS_AUDIT_OPERATOR`. Confirm Facade clients remain initialized with B and standard-ops business calls still consume B.

- [ ] **Step 4: Review diffs and repository state**

For the standard-ops worktree:

```bash
git diff upstream/master...HEAD --check
git status --short --branch
git log --oneline --decorate -5
```

For the Facade worktree:

```bash
git diff origin/release...HEAD --check
git status --short --branch
git log --oneline --decorate -5
```

Expected: clean working trees containing only intentional commits.

- [ ] **Step 5: Push and create review requests only after local verification**

Standard-ops:

```bash
git push -u origin feat/delegated-audit-operator
gh pr create \
  --repo TencentBlueKing/bk-sops \
  --base master \
  --head dengyh:feat/delegated-audit-operator
```

Facade: push `ai/delegated-audit-operator` to the repository's normal writable remote and create an MR targeting `release`. Do not push to an upstream/protected branch directly.

- [ ] **Step 6: Record deployment configuration**

In the delivery summary, explicitly state that production behavior remains B until API Server configures `BK_AUDIT_DELEGATED_OPERATOR_APPS` to the verified PO Facade deployment app code. Do not guess or hardcode the production app code; retrieve it from the PO deployment configuration before rollout.
