# AI 平台调用埋点设计

## 背景

标准运维后续会在 OpenClaw 上构建 Skill 集，用于操作标准运维（构建流程、执行任务、查询状态等）。Skill 通过蓝鲸 API 网关直接调用 SOPS API，使用用户自己的 app_code。

当前问题：

- 无法识别一次 API 调用是否来自 AI 平台（如 OpenClaw），因为 app_code 是用户自己的
- 无法统计有多少用户通过 AI 平台使用 SOPS
- 无法分析 AI 触发的任务成功率和业务分布

## 目标

设计一套埋点机制，满足以下核心指标的统计需求：

1. **调用次数**：哪些 API 被 AI 平台调用，调用频率
2. **用户数**：有多少用户通过 AI 平台使用 SOPS
3. **成功率**：AI 触发的任务执行成功率
4. **业务分布**：哪些业务使用 AI 平台最多

## 设计约束

- OpenClaw Skill 通过**蓝鲸 API 网关**调用 SOPS API
- 使用**用户自己的 app_code**，无法通过 app_code 区分来源
- 不修改当前 Cursor 环境的 Skill 文件，而是产出 Skill 编写规范
- 数据记录复用现有 OTel trace 体系，不新建 DB 模型

## 方案：自定义 HTTP Header 注入

### 整体思路

Skill 在调用 SOPS API 时携带约定的 HTTP Header 标识来源。SOPS 后端检测 Header，将来源信息注入到 OTel Span 属性中，复用现有 trace 体系进行数据采集和查询。

### 数据流

```
OpenClaw Skill
    │
    │  HTTP Request + Headers:
    │    X-Bkapi-Ai-Platform: openclaw
    │    X-Bkapi-Ai-Skill: sops-task-execution
    │
    ▼
蓝鲸 API 网关（透传 Header）
    │
    ▼
SOPS 后端 (apigw views)
    │
    ├─ mark_ai_platform 装饰器
    │    → request.ai_platform = "openclaw"
    │    → request.ai_skill = "sops-task-execution"
    │
    ├─ trace_view 装饰器
    │    → span.set_attribute("bk_sops.ai_platform", "openclaw")
    │    → span.set_attribute("bk_sops.ai_skill", "sops-task-execution")
    │    → span.set_attribute("bk_sops.ai_username", username)
    │    → 导出到 OTel 后端
    │
    └─ create_task 视图（写操作）
         → create_method = "openclaw"
         → 写入 TaskFlowInstance + TaskflowStatistics
```

## 详细设计

### 1. Header 协议

遵循现有 `HTTP_X_BKAPI_MCP_SERVER_ID` 命名模式（`X-Bkapi-` 前缀是蓝鲸 API 网关约定）：

| Header | 用途 | 值示例 | 必传 |
|---|---|---|---|
| `X-Bkapi-Ai-Platform` | AI 平台标识 | `openclaw` | 是 |
| `X-Bkapi-Ai-Skill` | 技能名称 | `sops-task-execution` | 否 |

设计要点：

- `X-Bkapi-Ai-Platform` 是核心标识。后续其他 AI 平台接入只需传不同的值
- `X-Bkapi-Ai-Skill` 用于细粒度统计
- 不引入 session_id 等复杂字段，保持 YAGNI
- 与现有 MCP 检测（`is_mcp_request`）互不干扰，两者是独立维度

### 2. 后端检测

#### 2.1 检测函数

在 `gcloud/apigw/decorators.py` 中新增：

```python
def is_ai_platform_request(request):
    """检测请求是否来自 AI 平台，返回平台标识字符串，空字符串表示非 AI 请求"""
    header_key = getattr(settings, "APIGW_AI_PLATFORM_HEADER", "HTTP_X_BKAPI_AI_PLATFORM")
    ai_platform = request.META.get(header_key, "").strip()
    return ai_platform if ai_platform else ""
```

#### 2.2 装饰器

```python
def mark_ai_platform(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        request.ai_platform = is_ai_platform_request(request)
        request.ai_skill = request.META.get(
            getattr(settings, "APIGW_AI_SKILL_HEADER", "HTTP_X_BKAPI_AI_SKILL"), ""
        ).strip()
        return view_func(request, *args, **kwargs)
    return wrapper
```

应用到所有 apigw view 的装饰器链，放在 `mark_request_whether_is_trust` 附近。

### 3. OTel Span 属性注入

扩展 `trace_view` 装饰器（`gcloud/core/trace.py`），在构造 attributes 时自动从 request 读取 AI 来源信息：

```python
# trace_view 内部 _wrapped_view 中，构造 attributes 之后：
if hasattr(request, "ai_platform") and request.ai_platform:
    attributes["ai_platform"] = request.ai_platform
    attributes["ai_skill"] = getattr(request, "ai_skill", "")
    attributes["ai_username"] = request.user.username
    attributes["ai_app_code"] = getattr(
        request.app, settings.APIGW_MANAGER_APP_CODE_KEY, ""
    )
```

生成的 span 属性名为 `bk_sops.ai_platform`、`bk_sops.ai_skill` 等（`start_trace` 自动加 `{APP_CODE}.` 前缀）。

查询类 API 当前缺少 `trace_view`，后续逐步补充以覆盖全部 API 的 trace 能力。

### 4. create_method 扩展

在 `gcloud/constants.py` 的 `TaskCreateMethod` 枚举中新增：

```python
class TaskCreateMethod(Enum):
    APP = "app"
    API = "api"
    APP_MAKER = "app_maker"
    PERIODIC = "periodic"
    CLOCKED = "clocked"
    MOBILE = "mobile"
    MCP = "mcp"
    OPENCLAW = "openclaw"  # 新增
```

`TASK_CREATE_METHOD` 列表同步新增 `(TaskCreateMethod.OPENCLAW.value, _("OpenClaw"))`。

`create_task` 视图中判断优先级调整为：`ai_platform` > `is_mcp_request` > `API`。

### 5. Settings 配置

在 `config/default.py` 中新增：

```python
APIGW_AI_PLATFORM_HEADER = "HTTP_X_BKAPI_AI_PLATFORM"
APIGW_AI_SKILL_HEADER = "HTTP_X_BKAPI_AI_SKILL"
```

### 6. Skill 编写规范

产出 `docs/specs/openclaw-sops-skill-convention.md`，其中包含 AI 来源标识条款：

> **[必须] AI 来源 Header**
>
> 所有 OpenClaw Skill 在调用 SOPS API 时，必须在 HTTP 请求头中携带以下 Header：
>
> | Header | 值 | 必传 | 说明 |
> |---|---|---|---|
> | `X-Bkapi-Ai-Platform` | `openclaw` | 是 | 固定值，标识请求来自 OpenClaw |
> | `X-Bkapi-Ai-Skill` | skill 名称 | 是 | 当前 skill 的标识 |

## 指标查询方式

| 指标 | 查询方式 |
|---|---|
| 调用次数 | OTel 后端过滤 `bk_sops.ai_platform = openclaw` 的 span 数量，按 span name 分组 |
| 用户数 | 同上，按 `bk_sops.ai_username` 去重计数 |
| 成功率 | `TaskflowStatistics` 中 `create_method = openclaw` 的任务，关联完成状态 |
| 业务分布 | OTel 后端过滤同上，按 `bk_sops.project_id` 分组 |

## 变更清单

| 序号 | 变更位置 | 改动内容 | 影响面 |
|---|---|---|---|
| 1 | `gcloud/apigw/decorators.py` | 新增 `is_ai_platform_request()` 和 `mark_ai_platform` 装饰器 | 新增代码，无侵入 |
| 2 | `gcloud/core/trace.py` | 扩展 `trace_view`，自动读取 AI 来源属性写入 span | 仅追加属性，现有 span 不受影响 |
| 3 | `gcloud/constants.py` | `TaskCreateMethod` 新增 `OPENCLAW`；`TASK_CREATE_METHOD` 新增对应项 | 枚举扩展 |
| 4 | `gcloud/apigw/views/create_task.py` | `create_method` 判断优先级调整 | 仅改判断顺序 |
| 5 | 各 apigw view 文件 | 装饰器链添加 `@mark_ai_platform`；查询 API 补充 `@trace_view` | 可分批推进 |
| 6 | `config/default.py` | 新增 Header 配置项 | 新增配置，有默认值 |
| 7 | `docs/specs/openclaw-sops-skill-convention.md` | 新建 Skill 编写规范 | 纯文档 |

## 不涉及的改动

- 不新建 DB 模型，不需要 migration
- 不修改当前 Cursor Skill 文件
- 不修改 API 网关配置
- 不新增 Celery 任务

## 分阶段交付

- **Phase 1（最小可用）**：变更 1 + 3 + 4 + 6 + 7 — 后端识别 + create_method 扩展 + 规范文档
- **Phase 2（trace 覆盖）**：变更 2 + 5 — OTel span 属性注入 + 查询 API 补充 trace_view
