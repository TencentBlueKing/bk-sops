# bk-sops PO Superuser Admin Read Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为指定 PO App Code 提供严格限定的 bk-sops 管理员只读通道，使 PO 的 `is_superuser` 能查看全部未停用业务、业务流程和任务，但不获得任何写能力。

**Architecture:** 在现有 APIGW 身份识别之后增加显式 `mark_admin_read_request` 装饰器，仅为选定读取 API 设置 `request.is_admin_read`；查看类 IAM 拦截器识别该标记，写拦截器完全不变。App Code 白名单、已验证 APIGW 用户、审计操作人、HTTP 方法和接口装饰器共同形成失败关闭的边界，普通 IAM 路径保持原样。

**Tech Stack:** Python 3.6.15、Django 3.2.25、bk-sops APIGW decorators、bk-iam、cachetools、Django TestCase/APITestCase、YAML API resources。

## Global Constraints

- TAPD Story：`137115625`，所有提交信息以 `--story=137115625` 结尾。
- 只增加“可见”权限；`ProjectEdit`、`FlowEdit`、`TaskOperate`、`AdminEdit` 等写权限不旁路。
- `auth_actions` 必须继续表示管理员本人的真实 IAM 权限，禁止补造 `project_view`、`project_edit` 或其他 action。
- 管理员只读声明只接受白名单 PO App Code，环境变量键固定为 `ADMIN_READ_APP_WHITELIST`，未配置时默认空集合。
- 已携带 `X-BkSops-Admin-Read` 但校验失败时返回 `REQUEST_FORBIDDEN_INVALID`；未携带时继续原 IAM 路径。
- 只有语义只读的 `preview_task_tree` 可显式接受 POST；不能形成通用 POST 旁路。
- 普通模式与管理员只读模式必须使用不同缓存 key。
- API 响应 schema 保持兼容，节点日志、参数与插件输出继续使用现有裁剪和脱敏。
- Python 代码兼容 3.6，不使用 dataclass、海象运算符或 3.7+ 语法。
- 设计依据：`docs/specs/2026-08-13-po-superuser-admin-read-design.md`。

---

## File Structure

- `gcloud/apigw/decorators.py`：管理员只读请求的唯一识别入口与失败关闭响应。
- `gcloud/apigw/utils.py`：把 `request.is_admin_read` 纳入 APIGW 缓存键。
- `gcloud/iam_auth/view_interceptors/apigw/*.py`：仅查看类拦截器识别管理员只读标记。
- `gcloud/apigw/views/*.py`：选定读取 API 显式安装装饰器；项目列表与详情提供管理员读取分支。
- `gcloud/tests/apigw/test_admin_read.py`：装饰器、缓存键与拦截器的安全边界测试。
- `gcloud/tests/apigw/views/test_get_user_project_list.py`、`test_get_user_project_detail.py`：项目列表/详情行为测试。
- `gcloud/tests/apigw/views/test_admin_read_endpoints.py`：接口白名单与方法范围测试。
- `docs/zh_hans/apidoc/*.md`、`docs/en/apidoc/*.md`：只读调用头、限制及错误语义。
- `gcloud/apigw/management/commands/data/api-resources.yml`：只校验现有路径和方法，不新增写资源。
- `gcloud/apigw/docs/apigw-docs.tgz`：按仓库规范重新打包 API 文档。

### Task 1: Admin-read request marker and cache isolation

**Files:**
- Modify: `gcloud/apigw/decorators.py:26-97`
- Modify: `gcloud/apigw/utils.py:33-64`
- Create: `gcloud/tests/apigw/test_admin_read.py`

**Interfaces:**
- Consumes: `request.app`、`request.user`、`request._apigw_jwt_user_verified`，均由 `mark_request_whether_is_trust` 在外层先设置。
- Produces: `admin_read_app_whitelist: EnvWhitelist`、`mark_admin_read_request(allowed_methods=("GET",))`、`request.is_admin_read: bool`；`deal_request_args()` 生成包含 `admin_read:0|1` 的 key。

- [ ] **Step 1: Write failing decorator and cache tests**

在 `gcloud/tests/apigw/test_admin_read.py` 创建以下测试骨架，并复用 `RequestFactory` 构造请求：

```python
import json
from types import SimpleNamespace
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from gcloud import err_code
from gcloud.apigw.decorators import mark_admin_read_request
from gcloud.apigw.utils import api_hash_key


class AdminReadDecoratorTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create(username="po_admin")

    def build_request(self, method="get", admin_header="true", operator="po_admin"):
        request = getattr(self.factory, method)(
            "/api/v3/projects/",
            HTTP_X_BKSOPS_ADMIN_READ=admin_header,
            HTTP_X_BKSOPS_AUDIT_OPERATOR=operator,
        )
        request.user = self.user
        request.app = SimpleNamespace(app_code="po-app")
        request._apigw_jwt_user_verified = True
        return request

    @mock.patch("gcloud.apigw.decorators.admin_read_app_whitelist.has", return_value=True)
    def test_verified_whitelist_request_enables_admin_read(self, whitelist_has):
        view = mark_admin_read_request()(lambda request: request.is_admin_read)
        self.assertTrue(view(self.build_request()))

    @mock.patch("gcloud.apigw.decorators.admin_read_app_whitelist.has", return_value=True)
    def test_audit_operator_mismatch_fails_closed(self, whitelist_has):
        view = mark_admin_read_request()(lambda request: True)
        response = view(self.build_request(operator="another_user"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["code"], err_code.REQUEST_FORBIDDEN_INVALID.code)

    @mock.patch("gcloud.apigw.decorators.admin_read_app_whitelist.has", return_value=True)
    def test_unverified_apigw_user_fails_closed(self, whitelist_has):
        request = self.build_request()
        request._apigw_jwt_user_verified = False
        response = mark_admin_read_request()(lambda request: True)(request)
        self.assertEqual(json.loads(response.content)["code"], err_code.REQUEST_FORBIDDEN_INVALID.code)

    def test_absent_header_keeps_normal_mode(self):
        request = self.factory.get("/api/v3/projects/")
        request.user = self.user
        request.app = SimpleNamespace(app_code="not-used")
        request._apigw_jwt_user_verified = True
        result = mark_admin_read_request()(lambda request: request.is_admin_read)(request)
        self.assertFalse(result)

    @mock.patch("gcloud.apigw.decorators.admin_read_app_whitelist.has", return_value=True)
    def test_get_only_marker_rejects_post(self, whitelist_has):
        response = mark_admin_read_request()(lambda request: True)(self.build_request(method="post"))
        self.assertEqual(json.loads(response.content)["code"], err_code.REQUEST_FORBIDDEN_INVALID.code)


class AdminReadCacheKeyTestCase(TestCase):
    def test_admin_read_mode_changes_cache_key(self):
        request = RequestFactory().get("/api/v3/projects/1/")
        request.user = SimpleNamespace(username="po_admin")
        request.is_admin_read = False
        normal_key = api_hash_key(request)
        request.is_admin_read = True
        self.assertNotEqual(normal_key, api_hash_key(request))
```

- [ ] **Step 2: Run the new tests and verify RED**

Run:

```bash
PYENV_VERSION=3.6.15 APP_ID=bk_sops APP_TOKEN=test BK_PAAS_HOST=http://paas.test BK_IAM_V3_INNER_HOST=http://iam.test python manage.py test gcloud.tests.apigw.test_admin_read -v 2
```

Expected: import fails because `mark_admin_read_request` does not exist; if test database connectivity fails first, record the MySQL error and run the pure decorator cases with the repository's configured CI database before changing production code.

- [ ] **Step 3: Implement the marker and strict validation**

在 `gcloud/apigw/decorators.py` 的 `app_whitelist` 旁新增：

```python
admin_read_app_whitelist = EnvWhitelist(transient_list=set(), env_key="ADMIN_READ_APP_WHITELIST")
ADMIN_READ_HEADER = "HTTP_X_BKSOPS_ADMIN_READ"
ADMIN_READ_AUDIT_OPERATOR_HEADER = "HTTP_X_BKSOPS_AUDIT_OPERATOR"


def _admin_read_forbidden(message):
    return JsonResponse(
        {
            "result": False,
            "data": None,
            "message": message,
            "code": err_code.REQUEST_FORBIDDEN_INVALID.code,
        }
    )


def mark_admin_read_request(allowed_methods=("GET",)):
    allowed_methods = frozenset(allowed_methods)

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            setattr(request, "is_admin_read", False)
            header_value = request.META.get(ADMIN_READ_HEADER)
            if header_value is None:
                return view_func(request, *args, **kwargs)

            app_code = getattr(request.app, settings.APIGW_MANAGER_APP_CODE_KEY, "")
            audit_operator = request.META.get(ADMIN_READ_AUDIT_OPERATOR_HEADER, "")
            username = getattr(request.user, "username", "")
            valid = all(
                (
                    header_value == "true",
                    request.method in allowed_methods,
                    getattr(request, "_apigw_jwt_user_verified", False) is True,
                    bool(username),
                    audit_operator == username,
                    admin_read_app_whitelist.has(app_code),
                )
            )
            if not valid:
                return _admin_read_forbidden("invalid admin read request")

            setattr(request, "is_admin_read", True)
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
```

保持 `mark_request_whether_is_trust` 现有 `_capture_original_apigw_jwt_user()` 调用顺序不变；不要把 PO App Code 加入 `APP_WHITELIST`。

- [ ] **Step 4: Isolate cache keys**

在 `gcloud/apigw/utils.py::deal_request_args` 把 request tag 改为：

```python
request_tag = "path:{},user:{},params:{},admin_read:{}".format(
    request.path,
    request.user.username,
    request_params,
    int(getattr(request, "is_admin_read", False) is True),
)
```

- [ ] **Step 5: Run focused tests and verify GREEN**

Run the command from Step 2. Expected: all cases in `gcloud.tests.apigw.test_admin_read` pass in an environment with the configured test database.

- [ ] **Step 6: Commit the security foundation**

```bash
git add gcloud/apigw/decorators.py gcloud/apigw/utils.py gcloud/tests/apigw/test_admin_read.py
git commit -m "feat: 增加管理员只读请求标记 --story=137115625"
```

### Task 2: Read-only IAM interceptor bypass

**Files:**
- Modify: `gcloud/iam_auth/view_interceptors/apigw/project_view.py:25-35`
- Modify: `gcloud/iam_auth/view_interceptors/apigw/flow_view.py:26-36`
- Modify: `gcloud/iam_auth/view_interceptors/apigw/get_template_info.py:27-44`
- Modify: `gcloud/iam_auth/view_interceptors/apigw/task_view.py:25-35`
- Modify: `gcloud/iam_auth/view_interceptors/apigw/functionalization_task_view.py:24-32`
- Modify: `gcloud/tests/apigw/test_admin_read.py`

**Interfaces:**
- Consumes: `request.is_admin_read: bool` from Task 1 and existing `request.is_trust`.
- Produces: selected view interceptors return before IAM only for `request.is_admin_read is True`; all edit/operate interceptors remain byte-for-byte unchanged.

- [ ] **Step 1: Add RED tests for the five view interceptors**

在 `gcloud/tests/apigw/test_admin_read.py` 增加一个参数化帮助方法。每个测试构造 `request.is_admin_read=True`，patch 对应模块的 `allow_or_raise_auth_failed`，调用 interceptor 的 `process(request, view, args, kwargs)`，断言 IAM 函数未调用：

```python
class AdminReadInterceptorTestCase(TestCase):
    def build_request(self):
        return SimpleNamespace(is_admin_read=True, is_trust=False, user=SimpleNamespace(username="po_admin"))

    @mock.patch("gcloud.iam_auth.view_interceptors.apigw.project_view.allow_or_raise_auth_failed")
    def test_project_view_skips_iam(self, allow):
        from gcloud.iam_auth.view_interceptors.apigw.project_view import ProjectViewInterceptor

        interceptor = ProjectViewInterceptor()
        interceptor.process(self.build_request(), None, (), {"project_id": 1})
        allow.assert_not_called()
```

分别为 `FlowViewInterceptor`、业务模板分支的 `GetTemplateInfoInterceptor`、`TaskViewInterceptor` 和 `FunctionViewInterceptor` 添加同等断言；再加一例公共模板，断言 `GetTemplateInfoInterceptor` 仍调用 IAM。

- [ ] **Step 2: Run interceptor cases and verify RED**

Run:

```bash
PYENV_VERSION=3.6.15 APP_ID=bk_sops APP_TOKEN=test BK_PAAS_HOST=http://paas.test BK_IAM_V3_INNER_HOST=http://iam.test python manage.py test gcloud.tests.apigw.test_admin_read.AdminReadInterceptorTestCase -v 2
```

Expected: selected interceptors still call `allow_or_raise_auth_failed`.

- [ ] **Step 3: Add the minimal read bypass**

在五个 interceptor 的 `process()` 或等价入口中，放在 `request.is_trust` 判断之后、资源构造之前：

```python
if getattr(request, "is_admin_read", False) is True:
    return
```

`GetTemplateInfoInterceptor` 只在解析出业务模板类型后执行该分支；命中 `NON_COMMON_TEMPLATE_TYPES` 之外的公共模板必须继续原 IAM。不要修改任何 `*_edit.py`、`task_operate.py` 或管理员编辑 interceptor。

- [ ] **Step 4: Run interceptor and existing IAM tests**

Run:

```bash
PYENV_VERSION=3.6.15 APP_ID=bk_sops APP_TOKEN=test BK_PAAS_HOST=http://paas.test BK_IAM_V3_INNER_HOST=http://iam.test python manage.py test gcloud.tests.apigw.test_admin_read gcloud.tests.iam_auth -v 1
```

Expected: new bypass tests pass；普通请求、公共模板和既有 IAM 测试继续通过。

- [ ] **Step 5: Commit the interceptor boundary**

```bash
git add gcloud/iam_auth/view_interceptors/apigw gcloud/tests/apigw/test_admin_read.py
git commit -m "feat: 放开管理员查看拦截器 --story=137115625"
```

### Task 3: All-project list and CMDB-independent project detail

**Files:**
- Modify: `gcloud/apigw/views/get_user_project_list.py:24-66`
- Modify: `gcloud/apigw/views/get_user_project_detail.py:30-106`
- Modify: `gcloud/tests/apigw/views/test_get_user_project_list.py`
- Modify: `gcloud/tests/apigw/views/test_get_user_project_detail.py`

**Interfaces:**
- Consumes: `mark_admin_read_request()` and `request.is_admin_read` from Task 1.
- Produces: project list returns every `Project(is_disable=False)` in admin mode；project detail uses local Project fields, empty CMDB role fields, and real `auth_actions`.

- [ ] **Step 1: Add RED list/detail behavior tests**

在现有 `APITest` view tests 中通过 Django client 增加：

```python
@patch("gcloud.apigw.decorators.admin_read_app_whitelist.has", return_value=True)
@patch("gcloud.apigw.views.get_user_project_list.Project.objects.filter")
@patch("gcloud.apigw.views.get_user_project_list.get_user_projects")
def test_admin_read_returns_all_enabled_projects(self, get_user_projects, project_filter, whitelist_has):
    project_filter.return_value = [
        FancyDict(id=1, bk_biz_id=100, name="enabled", is_disable=False),
    ]
    response = self.client.get(
        path=self.url(),
        HTTP_BK_USERNAME="tester",
        HTTP_BK_APP_CODE="po-app",
        HTTP_BK_JWT_USERNAME="tester",
        HTTP_BK_JWT_USER_VERIFIED=True,
        HTTP_X_BKSOPS_ADMIN_READ="true",
        HTTP_X_BKSOPS_AUDIT_OPERATOR="tester",
    )
    data = json.loads(response.content)
    self.assertEqual([item["project_id"] for item in data["data"]], [1])
    get_user_projects.assert_not_called()
```

详情测试 patch `get_business_detail` 和 `get_resources_allowed_actions_for_user`，断言管理员模式不调用 CMDB、`bk_biz_id`/名称取自 `request.project`、四个角色字段为空、`auth_actions` 只来自 IAM 返回值。

- [ ] **Step 2: Run project view tests and verify RED**

Run:

```bash
PYENV_VERSION=3.6.15 APP_ID=bk_sops APP_TOKEN=test BK_PAAS_HOST=http://paas.test BK_IAM_V3_INNER_HOST=http://iam.test python manage.py test gcloud.tests.apigw.views.test_get_user_project_list gcloud.tests.apigw.views.test_get_user_project_detail -v 2
```

Expected: list still calls `get_user_projects`，detail still calls CMDB。

- [ ] **Step 3: Add the project list admin branch**

导入 `Project` 和 `mark_admin_read_request`，在 `get_user_project_list` 上把 marker 放在 `mark_request_whether_is_trust` 之后，并按模式取项目：

```python
@mark_request_whether_is_trust
@mark_admin_read_request()
def get_user_project_list(request):
    serializer = IncludeProjectSerializer(data=request.GET)
    if not serializer.is_valid():
        return {"result": False, "message": serializer.errors, "code": err_code.REQUEST_PARAM_INVALID.code}

    if request.is_admin_read:
        projects = Project.objects.filter(is_disable=False)
    else:
        try:
            projects = get_user_projects(request.user.username)
        except Exception as e:
            logger.exception("[API] get_user_project_list call fail: {}".format(e))
            return {
                "result": False,
                "message": "can not fetch project for user[{}]".format(request.user.username),
                "code": err_code.UNKNOWN_ERROR.code,
            }
```

保留现有 executor proxy 和响应字段逻辑。

- [ ] **Step 4: Add the project detail admin branch**

在详情 marker 之后保留 `project_inject`、`ProjectViewInterceptor` 和缓存顺序。用明确字典替代 CMDB 调用：

```python
if request.is_admin_read:
    biz_detail = {
        "bk_biz_id": request.project.bk_biz_id,
        "bk_biz_name": request.project.name,
        "bk_biz_developer": "",
        "bk_biz_maintainer": "",
        "bk_biz_tester": "",
        "bk_biz_productor": "",
    }
else:
    try:
        biz_detail = get_business_detail(request.user.username, request.project.bk_biz_id)
    except Exception as e:
        logger.exception("[API] get_user_business_detail call fail: {}".format(e))
        return {
            "result": False,
            "message": "can not get business[{}] detail for user[{}]".format(
                request.project.bk_biz_id, request.user.username
            ),
            "code": err_code.UNKNOWN_ERROR.code,
        }
```

始终执行现有 `get_resources_allowed_actions_for_user()`，禁止用管理员模式改写结果。

- [ ] **Step 5: Run project tests and commit**

Run the command from Step 2. Expected: new admin-read cases和既有普通模式用例全部通过。

```bash
git add gcloud/apigw/views/get_user_project_list.py gcloud/apigw/views/get_user_project_detail.py gcloud/tests/apigw/views/test_get_user_project_list.py gcloud/tests/apigw/views/test_get_user_project_detail.py
git commit -m "feat: 支持管理员查看全部业务 --story=137115625"
```

### Task 4: Explicit flow/task endpoint allowlist

**Files:**
- Modify: `gcloud/apigw/views/get_template_list.py`
- Modify: `gcloud/apigw/views/get_template_info.py`
- Modify: `gcloud/apigw/views/get_template_schemes.py`
- Modify: `gcloud/apigw/views/preview_task_tree.py`
- Modify: `gcloud/apigw/views/get_task_detail.py`
- Modify: `gcloud/apigw/views/get_task_status.py`
- Modify: `gcloud/apigw/views/get_task_node_data.py`
- Modify: `gcloud/apigw/views/get_task_node_detail.py`
- Modify: `gcloud/apigw/views/get_task_node_log.py`
- Modify: `gcloud/apigw/views/get_functionalization_task_list.py`
- Create: `gcloud/tests/apigw/views/test_admin_read_endpoints.py`

**Interfaces:**
- Consumes: `mark_admin_read_request(allowed_methods=("GET",))` and selected interceptor behavior from Tasks 1-2.
- Produces: exactly ten flow/task views opt in；`preview_task_tree` opts in with `allowed_methods=("POST",)`；resource ownership, deletion filters and response shaping remain active.

- [ ] **Step 1: Write RED decorator-order and method tests**

在 `test_admin_read_endpoints.py` 对每个 view 的 `__wrapped__` 链或 RequestFactory 调用做表驱动测试，固定清单：

```python
GET_ADMIN_READ_VIEWS = (
    "get_template_list",
    "get_template_info",
    "get_template_schemes",
    "get_task_detail",
    "get_task_status",
    "get_task_node_data",
    "get_task_node_detail",
    "get_task_node_log",
    "get_functionalization_task_list",
)


class AdminReadEndpointAllowlistTestCase(TestCase):
    def test_preview_marker_accepts_only_post(self):
        request = RequestFactory().get(
            "/api/v3/preview/",
            HTTP_X_BKSOPS_ADMIN_READ="true",
            HTTP_X_BKSOPS_AUDIT_OPERATOR="po_admin",
        )
        request.user = SimpleNamespace(username="po_admin")
        request.app = SimpleNamespace(app_code="po-app")
        request._apigw_jwt_user_verified = True
        with mock.patch("gcloud.apigw.decorators.admin_read_app_whitelist.has", return_value=True):
            response = mark_admin_read_request(allowed_methods=("POST",))(lambda request: True)(request)
        self.assertEqual(json.loads(response.content)["code"], err_code.REQUEST_FORBIDDEN_INVALID.code)
```

再为一个模板、一个任务、一个节点接口做集成式调用，断言 `request.is_admin_read=True` 能到达原 view 业务逻辑，归属不一致仍返回 `CONTENT_NOT_EXIST` 或现有参数错误。

- [ ] **Step 2: Run endpoint tests and verify RED**

Run:

```bash
PYENV_VERSION=3.6.15 APP_ID=bk_sops APP_TOKEN=test BK_PAAS_HOST=http://paas.test BK_IAM_V3_INNER_HOST=http://iam.test python manage.py test gcloud.tests.apigw.views.test_admin_read_endpoints -v 2
```

Expected: selected views do not yet expose the marker。

- [ ] **Step 3: Install the marker on GET views**

在九个 GET view 中导入 `mark_admin_read_request`，在每个文件现有 `mark_request_whether_is_trust` 下一行插入 marker，其他函数体和装饰器不变：

```python
@mark_request_whether_is_trust
@mark_admin_read_request()
@project_inject
@iam_intercept(TaskViewInterceptor())
```

实际函数名和既有参数保持不变；若某 view 没有 `project_inject`，marker 仍紧跟在 `mark_request_whether_is_trust` 之后，其他装饰器原顺序不动。

- [ ] **Step 4: Install the POST-only marker on preview**

`preview_task_tree` 使用：

```python
@mark_request_whether_is_trust
@mark_admin_read_request(allowed_methods=("POST",))
@project_inject
@iam_intercept(FlowViewInterceptor())
```

保持现有 preview 计算逻辑，确认它不创建任务、不保存模型。

- [ ] **Step 5: Run endpoint and regression tests**

Run:

```bash
PYENV_VERSION=3.6.15 APP_ID=bk_sops APP_TOKEN=test BK_PAAS_HOST=http://paas.test BK_IAM_V3_INNER_HOST=http://iam.test python manage.py test gcloud.tests.apigw.views.test_admin_read_endpoints gcloud.tests.apigw.views -v 1
```

Expected: admin read only reaches the listed views；普通请求和资源归属校验保持通过。

- [ ] **Step 6: Commit the explicit allowlist**

```bash
git add gcloud/apigw/views gcloud/tests/apigw/views/test_admin_read_endpoints.py
git commit -m "feat: 开放流程任务管理员只读接口 --story=137115625"
```

### Task 5: API documentation, packaging, and release verification

**Files:**
- Modify: `docs/zh_hans/apidoc/get_user_project_list.md`
- Modify: `docs/zh_hans/apidoc/get_user_project_detail.md`
- Modify: `docs/zh_hans/apidoc/get_template_list.md`
- Modify: `docs/zh_hans/apidoc/get_template_info.md`
- Modify: `docs/zh_hans/apidoc/get_template_schemes.md`
- Modify: `docs/zh_hans/apidoc/preview_task_tree.md`
- Modify: `docs/zh_hans/apidoc/get_task_detail.md`
- Modify: `docs/zh_hans/apidoc/get_task_status.md`
- Modify: `docs/zh_hans/apidoc/get_task_node_data.md`
- Modify: `docs/zh_hans/apidoc/get_task_node_detail.md`
- Modify: `docs/zh_hans/apidoc/get_task_node_log.md`
- Modify: `docs/zh_hans/apidoc/get_functionalization_task_list.md`
- Modify: matching files under `docs/en/apidoc/`
- Verify: `gcloud/apigw/management/commands/data/api-resources.yml`
- Modify: `gcloud/apigw/docs/apigw-docs.tgz`

**Interfaces:**
- Consumes: final endpoint list and header contract from Tasks 1-4.
- Produces: bilingual caller contract, regenerated docs archive, release/readback checklist；no API path or response schema addition。

- [ ] **Step 1: Add exact admin-read contract to each affected API doc**

在中文文档“请求头/说明”中加入：

```text
管理员只读调用仅供已配置的 PO 后端使用。调用方必须同时发送
X-BkSops-Admin-Read: true 与 X-BkSops-Audit-Operator: <已认证用户名>。
该模式只跳过查看权限，不改变 auth_actions，不提供任何编辑、创建、操作或下载权限。
非法声明返回 REQUEST_FORBIDDEN_INVALID；未发送声明时沿用原 IAM 鉴权。
```

英文文档使用等价内容，并在 `preview_task_tree` 文档中明确仅该 POST 为无副作用预览。

- [ ] **Step 2: Validate resource methods and paths**

Run:

```bash
python - <<'PY'
import yaml

path = "gcloud/apigw/management/commands/data/api-resources.yml"
with open(path, "r") as stream:
    document = yaml.safe_load(stream)
required = {
    "get_user_project_list",
    "get_user_project_detail",
    "get_template_list",
    "get_template_info",
    "get_template_schemes",
    "preview_task_tree",
    "get_task_detail",
    "get_task_status",
    "get_task_node_data",
    "get_task_node_detail",
    "get_task_node_log",
    "get_functionalization_task_list",
}
operation_ids = {
    operation["operationId"]
    for path_item in document["paths"].values()
    for method, operation in path_item.items()
    if method in {"get", "post", "put", "patch", "delete"}
}
missing = sorted(required - operation_ids)
assert not missing, missing
print("validated {} admin-read resources".format(len(required)))
PY
```

Expected: `validated 12 admin-read resources`；不改变任何路径和方法。

- [ ] **Step 3: Repack the API docs archive using repository convention**

先从 `docs-management.mdc` 读取仓库规定命令，然后在 `gcloud/apigw/docs/` 执行该命令；完成后验证归档包含本次 12 个中英文文档：

```bash
tar -tzf gcloud/apigw/docs/apigw-docs.tgz | rg 'get_user_project_list|get_user_project_detail|get_template_list|get_template_info|get_template_schemes|preview_task_tree|get_task_detail|get_task_status|get_task_node_data|get_task_node_detail|get_task_node_log|get_functionalization_task_list'
```

Expected: 每个受影响文档均出现在归档中。

- [ ] **Step 4: Run full focused verification**

Run:

```bash
PYENV_VERSION=3.6.15 APP_ID=bk_sops APP_TOKEN=test BK_PAAS_HOST=http://paas.test BK_IAM_V3_INNER_HOST=http://iam.test python manage.py test gcloud.tests.apigw.test_admin_read gcloud.tests.apigw.views gcloud.tests.iam_auth -v 1
```

Expected: all selected suites pass。当前本机若仍因 `localhost` MySQL 不可用而失败，必须在 CI/测试数据库环境重跑并保存通过证据，不能把本地导入成功写成测试通过。

- [ ] **Step 5: Perform security grep and diff review**

Run:

```bash
rg -n "is_admin_read|mark_admin_read_request|ADMIN_READ_APP_WHITELIST" gcloud
git diff --check upstream/master...HEAD
git diff --name-only upstream/master...HEAD
```

Expected: `is_admin_read` 只出现在装饰器、缓存键、五个查看拦截器、12 个读取 view 和测试；任何 edit/operate view 或 interceptor 命中都必须移除。

- [ ] **Step 6: Commit docs and package**

```bash
git add docs/zh_hans/apidoc docs/en/apidoc gcloud/apigw/docs/apigw-docs.tgz
git commit -m "docs: 补充管理员只读接口说明 --story=137115625"
```

- [ ] **Step 7: Configure and verify STAG without changing code**

在 bk-sops WebConsole 读取 PO 的准确 App Code 后配置：

```python
from gcloud.core.models import EnvironmentVariables

row = EnvironmentVariables.objects.get(key="ADMIN_READ_APP_WHITELIST")
print(row.key)
print(row.value)
```

Expected: `value` 精确包含目标 PO App Code。随后用三个账号验证：普通无权限用户不可见；`is_superuser` 可查看全部未停用业务/流程/任务但所有写操作仍拒绝；有真实 IAM 权限用户保持原有查看与操作能力。记录 request/trace ID，验证 `auth_actions` 未补造。回滚时先关闭 PO 功能开关，再清空 `ADMIN_READ_APP_WHITELIST`，最后清理 admin-read 缓存并复测普通 IAM。
