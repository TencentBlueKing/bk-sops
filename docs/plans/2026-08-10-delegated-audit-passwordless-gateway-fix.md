# 免登录网关委托审计信任修复 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让经过认证且在专用白名单中的 PO Facade 在免登录网关调用中仍可把 A 作为审计操作人，同时保持 B 用于 IAM 和任务执行。

**Architecture:** 保留 API Gateway 应用认证和 `BK_AUDIT_DELEGATED_OPERATOR_APPS` 作为委托身份的信任边界，并继续校验委托头格式。仅从 `get_audit_username()` 的接受条件中移除 `_apigw_jwt_user_verified`，因为 `get_client_by_username(B)` 在没有 access token 时会产生“应用已验证、用户未验证”的合法免登录调用。

**Tech Stack:** Python 3.6、Django 3.2、`unittest` / Django `SimpleTestCase`

## Global Constraints

- 设计规格以 `docs/specs/2026-08-10-delegated-audit-operator-design.md` 为准。
- 只有 `request.app.verified is True` 且 app code 位于 `BK_AUDIT_DELEGATED_OPERATOR_APPS` 时才接受委托操作人。
- 委托操作人仍须匹配现有账号格式和长度限制。
- `request.user.username`、IAM 校验、任务创建和任务执行继续使用 B。
- 非白名单应用、未验证应用、缺失或非法委托头继续回退 B，且不得阻断业务请求。
- 提交必须关联 TAPD Story `136920805`。

---

### Task 1: 兼容免登录代理用户的委托审计身份

**Files:**
- Modify: `gcloud/tests/contrib/audit/test_utils.py`
- Modify: `gcloud/contrib/audit/utils.py:65-104`

**Interfaces:**
- Consumes: `get_audit_username(request) -> str`，其中 request 提供 `user`、`app`、`META` 和可选 `trace_id`。
- Produces: 对已验证白名单应用返回合法委托操作人 A；其余情况返回代理用户 B。

- [ ] **Step 1: 写入免登录网关调用的失败回归测试**

将原有复合回退测试中的应用边界保留，并新增明确的免登录用例：

```python
@override_settings(BK_AUDIT_DELEGATED_OPERATOR_APPS={"bk-sops-facade"})
def test_trusted_app_uses_delegated_operator_for_unverified_gateway_user(self):
    self.assertEqual(
        utils.get_audit_username(self.request(operator="alice", verified=False)),
        "alice",
    )
```

原有测试继续分别断言 `app_code="other-app"` 和 `app_verified=False` 时返回 `executor`。

- [ ] **Step 2: 运行新增测试并确认红灯**

Run:

```bash
python manage.py test \
  gcloud.tests.contrib.audit.test_utils.DelegatedAuditUsernameTestCase.test_trusted_app_uses_delegated_operator_for_unverified_gateway_user \
  -v 2
```

Expected: FAIL，实际值为 `executor`、期望值为 `alice`，证明失败由现有 `_apigw_jwt_user_verified` 条件触发。

- [ ] **Step 3: 实现最小修复**

把 `get_audit_username()` 的不可信条件收敛为应用身份和白名单：

```python
if app_code not in trusted_apps or getattr(app, "verified", False) is not True:
    logger.warning(...)
    return proxy_username
```

保留 `_capture_original_apigw_jwt_user()` 和相关 request 属性，避免影响 `plugin_gateway` 对原始网关用户名的现有使用。

- [ ] **Step 4: 运行新增测试并确认绿灯**

Run:

```bash
python manage.py test \
  gcloud.tests.contrib.audit.test_utils.DelegatedAuditUsernameTestCase.test_trusted_app_uses_delegated_operator_for_unverified_gateway_user \
  -v 2
```

Expected: PASS。

- [ ] **Step 5: 运行委托审计和 APIGW 回归测试**

Run:

```bash
python manage.py test \
  gcloud.tests.contrib.audit.test_utils \
  gcloud.tests.apigw.views.test_plugin_gateway \
  -v 2
```

Expected: 全部 PASS；非白名单应用和未验证应用仍回退 B，原始 APIGW JWT 用户捕获行为保持不变。

- [ ] **Step 6: 运行代码风格检查**

Run:

```bash
pre-commit run black --files gcloud/contrib/audit/utils.py gcloud/tests/contrib/audit/test_utils.py
pre-commit run isort --files gcloud/contrib/audit/utils.py gcloud/tests/contrib/audit/test_utils.py
pre-commit run flake8 --files gcloud/contrib/audit/utils.py gcloud/tests/contrib/audit/test_utils.py
```

Expected: 三项检查均通过。

- [ ] **Step 7: 提交修复**

```bash
git add gcloud/contrib/audit/utils.py \
  gcloud/tests/contrib/audit/test_utils.py
git commit -m "fix: 兼容免登录网关委托审计 --story=136920805"
```
