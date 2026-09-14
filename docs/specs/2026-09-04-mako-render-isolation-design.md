# Mako 渲染隔离设计（无网无凭证渲染 + 复用池）

> 定位：这是「输入侧收紧」（见 `docs/specs/2026-09-03-mako-enforce-precise-policy-design.md`，
> bamboo-engine PR #284 / bk-sops PR #8505）的后续一层。输入侧解决「降低被打穿的概率」；
> 本文解决「即便被打穿，注入面也拿不到凭证、连不出网络，无法把标准运维当跳板打生态」——
> 即降低爆炸半径（blast radius）。

## 背景与动机

标准运维（bk-sops）允许用户在流程节点里写 Mako 变量表达式（`${...}`），这些表达式会在
服务端被真正执行。等价于「让用户写一小段代码」。我们已经在输入侧做了多层限制（AST 白名单、
危险属性/保留命名空间 always-on 拦截、frame 内省拦截、shield words、受限 builtins、注入模块
deny-list）。

但业界共识很明确——**语言内沙箱不是 RCE 边界，只是缩小可表达能力**：

- Jinja2 官方 `SandboxedEnvironment` 与我们对 Mako 做的事同构（拦属性/调用），但它是「基于
  属性名的 AST 静态检查」，会被 `__class__` → `__subclass__` → `subprocess.Popen` 绕过
  （[RootShell: Escaping Jinja2 Sandbox](https://rootshell.yanivhaliwa.com/study/escaping-jinja2-sandbox-class)）。
  Jinja2 文档自己要求「只传相关数据、别传全局/带副作用对象、用 CPU/内存 limits 跑」
  （[Jinja Sandbox](https://jinja.palletsprojects.com/en/stable/sandbox/)）。
- `RestrictedPython` 也明说「compile 限制本身不足以当沙箱，不是安全边界」
  （[RestrictedPython idea](https://restrictedpython.readthedocs.io/en/latest/idea.html)）。
- 多份 2026 指南统一口径：不可信代码要靠**外部隔离**（进程/内核/硬件），别指望 Python 自沙箱
  （[safeguard.sh](https://safeguard.sh/resources/blog/python-sandbox)、
  [smarttldr](https://smarttldr.com/he/topic/python-sandbox-escape-prevention/core)）。

因此输入侧的 AST 白名单/shield 属于「降概率」层，必须再叠加一层「降影响」的运行时隔离。

## 威胁模型

bk-sops 是编排/自动化平台，本质是「钥匙串」型服务。渲染 Mako 的进程（Django web /
celery worker）当前握着：

| 进程可触达 | 被窃取后果 |
| --- | --- |
| APIGW/ESB `app_secret` | 冒充平台身份调 CMDB / JOB / GSE 全家桶（最致命的横向跳板）|
| DB / Redis / broker 凭证 | 拖走全部流程、模板、用户数据 |
| 内网直连各重要服务 | 横向到生态其他系统 |
| GSE/JOB 下发通道 | 一次 RCE → 成千上万台主机 |

攻击者的目标：从一个「只能算术、拼串」的表达式绕到执行原语，进而**外传窃取的凭证**或
**反弹 shell / C2**，把 bk-sops 当跳板攻击生态里的其他服务。

**核心洞见**：注入发生在「渲染」这一步。如果渲染进程本身**无网络、无凭证**，那么即便渲染面被
完美 RCE，攻击者也拿不到全局密钥、连不出网络，只能搞崩渲染进程自己。

## 关键架构事实（已核实）

> 依据：`bamboo_engine` / `pipeline`（bamboo-pipeline 3.24.x）源码 + bk-sops 调用链核实。

1. **严格的「先求值、后渲染」两阶段**：
   - **hydrate 阶段**（worker/web，有网有凭证）：`Context.hydrate()` 对每个变量调
     `var.get()`；`LazyVariable.get_value()` 在这里才去调 CMDB/ESB/DB（IP 选择器、集群/人员
     选择器等）。
   - **渲染阶段**：`Template.render(hydrated_context)` / `ConstantTemplate.resolve_data()`
     只对**已经求值完的 plain 值**做字符串插值。
2. **唯一执行点**：整条渲染链里真正执行用户表达式的只有一行——`bamboo_engine/template/
   template.py::_render_template` 中的 `tm.render_unicode(**data)`（V1/分析链路对称位置：
   `pipeline/core/data/expression.py::ConstantTemplate.resolve_template`）。
3. **`_system` / `SystemObject`** 只是标量元数据的 `dict` 包装（executor、task_id、bk_biz_id、
   task_url、trace_id 等），**不含 client / 回调 / 网络能力**，可序列化。
4. **渲染合法所需**：能用的模块是 `datetime / re / os.path / json` 这类**纯计算**（白名单早已
   禁网络模块）。**渲染本身不需要网络与凭证**——这正是可以把它整体外移到隔离环境的前提。
5. **两处渲染**：变量渲染同时发生在 Django web（预览）与 celery worker（执行），但都汇聚到上述
   `_render_template` chokepoint。

结论：仅隔离「渲染」这一步，**不会阻断** LazyVariable/CMDB/插件在 hydrate/execute 阶段的
正常网络与凭证访问。

## 目标与非目标

### 目标

1. 让「渲染」这一注入面运行在**无网络、无凭证**的隔离环境，使渲染面 RCE 无法外传凭证 / 连出网络。
2. 对存量业务**语义无破坏**（渲染本就吃已求值的 plain 值）。
3. 复用隔离环境，避免「每次渲染新开进程」的高开销；提供灰度开关与可回退路径。

### 非目标

- 不在本方案里做基础设施层 egress 白名单（见下「为什么不是 egress-only」）。
- 不改变 hydrate（变量求值）阶段的网络/凭证访问——它是预期能力，另受业务权限治理。
- 不追求「进程内重建干净 CPython 解释器」（不可行，见「Python 特有难点」）。
- 不移除输入侧的 AST 白名单/shield——它们作为「降概率」层继续保留。

## 为什么不是 egress-only（否掉「改造①」作为主手段）

egress 白名单必须放行 APIGW/ESB（它前置了整个生态），而被攻陷的 worker 手里握着
`app_secret`，照样能借「网关 + 密钥」摸到全生态 → 对「以 bk-sops 为跳板」的 containment 很弱，
只挡得住最粗糙的「直连攻击者 IP 外传 / 反弹 shell」。而「无网渲染沙箱」已让注入面彻底无网，
使 egress 在「防渲染 RCE 外传」这件事上冗余。真正限制 worker 爆炸半径要靠**网关侧对
`app_secret` 的最小授权 + 轮换**，不是 egress。

## 方案空间：业界隔离方式对比

| 方式 | 机制 | 隔离强度 | 启动 / 复用开销 | 对 Mako 渲染适配 |
| --- | --- | --- | --- | --- |
| 语言内沙箱（Jinja2 Sandbox / RestrictedPython）| 拦 AST | 弱（非边界）| 最快 | 已有等价物，仅「降概率」 |
| **OS 进程级**（subprocess + seccomp + namespaces + rlimits；nsjail/bubblewrap）| 共享内核，限 syscall/网络/权限 | 中（受约束不可信）| 轻；warm 复用后约 5–10ms | ✅ 最契合 |
| gVisor（用户态内核拦 syscall）| 缩小内核攻击面 | 较强（Cloud Run 多租户）| 有非平凡开销，Linux only | 可选加固 |
| 微VM（Firecracker）| 每次执行独立内核 | 最强（硬件级）| 约 125ms 启动，快照 warm resume 到几十 ms | 对本场景偏重 |
| **WASM / Pyodide**（CPython→WASM）| 能力模型 deny-by-default，默认无 fs/网络 | 强（内存安全）| 约 10ms、fresh 实例便宜 | 值得 POC |

（时延数据：[agentpatterns 对比](https://www.agentpatterns.ai/security/sandbox-runtime-comparison/)、
[blaxel](https://blaxel.ai/blog/python-sandbox-llm-untrusted-code-isolation)。）

**判断**：bk-sops 渲染是**极受限的计算**（模板串插值 + 少量纯计算模块），不是通用 Python，
威胁不需要每次微VM。OS 进程级（seccomp + 无网 + 无凭证）足够；WASM 因「fresh 实例便宜、
deny-by-default」在受限子集上很契合，作为并行探索。

## 推荐方案

### 切点（seam）

只改一处：把 `_render_template` 里「`MakoTemplate(template)` 编译 + `harden_template_builtins`
+ `render_unicode(**data)`」这段，从进程内调用改为**发给隔离渲染器**，返回字符串。

| 留在主进程（不动） | 移入隔离渲染器 |
| --- | --- |
| hydrate（变量求值，有网有凭证）| `MakoTemplate(template)` 编译 |
| `_render_string` 的 AST 检查 / 白名单（便宜、不执行用户码）| `harden_template_builtins` |
| 组装 `data`（沙箱 dict + context）| **`render_unicode(**data)`** ← 关键 |

- 传入隔离器：`(template_string, data)`。`data` = 沙箱 dict（`datetime/re/os.path/json`，可在隔离器
  本地重建）+ 序列化进来的 hydrated context。
- 覆盖两套实现：`bamboo_engine/template/template.py::_render_template` 与
  `pipeline/core/data/expression.py::ConstantTemplate.resolve_template`。只要在这两处切，
  `service_activity` / `empty_start_event`(pre_render) / web 预览等调用方**全部自动走隔离器**，
  无需逐个改。

### 可插拔 render backend

这两个入口都在 **bamboo-engine（依赖包）**，因此本改造本质是改 bamboo-engine（与 PR #284 同包）。
形态：引擎暴露一个可配置的 **render backend**——默认「进程内渲染」保持现状；bk-sops 配置成
「sandbox backend（进程池 / WASM）」。引擎侧只加 hook，bk-sops 侧只加配置，支持灰度与回退。

```
RenderBackend 接口（示意）
  render(template: str, data: dict) -> str        # 无网无凭证环境执行 render_unicode
  # 失败/不可序列化 → 抛特定异常，主进程按现状 inert 回显或降级
```

### 隔离器落地（首选：OS 进程池）

- **常驻 warm 进程池（prefork）**，不是每次 fork。
- 每个 worker：无 network namespace、无 DB/ESB/Redis 凭证（env 清洗）、seccomp 禁
  `execve/socket`、只读根 FS、非 root、CPU/内存/超时 rlimits。
- 复用策略见下节。

## 子进程复用设计（回应「每次新开开销大」）

业界主流对「任务级、低时延、频繁」的不可信执行 = **warm 池复用 + 每次执行拿到 pristine 上下文
+ 用后回收**，而非每次新建：

- forge-sandbox：warm 池复用，每次 `execute` 发 `Reset` 让 worker 丢弃并重建运行时（约 5–10ms，
  对比新开约 50ms）；安全不变量「每次执行都是全新上下文，无状态泄漏」；worker 跑够 `max_uses`
  次后回收（[pool.rs](https://docs.rs/forge-sandbox/latest/src/forge_sandbox/pool.rs.html)）。
- vurb/vinkius：Isolate 复用，每次 `execute` 新建 pristine Context，OOM/超时则 dispose 重建
  （[SandboxEngine](https://vurb.vinkius.com/sandbox)）。
- k8s agent-sandbox：`reset-and-reuse` + 分级 warm 填充
  （[PR #1232](https://github.com/kubernetes-sigs/agent-sandbox/pull/1232)）。

### 复用的安全不变量（必须满足）

复用进程跑不可信代码的核心风险是**跨执行状态泄漏**（上次渲染在解释器里留下的全局污染 / 残留
数据被下次读到）。缓解（组合使用）：

1. **每次渲染前 reset 到 pristine 命名空间**（丢弃并重建渲染局部作用域）；
2. **用后回收**（`max_uses` / recycle-after-N）；
3. 因隔离器**无网无凭证**，跨执行泄漏顶多是「别的任务的 context 值」——若要强隔离，按
   **业务/租户分池** 或 **用后即弃**。

### Python 特有难点

CPython **没有** V8 Isolate 那种「廉价重建干净上下文」的能力（`sys.modules` 缓存、导入副作用让
进程内 reset 到真·pristine 很难）。所以 Python 侧复用通常是 **prefork 进程池 + 每进程处理
1 次 / N 次后 recycle**（类似 gunicorn/celery worker recycle），而非「进程内重建干净解释器」。
这恰是 **WASM/Pyodide 的优势**：WASM 实例每次可廉价 fresh，天然规避状态泄漏且 deny-by-default，
值得作为第二条技术路线 POC。

## 存量兼容影响

- **功能语义**：基本无破坏。渲染只吃已求值的 plain 值；LazyVariable/CMDB/插件都在
  hydrate/execute，不在渲染面。
- **context 序列化长尾（主要工程风险）**：传入渲染的 context 含 `SystemObject`（纯 dict ✅）、
  `SetGroupInfo`、CMDB 返回的 dict/list 等。跨进程需可序列化；若某自定义变量对象携带不可 pickle
  的活状态（client/句柄/lambda），会失败 → 需盘点 + 兜底（降级为主进程渲染或报错留痕）。
- **性能/时延**：渲染按节点高频发生、web 预览时延敏感 → 必须进程池化，别每次 fork；评估 IPC +
  序列化开销与并发度。
- **一致性**：web 与 worker 两侧都要经隔离器，行为一致。
- **pre_render_mako**：启动时的一次完整 hydrate 仍留在 worker（有网有凭证），只把 Mako 字符串
  插值移入隔离器。

## POC 计划（分阶段，先验证再落地）

1. **阶段 0：context 可序列化盘点** ✅ 已完成，见下「阶段 0 结论」。
   - 扫描渲染入口实际传入的 context 对象类型（`SystemObject` / `SetGroupInfo` / CMDB dict / 自定义
     变量返回值），统计不可 pickle 的比例与来源。产出「可序列化性清单 + 兜底策略」。
   - 核心结论：19 个自定义变量中 13 个纯 plain 可直接移植；6 个 rich/unknown 的类模块依赖 Django、
     无法在最小 worker unpickle；「静默回退进程内」可被模板作者用 rich 变量绕过 → 默认策略需收敛。
2. **阶段 1：进程池隔离器 POC（首选路线）**
   - 在 bamboo-engine 加 `RenderBackend` hook；实现 `SubprocessPoolBackend`：prefork warm 池 +
     无网/无凭证/seccomp/rlimits + `max_uses` 回收 + 每次 pristine。
   - 基准：单节点渲染时延、批量渲染吞吐、web 预览 P95、序列化失败率。对比进程内基线。
3. **阶段 2：Pyodide/WASM 可行性 POC（并行探索）**
   - 验证 Mako（纯 Python）+ `datetime/re/json` 在 Pyodide 下能否渲染、时延与内存、C 扩展限制。
   - 若可行，对比进程池在隔离性/复用开销上的优劣。
4. **阶段 3：灰度落地**
   - bk-sops 通过配置切 backend；先影子比对（隔离器与进程内结果一致性），再灰度 worker，再灰度
     web 预览；保留一键回退到进程内。

## 实现状态（bamboo-engine 侧已落地，默认不改变行为）

> 代码在 bamboo-engine worktree `feat/mako-render-isolation`（PR #284 同线）。默认
> `MAKO_RENDER_BACKEND="inprocess"`，即**行为与现状完全一致**；切到 `"subprocess"` 才启用隔离。

**已实现（Phase 1a + 1b）**

1. **可插拔 render backend**（`bamboo_engine/template/render_backend.py`）：
   - 唯一“执行用户表达式”实现下沉为共享函数 `_render_with_sandbox`（进程内与隔离 worker 复用同一
     份逻辑，保证语义严格一致：编译/渲染失败一律 inert）。
   - `RenderBackend` 接口 + `InProcessRenderBackend`（默认，零行为变化）+ 注册表
     （`get/set/reset_render_backend`）。
   - 两个 seam 均已改走 backend：`Template._render_template`（新引擎）与
     `ConstantTemplate.resolve_template`（legacy pipeline）。调用方（service_activity / pre_render /
     web 预览）全部自动生效，无需逐个改。
2. **可序列化沙箱**：`SandboxSpec`（flavor + shield_words + import_modules，纯字符串可 pickle）+
   `SandboxProvider`（打包「进程内构造」与「spec」）。worker 只序列化 context，沙箱在子进程本地
   按 spec 重建（`datetime/re/json` 等模块不跨进程序列化）。
3. **legacy 沙箱 Django 解耦**：新增 Django-free `pipeline/core/data/sandbox_builder.py`
   （mock builtins + shield + 注入模块），使**精简 spawn worker 无需 import Django / 业务 app /
   凭证**即可重建 legacy 沙箱；`pipeline/core/data/sandbox.py` 委托它构造并保留全部向后兼容符号。
4. **`SubprocessPoolRenderBackend`**（无网无凭证隔离池）：
   - `spawn` 全新解释器 worker（不继承父进程内存、不 import Django）；warm 池复用，`max_uses` 用后
     回收，每次渲染以全新沙箱重建（pristine），杜绝跨执行状态泄漏。
   - **无凭证**：worker 启动即从 `os.environ` 清洗凭证类 env（`SECRET/PASSWORD/TOKEN/APP_SECRET/
     DB/REDIS/BROKER/...` 子串匹配，可经 `MAKO_RENDER_ENV_SCRUB_EXTRA` 追加）。
   - **无网 + 资源上限**（Linux 生效，macOS 等 no-op）：禁 core dump、CPU/内存 rlimits、尽力
     `unshare(CLONE_NEWNET)`（无权限则降级，凭证已清洗）。
   - **context 归一化**：发送前把 rich「属性包」对象搬运成 Django-free 的 `PortableRenderObject`，让含 rich
     内置变量的模板也能进隔离渲染（否则其类模块依赖 Django、无法在最小 worker unpickle）。见阶段 0 结论。
   - **fail-safe 兜底（默认 strict）**：残余不可序列化 context / worker 异常 → 默认 inert 回显（不静默回退
     特权进程；可切 `fallback_inprocess=True` 灰度保可用）；渲染超时 → 一律 inert（**绝不**回退，避免把 DoS
     带回主进程）；worker 侧 unpickle 失败 → 立即 `STATUS_ERR` 走统一兜底（不再拖满 timeout）。
   - 懒启动（首次 render 才拉池，避免 import 期 fork）；`atexit` 清理。

**启用方式（bk-sops 配置，灰度可回退）**

在 `config/default.py` 既有 `BambooSettings.MAKO_SANDBOX_IMPORT_MODULES = ...` 附近追加（默认
`inprocess`，灰度时按环境变量切 `subprocess`）：

```python
from bamboo_engine.config import Settings as BambooSettings

BambooSettings.MAKO_RENDER_BACKEND = os.getenv("BKAPP_MAKO_RENDER_BACKEND", "inprocess")  # inprocess | subprocess
BambooSettings.MAKO_RENDER_POOL_SIZE = int(os.getenv("BKAPP_MAKO_RENDER_POOL_SIZE", "4"))
BambooSettings.MAKO_RENDER_MAX_USES = int(os.getenv("BKAPP_MAKO_RENDER_MAX_USES", "500"))
BambooSettings.MAKO_RENDER_TIMEOUT = float(os.getenv("BKAPP_MAKO_RENDER_TIMEOUT", "30"))
```

引擎侧全部通过 `getattr(Settings, ..., <default>)` 读取，**未配置也安全**。可选进阶开关：
`MAKO_RENDER_FALLBACK_INPROCESS`（默认 **False = strict**；置 True 则残余不可序列化时回退进程内，灰度保可用用）、
`MAKO_RENDER_ENV_SCRUB_EXTRA`（list）、`MAKO_RENDER_OS_HARDEN`（默认 True）、
`MAKO_RENDER_NO_NETWORK`（默认 True）、`MAKO_RENDER_RLIMIT_CPU`（默认 30s）、
`MAKO_RENDER_RLIMIT_AS_MB`（默认 1024）。

**测试证据**：引擎 `tests/template/` 138 passed / 1 skipped（含隔离池 8 项：跨进程 PID 隔离、warm 复用、
`max_uses` 回收、env-scrub、超时 inert、不可序列化回退、无 spec 走进程内、编译错误 inert；OS 加固 6 项）；
legacy `test_expression/test_sandbox/test_sandbox_builder` 62 passed。端到端两 seam（engine + legacy）
在 `subprocess` 下渲染正确，且 legacy mock builtin `${int}→"int"` 证明 Django-free 沙箱已在 worker 内重建。

**未落地（后续阶段）**：阶段 2 Pyodide/WASM 并行 POC；seccomp（需 `pyseccomp`，非默认依赖）；按业务/租户分池；
生产快照采样量化受影响模板占比（见阶段 0 结论第 4 条）。

## 阶段 0 结论：context 可序列化盘点（已完成）

> 这是子进程路线的**风险门禁**。核对了两个渲染入口的 context 组成、全部自定义变量的 `get_value` 返回类型，
> 并对隔离后端做了实测。**它直接改写了默认兜底策略的正确性判断。**

### context 值的三类来源

渲染 context 的 value 只来自：① plain 常量（str/int/list/dict…，可 pickle）；② `SystemObject`——
`engine_pickle_obj/context.py` 里 `self.__dict__ = attrs` 的标量 dict 包装（executor/task_id/biz_cc_id…，
可 pickle）；③ `LazyVariable.get_value()` 的返回——**这是唯一由自定义代码决定、也是唯一有序列化风险的面**。

### 盘点结果（19 个自定义变量，全部在 `pipeline_plugins/variables/collections/`）

| 分桶 | 数量 | 说明 / 代表 |
| --- | ---: | --- |
| PLAIN（str/数值/None） | 11 | password / select / *time 系列 / staff_group_selector / ip / ip_selector / ip_filter / set_module_ip_selector |
| CONTAINER_OF_PLAIN（plain 的 list/dict） | 2 | text_value_select、attribute_query |
| **RICH_OBJECT（自定义类实例）** | **5** | datatable(`DataTableValue`)、set_allocation(`SetDetailData`)、set_group_selector(`SetGroupInfo`)、set_filter_selector(`SetInfo`)、set_module_selector(`SetModuleInfo`) |
| UNKNOWN | 1 | bk_user_selector（`return self.value` 透传，类型取决于前端） |

13/19 是纯 plain（含 SystemObject），**可原样搬进最小 worker**。风险集中在 5 个 rich wrapper + 1 个 unknown。

### 关键洞见：难点不是「能不能 pickle」，而是「worker 能不能 unpickle」

- 5 个 rich wrapper 实例**只含 plain data**（动态 `setattr` 的列 list + `flat__x` 字符串 + repr 串），无 client /
  句柄 / lambda。所以**父进程 `pickle.dumps` 成功**——平台本就 pickle 存储 context（`engine_pickle_obj`），
  picklability 是既有不变量。
- 但这些类**定义所在模块 import 即依赖 Django**：`from django.conf import settings`、`ugettext_lazy`，且
  在**类体执行期**就读 `settings.STATIC_URL`（`datatable.py` 等 5 个文件均已核实）。因此**无 Django 的
  「无凭证最小 worker」`pickle.loads` 会在类模块 import 阶段失败**——engine flavor 的最小 worker 无法重建这 6 类对象。

### 两种失败模式（实测；均已被正确处理）

1. **父进程侧 pickle 失败**（真正不可序列化对象）→ 干净回退进程内。（已有测试）
2. **worker 侧 unpickle 失败**（可 pickle 但类不可 import = 上述 6 类的真实模式）→ **本轮修复前**：worker 静默
   `continue` 不回包 → 父进程等满 timeout（默认 30s）再 inert 回显模板 = **datatable/cmdb 模板破图 + 30s 延迟**。
   已通过实测复现（`test_subprocess_worker_side_unpickle_failure_falls_back_fast`），并**修复**为 worker 立即回
   `STATUS_ERR` → 父进程走统一快速兜底。

### 攻击者可控性判定（安全门禁问题的答案）

- 模板注入攻击者**无法**新增 `LazyVariable` 子类（那需要往 bk-sops 推代码，本身已是发布/RCE 权限，超出模板注入模型）。
- 但**模板作者**（与注入 `${...}` 同一威胁行为体）只要在流程里放一个 rich 内置变量（如 `set_group_selector`），
  其 context 就含**无法在 worker 重建**的对象 → 触发回退。若回退默认是「静默回进程内」，其 `${...}` 注入就会
  在**有网有凭证的主进程**里执行。
- **结论**：`fallback_inprocess=True` 静默默认，对「模板作者即攻击者」这个我们真正关心的模型是**可绕过的**。
  回退策略必须是有意识的选择，而不是默认静默回特权进程。

### 建议与落地（据此收敛 Phase 1b 的默认策略）

1. **[已做]** 修复 worker 侧 unpickle 失败处理：立即回 `STATUS_ERR`，把 30s-timeout-inert 变成快速统一兜底。
2. **[已做] context 归一化**：`SubprocessPoolRenderBackend.render` 在 pickle 前调 `_portable_context`，把 rich
   「属性包」对象忠实搬运成 Django-free 的 `PortableRenderObject`（保留 `__dict__` 属性 + 捕获的 `str/repr`），
   使全部 19 个变量都能在最小 worker 渲染。已核实 5 个 wrapper 均为纯属性包（eager `setattr` + 仅 `__repr__`，
   无方法 / `__getattr__` / `__getitem__` / property），模板用法只是属性访问 + 列表下标 + bare `${var}`，故忠实
   搬运即可。归一化只作用于隔离发送路径；进程内渲染仍见原对象、行为零变化。可调用 / 类型 / 模块按引用保留
   （不破坏 `${f()}`），标量与容器递归处理。
   - 证据：`test_subprocess_backend_normalizes_rich_object_to_render_in_worker`、
     `test_portable_context_preserves_plain_and_callables_normalizes_rich`、`test_portable_render_object_roundtrips_via_pickle`；
     端到端在 `subprocess`+strict 下，一个 `__setstate__` 抛错的 rich 对象仍渲染出 `${v.flat__ip}` / `${v.hosts[1]}` /
     bare `${v}`——证明 worker 只见归一化载体、从不 unpickle 原类。
3. **[已做] 默认切 strict**：归一化后合法 context（含 rich 变量）已可进隔离渲染，故默认 `fallback_inprocess=False`
   ——残余「不可序列化」多属异常/攻击者构造，此时 inert 回显而**不**静默回退特权进程，堵掉「加个 rich 变量 /
   塞个不可序列化对象把注入拽回主进程」的绕过。灰度保可用可显式 `fallback_inprocess=True` /
   `MAKO_RENDER_FALLBACK_INPROCESS=True`。
4. **生产采样（后续）**：从 pipeline 实例快照抽样真实 hydrated context，实测「归一化后仍不可 pickle」的残余占比，
   验证 strict 默认在现网的可用性，定灰度顺序。

## 风险与开放问题

- 序列化不可行的自定义变量对象比例是否可接受？兜底降级会不会削弱隔离承诺？
- 进程池在高并发流程（大流程数百节点）下的资源占用与调度。
- Pyodide 对 Mako 全部语法 + 现有导入模块的兼容度未知，需 POC 验证。
- 复用池的「按业务/租户分池」粒度与运维复杂度权衡。
- 隔离器内仍能看到「本次任务」的 hydrated context（用户可能填敏感值）——非零残余，需在文档中明确
  说明其边界（看不到别的任务 / 全局 secret / 网络）。

## 参考资料

- Jinja2 Sandbox（官方）：<https://jinja.palletsprojects.com/en/stable/sandbox/>
- Escaping Jinja2 Sandbox（RootShell）：<https://rootshell.yanivhaliwa.com/study/escaping-jinja2-sandbox-class>
- RestrictedPython idea：<https://restrictedpython.readthedocs.io/en/latest/idea.html>
- Python Sandbox 最佳实践（safeguard.sh）：<https://safeguard.sh/resources/blog/python-sandbox>
- 隔离方式对比（agentpatterns）：<https://www.agentpatterns.ai/security/sandbox-runtime-comparison/>
- LLM 不可信代码隔离（blaxel）：<https://blaxel.ai/blog/python-sandbox-llm-untrusted-code-isolation>
- warm 池复用（forge-sandbox pool.rs）：<https://docs.rs/forge-sandbox/latest/src/forge_sandbox/pool.rs.html>
- Zero-Trust V8 Isolate（vurb）：<https://vurb.vinkius.com/sandbox>
- reset-and-reuse（k8s agent-sandbox PR #1232）：<https://github.com/kubernetes-sigs/agent-sandbox/pull/1232>
