# 插件网关原生表单透传 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在已经上线的插件网关目录与执行能力上，按插件原生协议向 BKFlow V4 暴露内置组件 `component_js`、第三方插件 `renderform/jsonschema`、精确版本和可执行表单上下文，并只对登记的表单辅助接口开放凭证型跨域访问。

**Architecture:** detail 在保留现有 `inputs/outputs/form_schema` 的同时新增 `forms/form_context`。内置组件直接读取组件类表单属性，第三方插件直接读取插件服务详情；不带 `source_key` 时沿用旧 detail 行为，带 `source_key` 时 operator 只取 `mark_request_whether_is_trust` 捕获的 signed JWT 原始非空 username，由已通过 APIGW 应用认证并获得资源权限的受信调用应用代传，不读取 query/body，也不要求 `user.verified=true`。浏览器从 BKFlow 直连标准运维静态资源与表单数据接口，CORS 由精确 Origin 和精确路由共同放行。

**Tech Stack:** Django 3.2, Django REST Framework, django-cors-headers 3.7, pipeline component framework, bk-plugin-service client, API Gateway, Django TestCase

**Spec:** `docs/specs/2026-06-26-plugin-gateway-full-capability-design.md` 第 1.3-1.5、9、10 节

**Dependency:** `docs/plans/2026-06-26-plugin-gateway-full-capability.md` 已实施的目录、来源配置、黑名单、执行上下文和三种执行模式

## Global Constraints

1. 本计划继续使用当前分支 `fix/plugin-gateway-form-schema`，不重做已经合入的目录和运行壳。
2. 本轮是加法发布：`forms/form_context` 与现有 `form_schema` 同时返回。不要删除 `gcloud/plugin_gateway/services/form_schema.py`、`builtin_form_schema.py` 及其测试。
3. detail 请求给出 `version` 时必须精确读取该版本。版本不存在或已下架直接失败，不得回退到默认或最新版本。
4. 不带 `source_key` 时沿用旧 detail 行为；带 `source_key` 时 operator 只能由 `mark_request_whether_is_trust` 捕获的 `_apigw_jwt_username` 产生，必须非空，并通过 `_caller_app_code(request)` 确认 APIGW caller app 存在。不接受 query/body 中的 operator，不要求 `_apigw_jwt_user_verified=true`；资源权限只授予受信调用应用。
5. `form_context` 只传 JSON 数据；函数由 BKFlow 本地实现。
6. 跨域只允许配置的 BKFlow Origin 和登记路由。禁止对整个 `/pipeline/` 或整个标准运维站点放开 CORS。
7. 第三方 `data_api` 的同源存量调用保持原行为；仅跨 Origin 请求增加插件网关可见性与黑名单校验。
8. 原生表单存在但加载失败时由消费方明确报错。提供方没有 `forms.input` 时才允许消费方根据 `inputs` 生成通用表单。
9. 所有提交使用 `<type>: <subject> --story=133649781`。
10. Stage 验收使用 `scope_type=biz`、`scope_value=100605`、operator `dannydeng`；涉及 SAP 的存量插件只验证配置和解析，禁止执行。

---

## File Structure

| File | Action | Responsibility |
|---|---|---|
| `gcloud/plugin_gateway/services/native_forms.py` | Create | 把组件类和插件服务详情转换为不改变语义的 `forms` 描述 |
| `gcloud/plugin_gateway/services/builtin_catalog.py` | Modify | 内置 detail 增加 `component_js`，保留 `form_schema` |
| `gcloud/plugin_gateway/services/catalog.py` | Modify | 第三方 detail 透传 `renderform/jsonschema`，装配 `form_context` |
| `gcloud/plugin_gateway/services/context.py` | Modify | 复用执行 Project 解析并生成纯数据表单上下文 |
| `gcloud/apigw/views/plugin_gateway.py` | Modify | detail 读取来源与 scope，按 source_key 选择 signed JWT 代传 operator 并校验 caller app，映射上下文错误 |
| `gcloud/plugin_gateway/cors.py` | Create | 精确 Origin + 精确路径的 CORS signal 判定 |
| `gcloud/plugin_gateway/apps.py` | Modify | 在 AppConfig.ready 中注册 CORS signal |
| `config/default.py` | Modify | 插件表单 CORS 设置与中间件开关 |
| `env_v2.py`, `env_v3.py` | Modify | 插件表单 CORS 环境变量 |
| `plugin_service/api.py` | Modify | 跨域 data_api 增加网关可见性检查 |
| `gcloud/tests/plugin_gateway/test_native_forms.py` | Create | 原生表单描述单元测试 |
| `gcloud/tests/plugin_gateway/test_builtin_catalog.py` | Modify | 内置表单透传兼容测试 |
| `gcloud/tests/plugin_gateway/test_catalog.py` | Modify | 第三方表单、精确版本和上下文测试 |
| `gcloud/tests/plugin_gateway/test_context_resolve.py` | Modify | 表单上下文与执行上下文一致性测试 |
| `gcloud/tests/plugin_gateway/test_cors.py` | Create | Origin/路由组合测试 |
| `gcloud/tests/apigw/views/test_plugin_gateway.py` | Modify | detail 查询参数、认证 operator 和错误映射测试 |
| `gcloud/tests/plugin_gateway/test_plugin_service_api.py` | Create | data_api 跨域可见性与同源兼容回归 |
| `docs/zh_hans/apidoc/plugin_gateway_get_plugin_detail.md` | Modify | 中文 detail 协议文档 |
| `docs/en/apidoc/plugin_gateway_get_plugin_detail.md` | Modify | 英文 detail 协议文档 |
| `gcloud/apigw/management/commands/data/api-resources.yml` | Modify | detail 查询参数和响应说明 |
| `gcloud/apigw/docs/apigw-docs.tgz` | Regenerate | APIGW 文档归档 |
| `docs/zh_hans/deploy/plugin_gateway_deploy.md` | Modify | CORS 配置和发布顺序 |
| `docs/en/deploy/plugin_gateway_deploy.md` | Modify | CORS 配置和发布顺序 |

Files deliberately unchanged in this release:

- `gcloud/plugin_gateway/services/form_schema.py`
- `gcloud/plugin_gateway/services/builtin_form_schema.py`
- `gcloud/tests/plugin_gateway/test_builtin_form_schema.py`
- 插件网关执行、轮询和回调任务

---

### Task 1: 原样描述内置组件表单

**Files:**
- Create: `gcloud/plugin_gateway/services/native_forms.py`
- Modify: `gcloud/plugin_gateway/services/builtin_catalog.py`
- Create: `gcloud/tests/plugin_gateway/test_native_forms.py`
- Modify: `gcloud/tests/plugin_gateway/test_builtin_catalog.py`

- [ ] **Step 1: 写内置表单失败测试**

在 `test_native_forms.py` 定义不依赖真实组件注册表的测试组件：

```python
from django.test import SimpleTestCase, override_settings

from gcloud.plugin_gateway.services.native_forms import build_component_forms


@override_settings(BK_SOPS_HOST="https://bksops.example.com/")
class BuildComponentFormsTestCase(SimpleTestCase):
    def test_builds_input_and_output_component_js_descriptors(self):
        class Component:
            code = "job_execute_task"
            form = "/static/components/job.js"
            form_is_embedded = False
            base = "/static/components/base.js"
            output_form = "window.outputForm = true"
            embedded_output_form = True

        self.assertEqual(
            build_component_forms(Component),
            {
                "input": {
                    "type": "component_js",
                    "key": "job_execute_task",
                    "data": "https://bksops.example.com/static/components/job.js",
                    "is_embedded": False,
                    "base": "https://bksops.example.com/static/components/base.js",
                },
                "output": {
                    "type": "component_js",
                    "key": "job_execute_task",
                    "data": "window.outputForm = true",
                    "is_embedded": True,
                    "base": None,
                },
            },
        )

    def test_returns_null_descriptors_when_component_has_no_forms(self):
        class Component:
            code = "bk_http_request"

        self.assertEqual(build_component_forms(Component), {"input": None, "output": None})
```

在 `test_builtin_catalog.py` 增加断言：

```python
detail = BuiltinCatalogService.get_plugin_detail("job_fast_execute_script", "v2.0")
self.assertEqual(detail["forms"]["input"]["type"], "component_js")
self.assertEqual(detail["forms"]["input"]["key"], "job_fast_execute_script")
self.assertTrue(detail["forms"]["input"]["data"].startswith(settings.BK_SOPS_HOST))
self.assertIn("form_schema", detail)
```

- [ ] **Step 2: 运行测试并确认失败**

Run:

```bash
python manage.py test \
  gcloud.tests.plugin_gateway.test_native_forms \
  gcloud.tests.plugin_gateway.test_builtin_catalog -v 2
```

Expected: FAIL，`native_forms` 不存在或 detail 没有 `forms`。

- [ ] **Step 3: 实现 URL 与组件描述转换**

创建 `native_forms.py`：

```python
from urllib.parse import urljoin, urlsplit

from django.conf import settings


def _string_value(value):
    if callable(value):
        value = value()
    return value


def absolute_sops_url(value):
    value = _string_value(value)
    if not value:
        return None
    value = str(value)
    if urlsplit(value).scheme:
        return value
    return urljoin(settings.BK_SOPS_HOST.rstrip("/") + "/", value.lstrip("/"))


def _component_form(component_cls, form_attr, embedded_attr, key, base=None):
    data = _string_value(getattr(component_cls, form_attr, None))
    if not data:
        return None
    is_embedded = bool(_string_value(getattr(component_cls, embedded_attr, False)))
    return {
        "type": "component_js",
        "key": key,
        "data": str(data) if is_embedded else absolute_sops_url(data),
        "is_embedded": is_embedded,
        "base": absolute_sops_url(base) if base else None,
    }


def build_component_forms(component_cls):
    code = str(component_cls.code)
    base = _string_value(getattr(component_cls, "base", None))
    return {
        "input": _component_form(component_cls, "form", "form_is_embedded", code, base),
        "output": _component_form(
            component_cls,
            "output_form",
            "embedded_output_form",
            code,
        ),
    }
```

实现时用真实组件基类的属性默认值校正 `callable` 处理；不得通过文件名推导注册 key。

- [ ] **Step 4: 在内置 detail 中增加 `forms`**

在 `BuiltinCatalogService.get_plugin_detail` 中取得精确版本组件类后：

```python
from gcloud.plugin_gateway.services.native_forms import build_component_forms

meta["forms"] = build_component_forms(component_cls)
```

保留现有 `build_builtin_form_schema` 调用和 `form_schema` 返回。

- [ ] **Step 5: 运行测试至通过**

Run:

```bash
python manage.py test \
  gcloud.tests.plugin_gateway.test_native_forms \
  gcloud.tests.plugin_gateway.test_builtin_catalog -v 2
```

Expected: PASS；JOB 快速执行脚本的 input URL、注册 key 和输出表单均正确，原 `form_schema` 断言仍通过。

- [ ] **Step 6: Commit**

```bash
git add gcloud/plugin_gateway/services/native_forms.py \
  gcloud/plugin_gateway/services/builtin_catalog.py \
  gcloud/tests/plugin_gateway/test_native_forms.py \
  gcloud/tests/plugin_gateway/test_builtin_catalog.py
git commit -m "feat: 原样暴露内置插件表单协议 --story=133649781"
```

---

### Task 2: 原样描述第三方插件表单并保持精确版本

**Files:**
- Modify: `gcloud/plugin_gateway/services/native_forms.py`
- Modify: `gcloud/plugin_gateway/services/catalog.py`
- Modify: `gcloud/tests/plugin_gateway/test_native_forms.py`
- Modify: `gcloud/tests/plugin_gateway/test_catalog.py`

- [ ] **Step 1: 写第三方协议失败测试**

覆盖 renderform、jsonschema 和无表单三种输入：

```python
def test_builds_renderform_descriptor(self):
    detail = {
        "forms": {
            "renderform": "window.$.atoms.demo = [{tag_code: 'input', attrs: {name: 'x'}}]",
            "is_embedded": True,
        }
    }
    self.assertEqual(
        build_third_party_forms("demo", detail),
        {
            "input": {
                "type": "renderform",
                "key": "demo",
                "data": detail["forms"]["renderform"],
                "is_embedded": True,
                "base": None,
            },
            "output": None,
        },
    )


def test_builds_jsonschema_descriptor(self):
    schema = {"type": "object", "properties": {"x": {"type": "string"}}}
    forms = build_third_party_forms("demo", {"forms": {"jsonschema": schema}})
    self.assertEqual(forms["input"]["type"], "jsonschema")
    self.assertEqual(forms["input"]["data"], schema)


def test_returns_null_input_when_provider_has_no_native_form(self):
    self.assertEqual(
        build_third_party_forms("demo", {"forms": {}}),
        {"input": None, "output": None},
    )
```

在 `test_catalog.py` 的第三方详情夹具中同时断言：

```python
self.assertEqual(detail["plugin_version"], "1.2.3")
self.assertEqual(detail["forms"]["input"]["type"], "renderform")
self.assertEqual(detail["forms"]["input"]["key"], "danny-test-plugi")
self.assertIn("form_schema", detail)
mock_get_plugin_detail_schema.assert_called_once_with("danny-test-plugi", "1.2.3")
```

新增不存在版本测试，断言 `_get_plugin_detail_schema` 未被调用且抛出 `PluginGatewayVersionNotFoundError`。

- [ ] **Step 2: 运行失败测试**

Run:

```bash
python manage.py test \
  gcloud.tests.plugin_gateway.test_native_forms \
  gcloud.tests.plugin_gateway.test_catalog -v 2
```

Expected: FAIL，第三方 detail 没有原生 `forms`。

- [ ] **Step 3: 实现第三方表单描述**

在 `native_forms.py` 增加：

```python
def _native_descriptor(form_type, key, data, is_embedded=True, base=None):
    if data in (None, ""):
        return None
    return {
        "type": form_type,
        "key": key,
        "data": data if is_embedded else absolute_sops_url(data),
        "is_embedded": bool(is_embedded),
        "base": absolute_sops_url(base) if base else None,
    }


def build_third_party_forms(plugin_code, detail_schema):
    provider_forms = detail_schema.get("forms")
    if not isinstance(provider_forms, dict):
        provider_forms = {}

    renderform = provider_forms.get("renderform")
    jsonschema = provider_forms.get("jsonschema")
    if renderform:
        input_form = _native_descriptor(
            "renderform",
            plugin_code,
            renderform,
            provider_forms.get("is_embedded", True),
            provider_forms.get("base"),
        )
    elif isinstance(jsonschema, dict):
        input_form = _native_descriptor("jsonschema", plugin_code, jsonschema)
    else:
        input_form = None

    return {"input": input_form, "output": None}
```

如果真实插件详情把 JSON Schema 放在 `forms.schema` 或 `forms.input`，先用现有 serializer/client 返回样例补充测试，再在这个函数中显式兼容；不要把普通 `inputs` JSON Schema误判为原生表单。

- [ ] **Step 4: 在统一 detail 中同时返回原生 forms 与旧 form_schema**

在 `PluginGatewayCatalogService.get_plugin_detail`：

```python
if plugin["plugin_source"] == PLUGIN_SOURCE_BUILTIN:
    forms = detail_schema.get("forms") or {"input": None, "output": None}
else:
    forms = build_third_party_forms(plugin["plugin_code"], detail_schema)

detail["forms"] = forms
```

现有 `build_structured_form_schema` 和 `detail["form_schema"]` 保持不变。

- [ ] **Step 5: 运行测试至通过**

Run:

```bash
python manage.py test \
  gcloud.tests.plugin_gateway.test_native_forms \
  gcloud.tests.plugin_gateway.test_catalog -v 2
```

Expected: PASS；三种表单语义明确，指定版本无隐式回退，旧 `form_schema` 测试不回归。

- [ ] **Step 6: Commit**

```bash
git add gcloud/plugin_gateway/services/native_forms.py \
  gcloud/plugin_gateway/services/catalog.py \
  gcloud/tests/plugin_gateway/test_native_forms.py \
  gcloud/tests/plugin_gateway/test_catalog.py
git commit -m "feat: 原样暴露第三方插件表单协议 --story=133649781"
```

---

### Task 3: 复用执行解析生成表单上下文

**Files:**
- Modify: `gcloud/plugin_gateway/services/context.py`
- Modify: `gcloud/plugin_gateway/services/catalog.py`
- Modify: `gcloud/apigw/views/plugin_gateway.py`
- Modify: `gcloud/tests/plugin_gateway/test_context_resolve.py`
- Modify: `gcloud/tests/plugin_gateway/test_catalog.py`
- Modify: `gcloud/tests/apigw/views/test_plugin_gateway.py`

- [ ] **Step 1: 写上下文一致性失败测试**

在 `test_context_resolve.py` 创建 `bk_biz_id=100605` 的 Project 和来源配置：

```python
@override_settings(BK_SOPS_HOST="https://bksops.example.com/")
def test_resolve_form_context_reuses_biz_project_resolution(self):
    context = PluginGatewayContextService.resolve_form_context(
        source_config=self.source_config,
        scope_type="biz",
        scope_value="100605",
        plugin_source="third_party",
        plugin_code="danny-test-plugi",
    )
    self.assertEqual(context["project"]["id"], self.project.id)
    self.assertEqual(context["project"]["bk_biz_id"], 100605)
    self.assertEqual(context["biz_cc_id"], 100605)
    self.assertEqual(
        context["bk_plugin_api_host"]["danny-test-plugi"],
        "https://bksops.example.com/plugin_service/data_api/danny-test-plugi/",
    )
    json.dumps(context)
```

另加 default project、scope map、无可解析 Project 三条测试，错误类型必须为 `PluginGatewayContextResolveError`。

在 APIGW view 测试中断言：

```python
request.GET = {
    "version": "v2.0",
    "source_key": "sops",
    "scope_type": "biz",
    "scope_value": "100605",
}
mock_get_plugin_detail.assert_called_once_with(
    request=request,
    plugin_id="builtin__job_fast_execute_script",
    version="v2.0",
    source_config=source_config,
    scope_type="biz",
    scope_value="100605",
    operator="dannydeng",
)
```

同时覆盖：

- query 中伪造 `operator=other` 不会改变传入 service 的 operator。
- `source_key` 携带非空 signed username 时，即使 `verified=false` 或 verified 字段缺省也成功；signed username 缺失或 caller app 缺失时返回 forbidden。
- 不传 `source_key` 时沿用旧调用，响应可以没有 `form_context`。
- source 不存在、disabled、Project 解析失败映射为明确 4xx。

- [ ] **Step 2: 运行失败测试**

Run:

```bash
python manage.py test \
  gcloud.tests.plugin_gateway.test_context_resolve \
  gcloud.tests.plugin_gateway.test_catalog \
  gcloud.tests.apigw.views.test_plugin_gateway -v 2
```

Expected: FAIL，`resolve_form_context` 和新增 detail 参数不存在。

- [ ] **Step 3: 实现纯数据上下文**

在 `PluginGatewayContextService` 中增加：

```python
@classmethod
def resolve_form_context(
    cls,
    source_config,
    scope_type,
    scope_value,
    plugin_source=None,
    plugin_code=None,
):
    resolved = cls.resolve_run_context(
        source_config,
        {"scope_type": scope_type, "scope_value": scope_value},
    )

    from gcloud.core.models import Project

    project = Project.objects.get(id=resolved["project_id"])
    site_url = settings.BK_SOPS_HOST.rstrip("/") + "/"
    context = {
        "project": {
            "id": project.id,
            "bk_biz_id": project.bk_biz_id,
            "from_cmdb": project.from_cmdb,
        },
        "biz_cc_id": project.bk_biz_id,
        "site_url": site_url,
        "component": urljoin(site_url, "api/v3/component/"),
        "variable": urljoin(site_url, "api/v3/variable/"),
        "template": urljoin(site_url, "api/v3/template/"),
        "instance": urljoin(site_url, "api/v3/taskflow/"),
        "bk_plugin_api_host": {},
    }
    if plugin_source == PLUGIN_SOURCE_THIRD_PARTY and plugin_code:
        context["bk_plugin_api_host"][plugin_code] = urljoin(
            site_url,
            "plugin_service/data_api/{}/".format(plugin_code),
        )
    return context
```

补齐 `settings/urljoin/PLUGIN_SOURCE_THIRD_PARTY` import。operator 不写入返回值；它只用于认证和日志。

- [ ] **Step 4: detail 接受已认证来源上下文**

扩展 service 签名：

```python
def get_plugin_detail(
    cls,
    request,
    plugin_id,
    version=None,
    source_config=None,
    scope_type=None,
    scope_value=None,
    operator="",
):
```

仅当 `source_config` 不为 `None` 时调用 `resolve_form_context`，并写入：

```python
detail["form_context"] = PluginGatewayContextService.resolve_form_context(
    source_config=source_config,
    scope_type=scope_type,
    scope_value=scope_value,
    plugin_source=plugin["plugin_source"],
    plugin_code=plugin["plugin_code"],
)
```

用结构化日志记录 `source_key/plugin_id/plugin_version/scope/operator`，不得记录 Cookie。

- [ ] **Step 5: APIGW view 只信任认证 operator**

`get_plugin_gateway_detail` 中：

```python
source_key = request.GET.get("source_key")
source_config = None
if source_key:
    operator = getattr(request, "_apigw_jwt_username", "")
    if not operator:
        return _error_response("signed APIGW username is required", forbidden_code)
    _caller_app_code(request)
    source_config = PluginGatewaySourceConfig.objects.get(
        source_key=source_key,
        is_enabled=True,
    )
else:
    operator = _caller_username(request)

plugin_detail = PluginGatewayCatalogService.get_plugin_detail(
    request=request,
    plugin_id=plugin_id,
    version=request.GET.get("version"),
    source_config=source_config,
    scope_type=request.GET.get("scope_type"),
    scope_value=request.GET.get("scope_value"),
    operator=operator,
)
```

捕获 `PermissionError`、`PluginGatewaySourceConfig.DoesNotExist` 和 `PluginGatewayContextResolveError`，分别返回 forbidden、来源不可用和参数无效错误；不读取 `request.GET["operator"]`。资源 YAML 保持 `userVerifiedRequired:false`、`appVerifiedRequired:true`、`resourcePermissionRequired:true`。

- [ ] **Step 6: 运行测试至通过**

Run:

```bash
python manage.py test \
  gcloud.tests.plugin_gateway.test_context_resolve \
  gcloud.tests.plugin_gateway.test_catalog \
  gcloud.tests.apigw.views.test_plugin_gateway -v 2
```

Expected: PASS；detail 与 execute 解析到同一 Project，旧 detail 调用仍兼容。

- [ ] **Step 7: Commit**

```bash
git add gcloud/plugin_gateway/services/context.py \
  gcloud/plugin_gateway/services/catalog.py \
  gcloud/apigw/views/plugin_gateway.py \
  gcloud/tests/plugin_gateway/test_context_resolve.py \
  gcloud/tests/plugin_gateway/test_catalog.py \
  gcloud/tests/apigw/views/test_plugin_gateway.py
git commit -m "feat: 插件详情返回业务表单上下文 --story=133649781"
```

---

### Task 4: 对登记接口开放有限凭证型 CORS

**Files:**
- Create: `gcloud/plugin_gateway/cors.py`
- Modify: `gcloud/plugin_gateway/apps.py`
- Modify: `config/default.py`
- Modify: `env_v2.py`
- Modify: `env_v3.py`
- Modify: `plugin_service/api.py`
- Create: `gcloud/tests/plugin_gateway/test_cors.py`
- Create: `gcloud/tests/plugin_gateway/test_plugin_service_api.py`

- [ ] **Step 1: 写 Origin 与路由组合失败测试**

`test_cors.py` 直接测试 signal handler，避免把中间件细节混入白名单规则：

```python
@override_settings(
    PLUGIN_GATEWAY_FORM_CORS_ALLOWED_ORIGINS={
        "https://stag-dot-bkflow-eng-svc.bkapps-sz.woa.com"
    }
)
def test_allows_registered_route_for_exact_origin(self):
    request = self.factory.get(
        "/pipeline/cc_get_business_list/",
        HTTP_ORIGIN="https://stag-dot-bkflow-eng-svc.bkapps-sz.woa.com",
    )
    self.assertTrue(allow_plugin_form_cors(None, request))


def test_rejects_unregistered_pipeline_route(self):
    request = self.factory.get(
        "/pipeline/admin/private/",
        HTTP_ORIGIN=self.allowed_origin,
    )
    self.assertFalse(allow_plugin_form_cors(None, request))


def test_rejects_suffix_or_scheme_mismatch(self):
    for origin in (
        "http://stag-dot-bkflow-eng-svc.bkapps-sz.woa.com",
        "https://stag-dot-bkflow-eng-svc.bkapps-sz.woa.com.evil.example",
    ):
        request = self.factory.get(
            "/pipeline/cc_get_business_list/",
            HTTP_ORIGIN=origin,
        )
        self.assertFalse(allow_plugin_form_cors(None, request))
```

覆盖首批登记接口：

- `/pipeline/cc_get_business_list/`
- `/pipeline/job_get_public_script_name_list/`
- `/pipeline/job_get_script_name_list/<path>`
- `/pipeline/get_job_account_list/<path>`
- `/pipeline/jobv3_get_instance_list/<path>`
- `/plugin_service/data_api/<plugin_code>/<path>`

再用 Django client 发 OPTIONS/GET，断言成功响应有：

```text
Access-Control-Allow-Origin: <exact origin>
Access-Control-Allow-Credentials: true
Vary: Origin
```

集成测试使用 `modify_settings` 在测试 client 初始化前 prepend
`corsheaders.middleware.CorsMiddleware`，不能只 `override_settings` 一个已经加载完成的 `MIDDLEWARE`：

```python
@modify_settings(
    MIDDLEWARE={"prepend": "corsheaders.middleware.CorsMiddleware"}
)
class PluginFormCorsMiddlewareTestCase(TestCase):
    ...
```

- [ ] **Step 2: 写第三方 data_api 跨域可见性失败测试**

在 `gcloud/tests/plugin_gateway/test_plugin_service_api.py` 覆盖：

```python
@override_settings(PLUGIN_GATEWAY_FORM_CORS_ALLOWED_ORIGINS={ALLOWED_ORIGIN})
@patch("plugin_service.api.PluginGatewayCatalogService.get_plugin_reference")
def test_cross_origin_data_api_requires_visible_plugin(self, get_reference):
    get_reference.return_value = None
    response = self.client.get(
        "/plugin_service/data_api/blocked/demo/",
        HTTP_ORIGIN=ALLOWED_ORIGIN,
    )
    self.assertEqual(response.status_code, 403)


def test_same_origin_data_api_keeps_legacy_behavior(self):
    response = self.client.get("/plugin_service/data_api/demo/options/")
    self.assertNotEqual(response.status_code, 403)
```

可见插件测试断言 client 收到真实 `request.user.username`。

- [ ] **Step 3: 运行测试并确认失败**

Run:

```bash
python manage.py test \
  gcloud.tests.plugin_gateway.test_cors \
  gcloud.tests.plugin_gateway.test_plugin_service_api -v 2
```

Expected: FAIL，signal handler、设置项和跨域 guard 尚不存在。

- [ ] **Step 4: 增加独立环境变量与中间件开关**

`env_v2.py` 和 `env_v3.py`：

```python
BKAPP_PLUGIN_GATEWAY_FORM_CORS_ALLOW = os.getenv(
    "BKAPP_PLUGIN_GATEWAY_FORM_CORS_ALLOW",
    "",
)
BKAPP_PLUGIN_GATEWAY_FORM_CORS_WHITELIST = os.getenv(
    "BKAPP_PLUGIN_GATEWAY_FORM_CORS_WHITELIST",
    "",
)
```

`config/default.py`：

```python
PLUGIN_GATEWAY_FORM_CORS_ALLOW = str(
    env.BKAPP_PLUGIN_GATEWAY_FORM_CORS_ALLOW or ""
).lower() in {"1", "true", "yes", "on"}
PLUGIN_GATEWAY_FORM_CORS_ALLOWED_ORIGINS = {
    origin.strip().rstrip("/")
    for origin in env.BKAPP_PLUGIN_GATEWAY_FORM_CORS_WHITELIST.split(",")
    if origin.strip()
}

if env.BKAPP_CORS_ALLOW or PLUGIN_GATEWAY_FORM_CORS_ALLOW:
    MIDDLEWARE = ("corsheaders.middleware.CorsMiddleware",) + MIDDLEWARE

CORS_ALLOW_CREDENTIALS = bool(env.BKAPP_CORS_ALLOW or PLUGIN_GATEWAY_FORM_CORS_ALLOW)
```

保留现有 `BKAPP_CORS_ALLOW/CORS_ORIGIN_WHITELIST` 行为。插件表单 Origin 不加入全局 `CORS_ORIGIN_WHITELIST`，由 signal 按路径决定。

- [ ] **Step 5: 实现精确 signal 判定**

创建 `gcloud/plugin_gateway/cors.py`：

```python
import re

from django.conf import settings

PLUGIN_FORM_PATHS = (
    re.compile(r"^/pipeline/cc_get_business_list/$"),
    re.compile(r"^/pipeline/job_get_public_script_name_list/$"),
    re.compile(r"^/pipeline/job_get_script_name_list/(?:.*)$"),
    re.compile(r"^/pipeline/get_job_account_list/(?:.*)$"),
    re.compile(r"^/pipeline/jobv3_get_instance_list/(?:.*)$"),
    re.compile(r"^/plugin_service/data_api/[^/]+/.+$"),
)


def is_plugin_form_cross_origin_request(request):
    origin = request.META.get("HTTP_ORIGIN", "").rstrip("/")
    return bool(
        origin
        and origin in settings.PLUGIN_GATEWAY_FORM_CORS_ALLOWED_ORIGINS
    )


def allow_plugin_form_cors(sender, request, **kwargs):
    if not settings.PLUGIN_GATEWAY_FORM_CORS_ALLOW:
        return False
    if not is_plugin_form_cross_origin_request(request):
        return False
    return any(pattern.match(request.path) for pattern in PLUGIN_FORM_PATHS)
```

在 `PluginGatewayConfig.ready()` 中幂等连接：

```python
from corsheaders.signals import check_request_enabled

from gcloud.plugin_gateway.cors import allow_plugin_form_cors

check_request_enabled.connect(
    allow_plugin_form_cors,
    dispatch_uid="plugin_gateway_form_cors",
)
```

确认 Django 实际加载 `PluginGatewayConfig`；若 settings 仅登记字符串 app name，则把该项改为 `gcloud.plugin_gateway.apps.PluginGatewayConfig`。

- [ ] **Step 6: 跨域 data_api 只允许网关可见第三方插件**

在 `get_plugin_api_data` 最前面增加：

```python
if is_plugin_form_cross_origin_request(request):
    plugin = PluginGatewayCatalogService.get_plugin_reference(plugin_code)
    if not plugin or plugin.get("plugin_source") != PLUGIN_SOURCE_THIRD_PARTY:
        return Response(
            {"result": False, "data": None, "message": "plugin is not available"},
            status=status.HTTP_403_FORBIDDEN,
        )
```

该查询复用 `get_plugin_reference`，因此同时遵守来源目录、插件存在性和 `do_not_open_list`。没有 `Origin` 或 Origin 不属于专用配置时不进入该 guard，保持标准运维同源存量页面行为。

- [ ] **Step 7: 运行 CORS 与 data_api 测试**

Run:

```bash
python manage.py test \
  gcloud.tests.plugin_gateway.test_cors \
  gcloud.tests.plugin_gateway.test_plugin_service_api -v 2
```

Expected: PASS；精确 Origin + 登记路由有凭证 CORS，任一条件不满足均不放行，黑名单插件跨域 403，同源调用不回归。

- [ ] **Step 8: 运行目录和黑名单回归**

Run:

```bash
python manage.py test \
  gcloud.tests.plugin_gateway.test_catalog \
  gcloud.tests.plugin_gateway.test_execution -v 2
```

Expected: PASS；list/detail/execute 的黑名单行为一致。

- [ ] **Step 9: Commit**

```bash
git add gcloud/plugin_gateway/cors.py \
  gcloud/plugin_gateway/apps.py \
  config/default.py env_v2.py env_v3.py \
  plugin_service/api.py \
  gcloud/tests/plugin_gateway/test_cors.py \
  gcloud/tests/plugin_gateway/test_plugin_service_api.py
git commit -m "feat: 限定开放插件表单跨域访问 --story=133649781"
```

---

### Task 5: 同步 APIGW 文档并完成回归

**Files:**
- Modify: `docs/zh_hans/apidoc/plugin_gateway_get_plugin_detail.md`
- Modify: `docs/en/apidoc/plugin_gateway_get_plugin_detail.md`
- Modify: `gcloud/apigw/management/commands/data/api-resources.yml`
- Regenerate: `gcloud/apigw/docs/apigw-docs.tgz`
- Modify: `docs/zh_hans/deploy/plugin_gateway_deploy.md`
- Modify: `docs/en/deploy/plugin_gateway_deploy.md`

- [ ] **Step 1: 更新 detail 请求文档**

记录可选查询参数：

```yaml
version:
  type: string
  required: false
source_key:
  type: string
  required: false
scope_type:
  type: string
  required: false
scope_value:
  type: string
  required: false
```

说明：

- `source_key` 未提供时沿用旧 detail 行为，不解析 `form_context`。
- `source_key` 提供时 `scope_type/scope_value` 参与 Project 解析。
- 不带 `source_key` 时沿用旧行为；带 `source_key` 时 operator 来自 APIGW 已认证调用应用代传的 signed JWT 非空 username，不是接口参数，不要求浏览器 user token。
- `forms.input/output` 的固定字段和四种消费语义。
- 过渡期 `form_schema` 仍可能存在，但新接入应读取 `forms`。

- [ ] **Step 2: 更新部署文档**

提供 Stage 示例：

```text
BKAPP_PLUGIN_GATEWAY_FORM_CORS_ALLOW=true
BKAPP_PLUGIN_GATEWAY_FORM_CORS_WHITELIST=https://stag-dot-bkflow-eng-svc.bkapps-sz.woa.com
```

写明不能配置 `*`，Origin 必须含 scheme 且不含路径；发布后先验证 Cookie、CSRF、CSP 和真实用户名，再测试动态表单。认证任一项失败即暂停，不启用匿名降级。

- [ ] **Step 3: 重新打包 APIGW 文档**

先按 `.ai/rules/api-change-checklist.mdc` 和仓库已有打包脚本确认命令，再运行仓库标准 APIGW 文档打包命令。验证归档确实包含更新后的中英文 detail 文档：

```bash
tar -tzf gcloud/apigw/docs/apigw-docs.tgz | rg "plugin_gateway_get_plugin_detail"
```

Expected: 中英文文档路径均存在。

- [ ] **Step 4: 运行完整插件网关回归**

Run:

```bash
python manage.py test gcloud.tests.plugin_gateway -v 2
python manage.py test gcloud.tests.apigw.views.test_plugin_gateway -v 2
```

Expected: PASS，无永久 RUNNING 测试，无 JSONField lazy translation 序列化错误。

- [ ] **Step 5: 静态校验**

Run:

```bash
git diff --check
python -m compileall \
  gcloud/plugin_gateway \
  gcloud/apigw/views/plugin_gateway.py \
  plugin_service/api.py
```

Expected: 均退出 0。

- [ ] **Step 6: Commit**

```bash
git add docs/zh_hans/apidoc/plugin_gateway_get_plugin_detail.md \
  docs/en/apidoc/plugin_gateway_get_plugin_detail.md \
  gcloud/apigw/management/commands/data/api-resources.yml \
  gcloud/apigw/docs/apigw-docs.tgz \
  docs/zh_hans/deploy/plugin_gateway_deploy.md \
  docs/en/deploy/plugin_gateway_deploy.md
git commit -m "docs: 同步插件原生表单网关文档 --story=133649781"
```

---

## Stage Acceptance Gate

严格按以下顺序验收；某一步发现未发布或未配置就停止：

1. detail 在不带 `source_key` 时仍返回旧兼容结构。
2. detail 带 `source_key=sops&scope_type=biz&scope_value=100605` 时返回 Project 对应的 `form_context`。
3. JOB 快速执行脚本精确版本返回 `component_js`，注册 key 为 `job_fast_execute_script`，静态 URL 可访问。
4. `danny-test-plugi` 精确版本返回原始 `renderform` 或 `jsonschema`，`bk_plugin_api_host` 指向该插件 data_api。
5. BKFlow Origin 对已登记接口的 OPTIONS/GET 有凭证 CORS；未登记 `/pipeline/` 接口没有该响应头。
6. BKFlow 通过已认证且获资源权限的 caller app 访问 `source_key` detail 时，signed JWT 携带的非空 username 仍为 `dannydeng`；不依赖浏览器 user token。
7. 黑名单插件的 list/detail/data_api 跨域请求均不可用。
8. 已保存但已下架版本返回版本失效，不回退到 default/latest。
9. 同步、轮询、回调执行回归均通过；SAP 存量插件不执行。

## Spec Coverage Map

| Spec Requirement | Plan Coverage |
|---|---|
| §1.3 内置 `component_js` | Task 1 |
| §1.3 第三方 `renderform/jsonschema` 与精确版本 | Task 2 |
| §1.4 Project/form context 与认证 operator | Task 3 |
| §1.5 精确 Origin、登记路由、凭证 CORS | Task 4 |
| §1.5 第三方 data_api 可见性与同源兼容 | Task 4 |
| §9 自动测试与 Stage 验收 | Tasks 1-5 + Stage Acceptance Gate |
| §10 加法发布与删除旧转换的时机 | Global Constraints + Follow-up Cleanup Gate |

## Follow-up Cleanup Gate

只有 BKFlow V4 在 Stage 完成上述验收并稳定运行后，才另建变更删除：

- detail 的 `form_schema`
- `gcloud/plugin_gateway/services/form_schema.py`
- `gcloud/plugin_gateway/services/builtin_form_schema.py`
- 对应旧转换测试和插件级控件覆盖

该清理不属于本计划当前分支，不能与加法发布合并实施。
