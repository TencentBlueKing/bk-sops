# 标准运维工蜂内部代码 Python 3.11 迁移 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立可持续同步开源多租户版本的工蜂集成主线，将内部环境长期需要的代码升级到 Python 3.11，并生成能够参与业务灰度的完整内部制品。

**Architecture:** 工蜂 `V3.6.X` 保持 Python 3.6 并继续承载 legacy 和 Bridge。新的工蜂 `dev_multi_tenant` 以锁定的开源 `upstream/dev_multi_tenant` SHA 为基线，只逐项移植清单中确认需要长期保留的内部代码；所有目标模块从同一个验收 SHA 构建，并由业务能力检查阻止使用未完成改造的内部插件或接口。

**Tech Stack:** Python 3.11.10、Django 4.2.30、Celery 5.2.7、bamboo-pipeline 4.0.4、bamboo-engine 3.0.5、MySQL、RabbitMQ、Redis、pytest、工蜂 CI/CD

**Spec:** `docs/specs/2026-09-04-multi-tenant-gray-migration-design.md`

**TAPD:** [标准运维内部环境多租户版本平滑迁移](https://tapd.woa.com/10131351/prong/stories/view/1010131351137932246)

## Global Constraints

- 工蜂 `V3.6.X`、现有 Python 3.6 运行时、RabbitMQ、Redis、队列和发布模块不得原地升级或改名。
- 开源同步链固定为 `master -> release_humming_bird -> dev_multi_tenant`；内部目标发布再从开源 `dev_multi_tenant` 进入工蜂 `dev_multi_tenant`。
- 禁止将工蜂 `V3.6.X` 整体 merge 到目标主线；每项内部差异必须有明确处理结论和验证证据。
- Bridge 临时路由、旧模型兼容、旧 Celery 签名和旧引擎状态机只能存在于工蜂旧版分支。
- 工蜂目标主线只包含长期内部能力、正式对接适配和多租户目标实现。
- Web、API Server、Pipeline Worker、Callback、Cleaner、API Inner 和 Open Plugin 必须从同一目标 SHA 构建。
- 一个业务只有在其流程引用的全部内部能力都标记为 `ready` 后才能进入 mt 灰度。
- 实施前设置 `BK_SOPS_MIGRATION_TAPD_STORY`；所有提交消息追加 `--story=${BK_SOPS_MIGRATION_TAPD_STORY}`。
- 所有工作在独立 worktree 中执行；主工作区已有改动不得暂存、清理或覆盖。

---

## File Structure

以下文件只提交到工蜂目标主线，不回推到开源仓库：

- `scripts/migration/internal_overlay_manifest.yaml`：内部差异、目标动作和验证证据的唯一清单。
- `scripts/migration/validate_internal_overlay_manifest.py`：检查清单字段、状态和证据完整性。
- `scripts/migration/check_business_target_capabilities.py`：扫描业务流程引用并生成灰度准入结论。
- `gcloud/tests/migration/test_internal_overlay_manifest.py`：清单校验器测试。
- `gcloud/tests/migration/test_business_target_capabilities.py`：业务能力扫描测试。
- `gcloud/tests/internal/test_internal_imports.py`：内部模块在 Python 3.11 下的导入和注册测试。
- `gcloud/tests/internal/test_internal_integrations.py`：内部认证、SDK 和第三方交互契约测试。
- `gcloud/tests/internal/test_internal_components.py`：内部插件注册和执行契约测试。
- `docs/zh_hans/ops/internal_overlay_py311_matrix.md`：面向发布评审的迁移矩阵和验收证据索引。

现有内部代码按责任域修改：

- `requirements.txt`、`runtime.txt`：Python 3.11 兼容依赖和运行时。
- `env.py`、`env_ieod.py`、`gcloud/conf/sites/ieod/ver_settings.py`：内部环境和 SDK 入口。
- `pipeline_plugins/components/collections/sites/ieod/`：内部插件实现。
- `tencentcloud/`：工蜂内维护的本地 SDK 或兼容代码。
- `app_desc.yaml`、`Procfile`、`bin/`：内部模块构建和启动配置。

---

### Task 1: 冻结源 SHA 并建立内部差异清单

**Files:**
- Create: `scripts/migration/internal_overlay_manifest.yaml`
- Create: `scripts/migration/validate_internal_overlay_manifest.py`
- Create: `gcloud/tests/migration/test_internal_overlay_manifest.py`
- Create: `docs/zh_hans/ops/internal_overlay_py311_matrix.md`

**Interfaces:**
- Consumes: 刷新后的 `upstream/dev_multi_tenant`、`upstream/master` 和 `woa/V3.6.X`。
- Produces: 清单字段 `source_path`、`source_commit`、`category`、`action`、`status`、`owner`、`target_paths`、`target_version`、`modules`、`test_command`、`evidence`。
- Produces: `validate_internal_overlay_manifest.py --fail-on pending,unknown`，成功返回 0，清单不完整返回 1。

- [ ] **Step 1: 写清单校验失败测试**

```python
def test_manifest_rejects_ported_item_without_test_evidence(tmp_path):
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text(
        "items:\n"
        "  - source_path: env_ieod.py\n"
        "    source_commit: abc123\n"
        "    category: integration\n"
        "    action: port\n"
        "    status: ported\n"
        "    owner: platform\n"
        "    target_paths: [env_ieod.py]\n"
        "    target_version: python-3.11\n"
        "    modules: [default]\n"
        "    test_command: ''\n"
        "    evidence: ''\n",
        encoding="utf-8",
    )
    assert validate_manifest(manifest, fail_on={"pending", "unknown"}) == 1
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `pytest gcloud/tests/migration/test_internal_overlay_manifest.py -q`

Expected: FAIL，提示校验器尚不存在。

- [ ] **Step 3: 实现清单格式和校验器**

`internal_overlay_manifest.yaml` 每项使用以下结构：

```yaml
items:
  - source_path: env_ieod.py
    source_commit: "46171483cf69cf928c52ad48fc06ace96f63a24d"
    category: integration
    action: port
    status: pending
    owner: platform
    target_paths:
      - env_ieod.py
    target_version: python-3.11
    modules:
      - default
    test_command: python -m pytest gcloud/tests/internal/test_internal_integrations.py -q
    evidence: ""
```

校验器必须拒绝：缺字段、未知枚举、`ported/reimplemented` 没有测试命令或证据、
`dropped/legacy_only` 没有原因，以及 `source_commit` 不是 40 位 SHA 的条目。

- [ ] **Step 4: 生成并人工归类工蜂差异**

Run:
`git diff --name-status "$(git merge-base upstream/master woa/V3.6.X)"..woa/V3.6.X`

将每个差异归入 `deployment`、`integration`、`plugin`、`frontend`、`dependency`、
`obsolete`、`legacy_runtime` 或 `migration_only`，并将动作设为 `port`、`reimplement`、
`drop` 或 `legacy_only`。

- [ ] **Step 5: 运行校验和人工评审**

Run: `python scripts/migration/validate_internal_overlay_manifest.py --fail-on unknown`

Expected: exit code 0；允许待实施的 `pending`，不允许未归类的 `unknown`。

- [ ] **Step 6: 提交**

```bash
git add scripts/migration/internal_overlay_manifest.yaml scripts/migration/validate_internal_overlay_manifest.py gcloud/tests/migration/test_internal_overlay_manifest.py docs/zh_hans/ops/internal_overlay_py311_matrix.md
git commit -m "docs: 建立内部代码迁移清单 --story=${BK_SOPS_MIGRATION_TAPD_STORY}"
```

---

### Task 2: 建立工蜂多租户集成主线

**Files:**
- Create in Gongfeng: branch `dev_multi_tenant`
- Create: `docs/zh_hans/ops/internal_target_source_provenance.md`
- Modify: 工蜂分支保护和 CI 配置

**Interfaces:**
- Consumes: `upstream/dev_multi_tenant` 精确 SHA。
- Produces: 受保护的 `woa/dev_multi_tenant`。
- Produces: 目标源码溯源记录，包含开源 SHA、工蜂 SHA、同步时间和同步 MR。

- [ ] **Step 1: 刷新并记录三条源分支**

Run: `git fetch --prune upstream master release_humming_bird dev_multi_tenant`

Run: `git fetch --prune woa V3.6.X`

Run: `git show -s --format='%H %cI %s' upstream/dev_multi_tenant woa/V3.6.X`

Expected: 两个 SHA 均可解析，且工作区无本任务之外的暂存内容。

- [ ] **Step 2: 从开源目标 SHA 创建工蜂目标主线**

首次建立分支时执行：

```bash
target_sha=$(git rev-parse upstream/dev_multi_tenant)
git push woa "${target_sha}:refs/heads/dev_multi_tenant"
```

随后在工蜂将 `dev_multi_tenant` 设置为受保护分支，禁止 force push，要求 MR、CI 和
Code Review 后才能更新。

- [ ] **Step 3: 写入源码溯源记录**

在文档中记录固定分支名 `upstream/dev_multi_tenant`、`woa/dev_multi_tenant`，并把
`git rev-parse upstream/dev_multi_tenant`、`git rev-parse woa/dev_multi_tenant` 的完整
输出和创建分支的工蜂 MR IID 原样写入；短 SHA、分支浮动名称和未合入 MR 不得作为基线。

- [ ] **Step 4: 验证目标主线没有旧版整体合并**

Run: `git merge-base --is-ancestor woa/V3.6.X woa/dev_multi_tenant`

Expected: 非 0；工蜂 `V3.6.X` 不是目标主线祖先。

Run: `git merge-base --is-ancestor upstream/dev_multi_tenant woa/dev_multi_tenant`

Expected: exit code 0。

- [ ] **Step 5: 提交溯源文件并通过 MR 合入**

```bash
git add docs/zh_hans/ops/internal_target_source_provenance.md
git commit -m "docs: 记录工蜂多租户源码基线 --story=${BK_SOPS_MIGRATION_TAPD_STORY}"
```

---

### Task 3: 升级内部依赖和基础运行时

**Files:**
- Modify: `requirements.txt`
- Modify: `runtime.txt`
- Modify: `tencentcloud/`
- Create: `gcloud/tests/internal/test_internal_imports.py`
- Modify: `scripts/migration/internal_overlay_manifest.yaml`

**Interfaces:**
- Consumes: manifest 中 `dependency` 类条目的 `target_version`。
- Produces: Python 3.11 下可安装、可导入的内部依赖集合。
- Produces: `test_internal_imports.py` 对所有移植内部模块执行导入和 Django app 初始化。

- [ ] **Step 1: 写旧依赖不允许进入目标版本的失败测试**

```python
FORBIDDEN_TARGET_PINS = {
    "pip": "9.0.1",
    "ddtrace": "0.15.0",
    "greenlet": "1.1.3",
}


def test_target_requirements_do_not_keep_legacy_runtime_pins():
    requirements = Path("requirements.txt").read_text(encoding="utf-8")
    for package, version in FORBIDDEN_TARGET_PINS.items():
        assert f"{package}=={version}" not in requirements
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `pytest gcloud/tests/internal/test_internal_imports.py -q`

Expected: FAIL，列出仍存在的旧运行时 pin 或不可导入模块。

- [ ] **Step 3: 按 manifest 版本升级依赖**

从目标 `requirements.txt` 出发，只加入 manifest 已批准且通过 Python 3.11 验证的内部
SDK 版本。移除旧版 `pip==9.0.1`、`ddtrace==0.15.0`、`greenlet==1.1.3` 等遗留 pin；
本地维护的 `tencentcloud/` 必须通过 `compileall` 和实际导入测试。

- [ ] **Step 4: 构建全新环境并验证安装**

Run: `python3.11 -m venv .venv-internal-target`

Run: `.venv-internal-target/bin/python -m pip install -r requirements.txt`

Run: `.venv-internal-target/bin/python -m compileall env_ieod.py gcloud pipeline_plugins tencentcloud`

Expected: 安装和编译均成功，无 Python 2/3.6 语法错误或缺失 wheel。

- [ ] **Step 5: 运行导入测试并更新证据**

Run: `.venv-internal-target/bin/pytest gcloud/tests/internal/test_internal_imports.py -q`

Expected: PASS；将命令、CI URL 和结果写回 manifest 对应条目的 `evidence`。

- [ ] **Step 6: 提交**

```bash
git add requirements.txt runtime.txt tencentcloud gcloud/tests/internal/test_internal_imports.py scripts/migration/internal_overlay_manifest.yaml
git commit -m "build: 升级内部依赖到 Python 3.11 --story=${BK_SOPS_MIGRATION_TAPD_STORY}"
```

---

### Task 4: 移植内部环境和对接适配

**Files:**
- Modify: `env.py`
- Modify: `env_ieod.py`
- Modify: `gcloud/conf/sites/ieod/ver_settings.py`
- Create: `gcloud/tests/internal/test_internal_integrations.py`
- Modify: `scripts/migration/internal_overlay_manifest.yaml`

**Interfaces:**
- Consumes: Python 3.11 兼容的内部 SDK。
- Produces: Django 4.2 下的内部认证、客户端、网关地址和功能开关。
- Produces: 租户上下文从请求进入内部 SDK 的契约测试。

- [ ] **Step 1: 写 Django 4 和租户上下文失败测试**

```python
def test_internal_site_settings_use_django4_translation_api():
    source = Path("gcloud/conf/sites/ieod/ver_settings.py").read_text(encoding="utf-8")
    assert "ugettext_lazy" not in source
    assert "gettext_lazy" in source


def test_internal_client_receives_request_tenant(rf, mocker):
    request = rf.get("/")
    request.user = mocker.Mock(tenant_id="default")
    client = get_internal_client_by_request(request)
    assert client.tenant_id == "default"
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `pytest gcloud/tests/internal/test_internal_integrations.py -q`

Expected: FAIL，暴露旧 Django API 或缺失租户传递。

- [ ] **Step 3: 实现目标版本适配**

使用 `django.utils.translation.gettext_lazy`，并让内部客户端显式消费目标版本提供的
租户上下文。不得复制旧任务模型、旧 Celery 消息或 Bridge 路由判断。

- [ ] **Step 4: 运行对接契约测试**

Run: `pytest gcloud/tests/internal/test_internal_integrations.py -q`

Expected: PASS；错误租户或缺失租户时按目标版本统一策略失败，不回退为任意租户。

- [ ] **Step 5: 提交**

```bash
git add env.py env_ieod.py gcloud/conf/sites/ieod/ver_settings.py gcloud/tests/internal/test_internal_integrations.py scripts/migration/internal_overlay_manifest.yaml
git commit -m "feat: 适配多租户内部环境对接 --story=${BK_SOPS_MIGRATION_TAPD_STORY}"
```

---

### Task 5: 分批移植内部插件

**Files:**
- Modify: `pipeline_plugins/components/collections/sites/ieod/`
- Modify: `pipeline_plugins/components/collections/common.py`
- Create: `gcloud/tests/internal/test_internal_components.py`
- Modify: `scripts/migration/internal_overlay_manifest.yaml`

**Interfaces:**
- Consumes: manifest 中 `plugin` 类条目。
- Produces: Python 3.11 下可注册、可序列化和可执行的内部组件集合。
- Produces: 每个组件 code/version 对应的 `ready` 或 `legacy_only` 状态。

- [ ] **Step 1: 写组件清单覆盖失败测试**

```python
def test_every_registered_internal_component_has_manifest_entry():
    registered = discover_internal_component_codes()
    declared = load_manifest_component_codes()
    assert registered <= declared


def test_ready_components_support_target_context():
    for component in ready_internal_components():
        assert_component_contract(component, tenant_id="default")
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `pytest gcloud/tests/internal/test_internal_components.py -q`

Expected: FAIL，列出未登记组件或不兼容目标上下文的组件。

- [ ] **Step 3: 按外部系统域分批移植**

每批只处理同一外部系统目录；修复 Python 3.11 语法、Django 4 API、SDK 调用、字符串/
字节处理和异常序列化。组件 code 和已发布 version 不得改变；无法安全移植的组件标记
`legacy_only`，其使用业务不得进入灰度。

- [ ] **Step 4: 对每批执行契约和沙箱联调**

Run: `pytest gcloud/tests/internal/test_internal_components.py -q`

Run: `pytest pipeline_plugins/tests -q`

Expected: PASS；成功、失败、轮询、撤销和输出序列化路径均有覆盖。

- [ ] **Step 5: 更新 manifest 并按批提交**

```bash
git add pipeline_plugins/components/collections/sites/ieod pipeline_plugins/components/collections/common.py gcloud/tests/internal/test_internal_components.py scripts/migration/internal_overlay_manifest.yaml
git commit -m "feat: 迁移内部插件到 Python 3.11 --story=${BK_SOPS_MIGRATION_TAPD_STORY}"
```

---

### Task 6: 对齐内部页面、模块启动和发布配置

**Files:**
- Modify: `frontend/`
- Modify: `app_desc.yaml`
- Modify: `Procfile`
- Modify: `bin/`
- Create: `scripts/migration/verify_internal_artifact_source.py`
- Create: `gcloud/tests/migration/test_internal_artifact_source.py`

**Interfaces:**
- Consumes: 已移植的目标内部 API 和插件。
- Produces: Web、API Server、Pipeline Worker、Callback、Cleaner、API Inner、Open Plugin 的构建定义。
- Produces: `verify_internal_artifact_source.py --expected-sha SHA METADATA_FILE...`。

- [ ] **Step 1: 写制品来源失败测试**

```python
def test_rejects_mixed_module_source_sha(tmp_path):
    metadata = write_module_metadata(tmp_path, {"default": "aaa", "pipeline-worker": "bbb"})
    assert verify_artifacts(metadata, expected_sha="aaa") == 1
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `pytest gcloud/tests/migration/test_internal_artifact_source.py -q`

Expected: FAIL，提示校验器尚不存在。

- [ ] **Step 3: 迁移模块和启动配置**

以目标分支现有 `app_desc.yaml` 为基线加入内部环境配置，不复制旧版 Celery 4 命令。
所有 Worker 必须使用目标 Celery 5 启动方式和 `/bk_sops_mt`；Web/API/Callback 使用目标
Django 4 配置。每个构建写入相同的 `source_sha` 和 `release_version`。

- [ ] **Step 4: 构建前端并运行后端配置检查**

Run: `npm ci && npm run build`

Run: `python manage.py check --deploy`

Expected: PASS，无缺失内部路由、静态资源或 Django 配置错误。

- [ ] **Step 5: 构建所有模块并校验来源**

Run:
`python scripts/migration/verify_internal_artifact_source.py --expected-sha "$(git rev-parse HEAD)" build-metadata/*.json`

Expected: exit code 0；七类目标模块元数据中的 `source_sha` 完全相同。

- [ ] **Step 6: 提交**

```bash
git add frontend app_desc.yaml Procfile bin scripts/migration/verify_internal_artifact_source.py gcloud/tests/migration/test_internal_artifact_source.py
git commit -m "build: 对齐多租户内部模块发布配置 --story=${BK_SOPS_MIGRATION_TAPD_STORY}"
```

---

### Task 7: 实现业务能力准入检查

**Files:**
- Create: `scripts/migration/check_business_target_capabilities.py`
- Create: `gcloud/tests/migration/test_business_target_capabilities.py`
- Modify: `scripts/migration/internal_overlay_manifest.yaml`

**Interfaces:**
- Consumes: 业务流程模板、周期任务、clocked task 和 manifest 中的能力状态。
- Produces: `check_business_target_capabilities --bk-biz-id BK_BIZ_ID --strict`。
- Produces: JSON 报告字段 `bk_biz_id`、`eligible`、`referenced_capabilities`、`blocked_capabilities`、`target_sha`、`checked_at`。

- [ ] **Step 1: 写存在 legacy-only 插件时拒绝灰度的失败测试**

```python
def test_business_with_legacy_only_component_is_not_eligible(db):
    create_template(bk_biz_id=2, component_code="legacy_internal_component")
    mark_capability("legacy_internal_component", status="legacy_only")
    report = check_business(2, target_sha="abc")
    assert report["eligible"] is False
    assert report["blocked_capabilities"] == ["legacy_internal_component"]
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `pytest gcloud/tests/migration/test_business_target_capabilities.py -q`

Expected: FAIL，提示准入检查尚不存在。

- [ ] **Step 3: 实现业务引用扫描**

扫描业务流程模板、公共流程引用、周期任务和 clocked task，提取组件 code/version、内部
API、回调和调度能力。任一能力缺失、`pending`、`legacy_only` 或证据对应其他目标 SHA
时，`eligible=false`；不得在运行到具体节点时再回退旧引擎。

- [ ] **Step 4: 运行测试并生成首批业务报告**

Run: `pytest gcloud/tests/migration/test_business_target_capabilities.py -q`

Run:
`python scripts/migration/check_business_target_capabilities.py --bk-biz-id "${BK_SOPS_GRAY_BIZ_ID}" --strict --output capability-report.json`

Expected: 测试 PASS；命令仅在全部引用能力 `ready` 时返回 0。

- [ ] **Step 5: 提交**

```bash
git add scripts/migration/check_business_target_capabilities.py gcloud/tests/migration/test_business_target_capabilities.py scripts/migration/internal_overlay_manifest.yaml
git commit -m "feat: 增加业务灰度能力准入检查 --story=${BK_SOPS_MIGRATION_TAPD_STORY}"
```

---

### Task 8: 影子部署并完成工蜂目标版本验收

**Files:**
- Review: `scripts/migration/internal_overlay_manifest.yaml`
- Review: `docs/zh_hans/ops/internal_overlay_py311_matrix.md`
- Review: 工蜂七类模块构建元数据
- Update: `docs/zh_hans/ops/internal_overlay_py311_matrix.md`

**Interfaces:**
- Consumes: Tasks 1-7 的全部交付物。
- Produces: 工蜂多租户目标 SHA 的 Go/No-Go 结论。
- Produces: 主迁移计划 Task 0 的完成证据。

- [ ] **Step 1: 验证清单全部收口**

Run: `python scripts/migration/validate_internal_overlay_manifest.py --fail-on pending,unknown`

Expected: exit code 0；所有 `port/reimplement` 项均为 `ported/reimplemented` 且具有证据。

- [ ] **Step 2: 运行 Python 3.11 完整回归**

Run:
`python -m pytest gcloud/tests/internal gcloud/tests/migration pipeline_plugins/tests gcloud/tests/taskflow3 gcloud/tests/core -q`

Expected: PASS；任何环境缺失必须单独标记为验收阻塞，不能记录为代码通过。

- [ ] **Step 3: 部署无业务流量的目标模块**

从同一工蜂目标 SHA 构建并部署 Web、API Server、Pipeline Worker、Callback、Cleaner、
API Inner 和 Open Plugin；Target 使用新增 `/bk_sops_mt` 和独立 Redis，Bridge 灰度白名单
保持为空。

- [ ] **Step 4: 验证资源隔离和模块健康**

逐模块核对：运行时版本、源 SHA、健康检查、Worker 心跳、队列绑定、Redis 连接、数据库
只读检查和内部 SDK 连通性。确认 Target 没有消费者连接现有 `/bk_sops`。

- [ ] **Step 5: 执行内部测试业务端到端任务**

使用仅供迁移验证的内部业务创建包含内部插件、子流程、周期触发、回调、失败重试和撤销
路径的任务。验证消息只进入 `/bk_sops_mt`，并保存 task_id、trace_id、目标 SHA 和结果。

- [ ] **Step 6: 形成验收结论**

只有满足以下条件才标记 Go：清单无未决项、完整回归通过、七类模块同 SHA、资源隔离通过、
内部测试任务成功、首批业务能力报告 `eligible=true`。否则保持 No-Go，不得开启业务白名单。

---

### Task 9: 固化后续开源同步和工蜂发布流程

**Files:**
- Create: `docs/zh_hans/ops/sync_multi_tenant_to_internal.md`
- Create: `scripts/migration/check_internal_overlay_regression.py`
- Create: `gcloud/tests/migration/test_internal_overlay_regression.py`
- Modify: 工蜂 `dev_multi_tenant` CI 配置

**Interfaces:**
- Consumes: 后续 `upstream/dev_multi_tenant` SHA。
- Produces: `upstream/dev_multi_tenant -> woa/dev_multi_tenant` 的 MR 同步流程。
- Produces: CI 门禁，防止同步后丢失内部能力或重新引入 legacy 依赖。

- [ ] **Step 1: 写回归门禁失败测试**

```python
def test_sync_gate_rejects_removed_ready_capability():
    before = {"internal_component": "ready"}
    after = {}
    assert compare_capabilities(before, after).exit_code == 1
```

- [ ] **Step 2: 实现同步回归检查**

比较同步前后的内部能力清单、组件注册、API 路由、目标依赖和七类模块构建配置。删除
`ready` 能力、重新引入禁用旧依赖或改变组件 code/version 时失败。

- [ ] **Step 3: 编写同步运行手册**

固定步骤为：刷新上游 SHA、创建工蜂同步分支、生成差异报告、解决多租户冲突、执行
内部回归、通过 MR 合入 `woa/dev_multi_tenant`、从合入 SHA 生成各模块制品。禁止把
`woa/V3.6.X` 作为同步来源。

- [ ] **Step 4: 接入工蜂 CI 并验证失败/成功样例**

Run: `pytest gcloud/tests/migration/test_internal_overlay_regression.py -q`

Run: `python scripts/migration/check_internal_overlay_regression.py --base HEAD^ --head HEAD`

Expected: 测试 PASS；故意删除一个 ready 能力时 CI 失败，恢复后 CI 通过。

- [ ] **Step 5: 提交**

```bash
git add docs/zh_hans/ops/sync_multi_tenant_to_internal.md scripts/migration/check_internal_overlay_regression.py gcloud/tests/migration/test_internal_overlay_regression.py
git commit -m "ci: 固化多租户内部集成门禁 --story=${BK_SOPS_MIGRATION_TAPD_STORY}"
```

---

## 依赖顺序

```text
Task 1 内部差异清单
        |
        +------> Task 2 工蜂目标主线
        |              |
        |              v
        +------> Task 3 依赖与运行时
                       |
                       v
                 Task 4 内部对接
                       |
                       v
                 Task 5 内部插件
                       |
                       v
                 Task 6 模块与制品
                       |
                       v
                 Task 7 业务准入
                       |
                       v
                 Task 8 影子验收
                       |
                       v
                 Task 9 持续同步治理
```

Task 1 的清单和 Task 2 的目标主线可以并行准备，但任何内部代码移植都必须同时引用两者。
Task 8 Go 之前，不得开始主迁移计划中的业务灰度；Task 9 可以在首批灰度前完成，也必须
在下一次上游同步前启用。
