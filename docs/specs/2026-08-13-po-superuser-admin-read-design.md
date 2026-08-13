# PO 超级管理员全局只读可见权限设计

- TAPD：[137115625](https://tapd.woa.com/10131351/prong/stories/view/137115625)
- 适用仓库：`bk-sops`、`bk-sops-facade`（PO）

## 1. 背景

PO 当前使用登录用户身份调用 bk-sops API：

- 业务列表由 bk-sops 的 `get_user_project_list` 按用户的 `project_view` 权限过滤；
- 业务详情由 bk-sops 的 `get_user_project_detail` 先校验 `project_view`，再以当前用户身份查询 CMDB 业务详情；
- PO 本地多数读取接口调用 `has_business_view_permission`，写接口中也复用了这个判断；
- PO 的 Django `is_superuser` 目前只代表应用本地超级管理员，不会自动获得 bk-sops IAM 或 CMDB 业务权限。

因此，开发者中心管理员即使能够进入 WebConsole 并被设置为 PO 的 `is_superuser`，仍然无法稳定查看全部业务、流程和 PO 任务。

bk-sops 内部版处理跨业务管理场景时，没有给管理员伪造每个业务的 `project_view` / `project_edit`，而是提供由 `admin_view` / `admin_edit` 保护的独立管理通道。PO 参考这一模式，增加独立的超级管理员只读通道。

## 2. 目标与非目标

### 2.1 目标

当且仅当 PO 登录用户满足 `request.user.is_superuser is True` 时，允许其：

1. 查看 bk-sops 中所有未停用业务；
2. 查看这些业务下的流程模板、流程详情、执行方案和流程预览；
3. 查看 PO 中全部任务记录，以及对应的 bk-sops 任务详情、状态、流程树、节点详情和节点日志；
4. 查看 PO 业务配置和流程接入配置；
5. 在没有 CMDB 业务权限时仍能打开业务；
6. 保留管理员本人真实拥有的 IAM 权限，不伪造资源权限；
7. 通过独立日志识别管理员只读访问。

### 2.2 非目标

本期不因 `is_superuser` 放开以下能力：

- 新增、修改业务配置；
- 接入、修改或删除流程；
- 创建 PO 任务记录或 bk-sops 任务；
- 启动、暂停、撤销任务；
- 重试、跳过、强制失败等节点操作；
- PO 对外 APIGW 创建任务；
- 查看不在现有接口响应范围内的密钥、敏感配置或未脱敏数据；
- 将 bk-sops 中绕过 PO 创建的全部任务同步到 PO 任务列表；
- 批量授予或同步 bk-sops IAM、CMDB 权限。

## 3. 设计原则

1. **只读旁路与真实权限分离**：管理员只读能力不得写入或伪造成 `auth_actions`。
2. **普通链路不变**：非超级管理员继续使用现有 bk-sops IAM 和 CMDB 权限链路。
3. **写接口不复用放大的判断**：不能直接把现有 `has_business_view_permission` 改成超级管理员恒为 `True`，因为创建和操作接口也在使用它。
4. **调用方与接口双白名单**：只有指定 PO App Code 调用指定只读接口时，bk-sops 才接受管理员只读声明。
5. **后端为唯一信任源**：浏览器不能声明自己是超级管理员；PO 后端必须丢弃外部同名请求头并重新生成。
6. **失败关闭**：管理员只读配置异常时拒绝旁路，不降级为业务代理人或全局可信应用调用。
7. **可快速回滚**：通过功能开关和独立 App Code 白名单关闭，不需要回写 IAM 或 CMDB。

## 4. 总体架构

管理员访问的身份链保持为原始登录用户，PO 只额外声明本次调用是经过本地 `is_superuser` 校验的只读调用。

```text
Browser
  -> PO session authentication
  -> request.user.is_superuser
       false -> existing IAM/CMDB path
       true  -> PO admin-read path
                  -> strip client supplied admin-read headers
                  -> attach server generated admin-read marker
                  -> call bk-sops with original username
                       -> verify caller App Code
                       -> verify endpoint is read-only allowlisted
                       -> bypass only ProjectView/FlowView/TaskView/FunctionView
                       -> query data without granting write actions
```

本方案不把 PO 加入 bk-sops 的全局 `APP_WHITELIST`。全局可信应用会影响多类读写接口，不满足最小权限原则。

## 5. 管理员识别与配置

### 5.1 权威来源

PO 只认数据库用户模型上的：

```python
request.user.is_superuser is True
```

开发者中心拥有应用权限不等于 PO 运行时自动得到 `is_superuser=True`。管理员应先登录一次以创建本地用户记录，再通过 WebConsole 对准确用户名设置该字段。

### 5.2 WebConsole 配置与复核

配置前只读检查：

```python
from django.contrib.auth import get_user_model

User = get_user_model()
raw_usernames = input("请输入管理员用户名，多个用英文逗号分隔：")
usernames = [name.strip() for name in raw_usernames.split(",") if name.strip()]
assert usernames, "管理员用户名不能为空"

list(
    User.objects.filter(username__in=usernames).values(
        "username", "is_active", "is_staff", "is_superuser"
    )
)
```

确认用户名和记录数量后设置：

```python
updated = User.objects.filter(username__in=usernames).update(
    is_active=True,
    is_staff=True,
    is_superuser=True,
)
print({"expected": len(usernames), "updated": updated})
```

设置后使用相同的只读查询再次复核。若记录不存在，应让用户先登录，不在 WebConsole 中直接创建未知用户名。

## 6. PO 权限模型

### 6.1 后端能力拆分

保留现有函数的真实权限语义：

```text
has_business_view_permission(username, bk_biz_id)
    = 用户真实拥有 bk-sops project_view

has_business_edit_permission(username, bk_biz_id)
    = 用户真实拥有 bk-sops project_edit
```

新增面向请求对象的只读判断：

```text
can_read_business(request, bk_biz_id)
    = 功能开关开启且 request.user.is_superuser
      或用户真实拥有 project_view
```

同时提供调用模式判断，避免各 view 自行拼装条件：

```text
get_business_read_mode(request, bk_biz_id)
    -> "admin_read" | "iam"
```

### 6.2 只读入口

以下 PO 入口允许使用 `can_read_business`：

- `GET get_user_businesses`；
- `GET get_project_detail`；
- `GET get_user_templates`；
- `GET get_template_schemes`；
- `GET get_templates_info`；
- 语义只读的 `POST preview_task_tree`；
- `GET get_scheme_data`；
- `GET business_config`；
- `GET expose_template`；
- `GET task_create_record`；
- `GET get_pipeline_tree`；
- `GET get_task_bill_status`；
- `GET get_task_detail`；
- `GET get_task_status`；
- `GET get_functionalization_task_status`；
- `GET get_task_node_data`；
- `GET get_task_node_detail`；
- 新增 `GET get_task_node_log`。

其中 PO 本地读取不需要调用 bk-sops；涉及 bk-sops 的读取在 `admin_read` 模式下使用管理员只读调用标记。

调用 bk-sops 时必须按模式分流：

- `admin_read`：以当前登录管理员 `request.user.username` 作为原始操作人，并携带管理员只读声明；
- `iam`：保持现有当前用户或 `BusinessConfig.task_executor` 代理人逻辑；
- 管理员只读请求被拒绝或配置缺失时失败关闭，不回退到业务代理人。

这样可以避免“为了看数据而冒用代理人身份”，并确保日志中的查看人始终是实际管理员。

### 6.3 明确保持原鉴权的入口

以下入口不得使用 `can_read_business`：

- `POST/PATCH business_config`；
- `POST/DELETE expose_template`；
- `POST task_create_record`；
- `POST create_task`；
- PO 对外 `backend.apigw.views.create_task`；
- `POST operate_task`；
- `POST operate_node`。

即使请求用户是 `is_superuser`，这些接口仍按用户真实 IAM 权限、审批状态、PO 配置、业务代理人和任务状态执行。

## 7. PO 到 bk-sops 的只读声明

### 7.1 请求头

PO 后端在确认管理员只读模式后生成：

```text
X-BkSops-Admin-Read: true
X-BkSops-Audit-Operator: ${authenticated_username}
```

实现要求：

- 从浏览器或外部请求进入 PO 时，删除所有管理员只读同名头；
- 只有 PO 后端的只读客户端封装能够设置该头；
- `${authenticated_username}` 由服务端使用已认证的 `request.user.username` 替换，不能接受前端传值；
- 原始操作人继续使用当前已有审计头传递；
- 不在 URL、请求体或前端状态中传递可信标记。

### 7.2 bk-sops 校验

先在 PO WebConsole 读取准确 App Code：

```python
from django.conf import settings

print(settings.APP_CODE)
```

将该输出值配置到 bk-sops 的独立白名单：

```text
ADMIN_READ_APP_WHITELIST=${po_app_code}
```

管理员只读模式成立需要同时满足：

1. 请求经过 APIGW 身份注入；
2. `request.app` 中的 App Code 位于 `ADMIN_READ_APP_WHITELIST`；
3. 请求头 `X-BkSops-Admin-Read` 为严格布尔真值；
4. 当前 view 显式启用了 `mark_admin_read_request` 装饰器；
5. HTTP 方法符合该 view 的只读语义。

禁止仅根据请求头设置 `request.is_admin_read`，也禁止在全局中间件中为所有接口启用。`mark_admin_read_request` 只添加到选定的 bk-sops 读取接口，其职责是校验 App Code、请求头和 HTTP 方法，并显式设置 `request.is_admin_read`，不承载任何写权限。

装饰器顺序固定为：

```python
@mark_request_whether_is_trust
@mark_admin_read_request
@project_inject
@iam_intercept(ProjectViewInterceptor())
def selected_read_api(request, project_id):
    ...
```

即先完成现有网关调用方识别，再识别管理员只读模式，最后进入资源注入和 IAM 查看拦截器。未使用该装饰器的接口保持 `request.is_admin_read=False`。

### 7.3 拦截器行为

显式启用管理员只读的接口中：

- `ProjectViewInterceptor` 可在 `request.is_admin_read=True` 时跳过 `project_view`；
- `FlowViewInterceptor` 可在该模式下跳过 `flow_view`；
- `GetTemplateInfoInterceptor` 仅对业务流程模板跳过 `flow_view`，公共流程模板仍执行原有权限校验；
- `TaskViewInterceptor` 可在该模式下跳过 `task_view`；
- `FunctionViewInterceptor` 可在该模式下跳过职能化任务查看权限。

`ProjectEdit`、`FlowEdit`、`TaskOperate`、`AdminEdit` 等写拦截器不识别 `request.is_admin_read`。

## 8. bk-sops 接口行为

### 8.1 业务列表

`get_user_project_list`：

- 普通模式：保持 `get_user_projects(username)`；
- 管理员只读模式：读取所有 `is_disable=False` 的 `Project`；
- 仍使用现有响应结构；
- 列表查询不调用 CMDB。

### 8.2 业务详情

`get_user_project_detail`：

- 普通模式：保持 `project_view` 与当前用户 CMDB 详情查询；
- 管理员只读模式：不调用当前用户身份的 CMDB `search_business`；
- `project_id`、`project_name`、`from_cmdb`、`bk_biz_id` 和名称来自本地 `Project`；
- `bk_biz_developer`、`bk_biz_maintainer`、`bk_biz_tester`、`bk_biz_productor` 等 CMDB 角色字段返回空字符串；
- `auth_actions` 仍查询并返回管理员本人真实拥有的 actions，不补造 `project_view` 或 `project_edit`；
- bk-sops 保持现有响应 schema，不增加或伪造 PO 身份字段。

`is_superuser`、`access_mode` 和 `capabilities` 由 PO 根据本地用户与当前调用模式补充，避免 bk-sops 推断 PO 数据库中的管理员身份。

### 8.3 流程和任务读取

选定的流程与任务读取 API 在管理员只读模式下只跳过查看拦截器，后续仍必须：

- 校验 project、template、task 的归属关系；
- 过滤已删除对象；
- 使用已有响应裁剪和脱敏逻辑；
- 保持分页与缓存行为；
- 将缓存 key 区分普通模式和 `admin_read` 模式。

首批接入的 bk-sops API 限定为：

- `get_user_project_list`、`get_user_project_detail`；
- `get_template_list`、`get_template_info`、`get_template_schemes`；
- `preview_task_tree`；
- `get_task_detail`、`get_task_status`；
- `get_task_node_data`、`get_task_node_detail`、`get_task_node_log`；
- `get_functionalization_task_list`。

PO 的 `get_pipeline_tree`、`get_task_bill_status` 等入口若转调 bk-sops，只能映射到上述白名单 API；新增读取能力必须单独评审并补充清单。

所有带接口缓存的读取 API 都必须把 `admin_read` 模式加入缓存 key。不能只依赖 URL、查询参数或用户名，以免同一管理员的 IAM 响应与管理员只读响应串用。

语义只读的 `preview_task_tree` 虽然使用 POST，但不得写数据库或触发任务。它通过显式接口白名单加入管理员只读范围，不能形成“所有 POST 都允许”的通用规则。

## 9. PO 页面行为

### 9.1 响应能力字段

PO 以独立能力字段表达管理员只读状态：

```json
{
  "is_superuser": true,
  "access_mode": "admin_read",
  "auth_actions": [],
  "capabilities": {
    "can_view": true,
    "can_manage_business": false,
    "can_manage_templates": false,
    "can_create_task": false,
    "can_operate_task": false
  }
}
```

规则如下：

- `auth_actions` 只表示真实 IAM 权限；
- `is_superuser` 只放大 `can_view`；
- 管理员同时拥有真实业务权限时，对应写能力按原规则为 `true`；
- 前端不得通过补造 `auth_actions` 解锁按钮。

### 9.2 页面表现

- 业务选择器展示全部未停用业务；
- 显示“管理员只读视图”标识；
- 未接入 PO 的业务显示“未接入 PO”；
- 未接入时业务配置、接入流程和任务列表返回空状态，不返回 500；
- 业务配置、流程接入、流程和任务详情可查看；
- 未接入 PO 的 bk-sops 流程显示 `exposed=false`，管理员可查看详情，但不能据此新增或删除 PO 接入配置；
- 新增、保存、删除、创建任务、任务操作和节点操作按钮按真实权限控制；
- 管理员没有真实业务权限时，禁用按钮提示“当前为管理员只读模式，需要真实业务权限才能操作”；
- 后端继续拒绝绕过前端直接构造的写请求。

PO 现有 `isStaff` 实际由 `project_edit` 推导，应拆分为“可查看业务配置页面”和“可编辑业务配置”两个概念，避免管理员只读页面被路由守卫挡住。

## 10. 错误处理与安全边界

1. bk-sops 未配置 PO App Code 时，返回明确的管理员只读通道拒绝信息，不尝试代理人回退；
2. 非白名单 App 或伪造请求头不能进入管理员只读模式；
3. PO 写接口不转发管理员只读头；
4. bk-sops 写接口即使收到该头也不设置 `request.is_admin_read`；
5. 业务不存在或已停用时返回明确的不存在状态；
6. PO 业务配置不存在时返回 `configured=false` 或空状态；
7. 普通与管理员只读响应缓存必须隔离；
8. 节点日志、参数和插件输出继续沿用现有脱敏与响应裁剪规则；
9. 管理员只读不会放开文件下载、密钥查看或其他未列入清单的资源；
10. 管理员只读通道配置异常时失败关闭。

## 11. 审计与可观测性

PO 记录管理员只读访问日志，至少包含：

- 管理员用户名；
- 权限来源 `is_superuser`；
- `bk_biz_id`；
- 模板、PO 任务记录、bk-sops 任务和节点标识；
- 接口或动作名称；
- Trace ID；
- 成功或失败及失败类型。

以下入口记录管理员只读审计：业务列表、业务详情、流程详情、任务详情、节点详情和节点日志。高频任务状态轮询不逐次记录业务审计日志，但保留常规访问日志和 Trace，避免日志爆量。

日志不得记录完整流程参数、插件输出、Cookie、应用密钥或其他敏感数据。

## 12. 测试设计

### 12.1 PO 单元测试

- 普通用户无业务权限时仍不可见；
- `is_superuser` 可以通过只读判断，但不能通过真实编辑判断；
- 浏览器伪造管理员只读请求头被丢弃；
- 管理员读取业务、配置、流程和任务成功；
- 管理员对所有写接口仍被拒绝；
- 管理员同时有真实权限时写能力按原规则开放；
- 未接入 PO 的业务返回可识别空状态；
- 管理员只读与普通缓存 key 隔离；
- 审计日志不包含敏感响应体。

### 12.2 bk-sops 单元测试

- 白名单 App + 管理员只读头 + 明确启用的读接口可以进入只读模式；
- 非白名单 App、缺少头或非法头均失败关闭；
- 选定的 `ProjectView`、`FlowView`、`GetTemplateInfo`、`TaskView` 和 `FunctionView` 可以按资源范围只读旁路；
- `get_template_info` 的公共流程模板仍执行原有 IAM 校验；
- 所有写拦截器不接受管理员只读旁路；
- 业务列表返回所有未停用项目；
- 管理员业务详情不调用 CMDB；
- `auth_actions` 不被补造；
- template/task 与 project 的归属校验仍生效；
- 普通用户原有 IAM、CMDB 与缓存行为不变；
- 流程预览不产生数据库写入。

### 12.3 STAG 验收矩阵

使用三个账号：

1. 普通用户，无目标业务权限；
2. 纯 PO `is_superuser`，无目标业务的 bk-sops IAM 和 CMDB 权限；
3. PO `is_superuser`，同时具有部分业务真实权限。

验收标准：

- 纯超级管理员看到的业务数等于 bk-sops 未停用项目数；
- 纯超级管理员可查看任意业务流程和任意 PO 任务详情；
- 业务详情不依赖管理员的 CMDB 权限；
- 纯超级管理员的全部写请求仍失败；
- 有真实权限的超级管理员只在对应业务恢复原有写能力；
- 普通用户的列表和资源权限完全不变；
- 关键访问可用 Trace ID 和审计日志定位。

## 13. 发布顺序

1. **发布 bk-sops 兼容能力**
   - 管理员只读识别代码上线；
   - `ADMIN_READ_APP_WHITELIST` 默认空；
   - 写接口不识别该能力；
   - 同步受影响 API 的中英文文档，校验并更新资源 YAML，重新生成文档包；
2. **配置 bk-sops 调用方白名单**
   - 只配置 PO 的准确 App Code；
   - 不将 PO 加入全局 `APP_WHITELIST`。
3. **发布 PO**
   - 后端、前端和测试一起发布；
   - `ENABLE_SUPERUSER_ADMIN_READ` 默认关闭。
4. **配置管理员**
   - 先查询确认现有用户记录；
   - 设置并回读 `is_superuser=True`。
5. **STAG 开启功能开关并验收**
   - 逐项执行三账号矩阵；
   - 验收通过后再在正式环境打开。

代码发布、功能开关打开和 STAG 业务验收是三个独立完成条件，不能用其中一个替代另一个。

## 14. 回滚方案

紧急回滚顺序：

1. 关闭 PO 的 `ENABLE_SUPERUSER_ADMIN_READ`；
2. 从 bk-sops 的 `ADMIN_READ_APP_WHITELIST` 移除 PO App Code；
3. 清理管理员只读相关缓存；
4. 保留用户 `is_superuser` 数据，避免影响 Django Admin 等既有用途；
5. 确认普通用户 IAM/CMDB 链路恢复为唯一入口。

本方案不写入 bk-sops IAM、不修改 CMDB 权限、不批量改变业务数据，因此可通过配置快速恢复现状。

## 15. 实现边界与交付物

实现分为两个仓库：

### bk-sops

- 管理员只读 App Code 配置；
- `mark_admin_read_request` 显式装饰器；
- 选定查看拦截器的只读旁路；
- 业务列表与详情的管理员只读分支；
- 流程、任务读取接口接入；
- 缓存隔离、单元测试及必要的 API 文档和网关配置。

### bk-sops-facade / PO

- `is_superuser` 只读权限服务；
- 管理员只读 bk-sops 客户端封装；
- 读取接口与写接口分流；
- 页面能力字段、只读标识和按钮控制；
- 未接入业务空状态；
- 管理员读取审计日志；
- 单元测试和 STAG 验收脚本或清单。

实现计划必须分别列出两个仓库的文件、测试、发布依赖和回滚动作，并以先 bk-sops、后 PO 的顺序交付。
