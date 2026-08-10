# 标准运维委托调用审计操作人设计

## 背景

PO 环境通过 `bk-sops-facade` 调用标准运维 API Server。用户 A 在 PO 登录、完成业务权限校验和审批后，Facade 会读取 `BusinessConfig.task_executor` 得到业务执行代理人 B，并通过 `get_sops_client_by_username(B)` 调用标准运维。

现有链路中，内部网关认证用户、标准运维 `request.user`、任务创建人及审计操作人均为 B。PO 登录用户 A 只保存在 Facade 本地记录中，没有进入标准运维请求，因此审计中心无法回答“谁在 PO 发起了操作”。

## 目标

- PO 发起的任务创建、任务操作和节点操作在审计中心以 A 作为最终操作人。
- 内部网关认证、标准运维 IAM 校验、任务创建与任务操作继续使用 B。
- 标准运维任务实例的 `creator`、运行时执行身份及现有本地操作记录语义保持不变。
- 非可信应用、缺失委托身份或非法委托身份一律回退为网关认证用户 B。
- 不新增审计动作、资源或公开 API 请求/响应字段。
- 审计身份解析失败不得阻断业务请求。

## 非目标

- 不让 A 直接承担标准运维 IAM 权限校验。
- 不改变 PO 的审批、业务权限和 `BusinessConfig.task_executor` 配置方式。
- 不改变标准运维任务实例的创建人或执行代理逻辑。
- 不允许普通 API 调用方自行指定审计操作人。
- 本期不引入共享密钥、JWS/HMAC、时间戳或 nonce；如后续合规要求提高，再在本设计的可信应用边界上增加签名和防重放。

## 方案选择

### 采用：可信应用声明委托审计操作人

Facade 继续以 B 创建标准运维网关客户端，并由后端添加专用请求头：

```text
X-BkSops-Audit-Operator: A
```

标准运维仅在以下条件全部成立时接受该值：

1. 请求由 API Gateway 注入应用身份，且应用身份已经验证。
2. 调用应用 app code 位于专用配置 `BK_AUDIT_DELEGATED_OPERATOR_APPS` 中。
3. 请求头中的 A 非空、长度不超过 64，并且只包含允许的账号字符。

接受后，仅审计事件的 `AuditContext.username` 使用 A。业务代码继续使用 `request.user.username`，因此 IAM、任务创建、异步启动、任务/节点操作均保持 B。

PO Facade 使用 `get_client_by_username(B)` 走内部网关免登录认证。当 B 没有可用 access token 时，网关仍会验证 Facade 应用身份，但不会把声明的 B 标记为已验证用户。委托头由已验证且在专用白名单中的 Facade 后端生成，因此 B 的 JWT 用户验证状态不作为接受 A 的条件。

### 不采用：把网关用户改成 A

该方案会使标准运维 IAM 和任务操作权限同时切换到 A。PO 外部用户通常没有目标业务和模板权限，与“B 继续作为实际执行身份”的目标冲突。

### 暂不采用：每个请求独立签名

签名能增强跨代理链路的不可篡改性，但需要新增密钥分发、轮换和防重放机制。当前内部网关已经认证调用应用和代理用户，本期使用专用 app code 白名单建立最小可信边界；签名作为后续增强项。

## 身份与数据流

| 环节 | 身份 | 用途 |
| --- | --- | --- |
| PO 登录与业务权限校验 | A | 判断谁可以在 PO 发起操作 |
| Facade 本地 `created_by` / `operator` / `task_creator` | A | PO 自身留痕 |
| Facade 网关客户端 | B | 获取标准运维权限并发起请求 |
| API Gateway 免登录调用用户 | B | 生成标准运维请求用户，可能不带已验证用户标记 |
| 标准运维 `request.user.username` | B | IAM、任务创建和任务/节点操作 |
| 标准运维审计 `username` | A | 审计中心最终操作人 |
| 标准运维审计资源快照 | 任务真实数据 | 可继续体现任务 creator/executor 为 B |

完整链路：

```text
PO 用户 A
  -> PO 鉴权和审批
  -> Facade 读取任务执行人 B
  -> 以 B 调用 API Gateway，并由 Facade 后端添加 A 的审计头
  -> API Gateway 验证 Facade 应用身份并携带 B
  -> 标准运维以 B 完成 IAM 与业务操作
  -> 标准运维仅在可信条件满足时以 A 上报审计
```

## PO Facade 改造

以 `origin/release` 为生产基线建立独立功能分支。

### 请求头生成

在 `backend/utils/bkapi.py` 定义统一头名称和构造函数，输入 PO 已认证的用户名 A，输出传给 BKAPI SDK 的 headers。Facade 后端必须覆盖该请求头，不能从浏览器请求头透传。

### 覆盖入口

- `backend/services/task_create.py::create_sops_task`：使用现有 `creator` 参数传递 A。
- `backend/views/operate_task.py::operate_task`：使用 `request.user.username` 传递 A。
- `backend/views/operate_node.py::operate_node`：使用 `request.user.username` 传递 A。

以上入口继续使用 `BusinessConfig.task_executor` 创建客户端。BKAPI SDK 的 `headers` 参数只增加委托审计声明，不修改 `bk_username` 和 access token。

## 标准运维改造

以最新 `upstream/master` 为基线建立 `feat/delegated-audit-operator`。

### 配置

新增部署配置 `BK_AUDIT_DELEGATED_OPERATOR_APPS`，内容为逗号分隔的 app code，默认空集合。默认关闭委托身份解析，避免代码部署后自动信任任何调用应用。

生产启用时配置 PO Facade 的真实 app code；不在社区代码中硬编码内部应用标识。

### 身份解析

在 `gcloud/contrib/audit/utils.py` 增加公共解析函数，输入 Django request，返回最终审计用户名：

- 默认返回 `request.user.username`，即 B。
- 只有 APIGW JWT 应用已验证、app code 在专用白名单且委托头合法时，返回 A。
- 接受委托身份时记录 A、B、app code 和 trace ID 的结构化日志。
- 请求头存在但不可信或非法时记录不包含原始非法值的告警，并回退 B。
- 函数不得修改 `request.user`。

### 覆盖入口

- `gcloud/apigw/views/create_task.py`
- `gcloud/apigw/views/operate_task.py`
- `gcloud/apigw/views/operate_node.py`

三个入口分别计算 `audit_username` 并仅传给 `bk_audit_add_event_on_commit`。原有 `username=request.user.username` 继续用于任务创建、Celery 参数、`task_action` 和 `nodes_action`。

## 安全与失败处理

- app code 必须来自 APIGW 认证后的 `request.app`，且 `request.app.verified is True`，不能读取普通业务请求参数。
- 不要求 `_apigw_jwt_user_verified is True`。免登录代理调用中的 B 可能只是由已验证应用声明的执行身份；A 的可信来源是已验证且在专用白名单中的 Facade 应用，而不是 B 的用户认证状态。
- 专用白名单不得复用现有 `APP_WHITELIST`，避免把其他信任应用自动扩展为审计身份代理。
- 委托头只接受 ASCII 账号字符 `A-Z`、`a-z`、`0-9`、`_`、`-`、`.`、`@`，长度为 1 到 64。
- 委托头缺失、非法、调用应用未验证或不可信时均回退 B，不返回错误响应。
- 日志不得记录 token、cookie、请求体或其他敏感信息。

## API 与审计中心边界

- 不修改公开请求 body、response、operationId、动作或资源定义。
- 专用请求头是 Facade 与标准运维之间的内部可信契约，不在公开 APIGW 申请文档中开放给普通调用方。
- 审计中心主操作人显示 A；任务资源快照仍可显示 creator/executor 为 B。这是“谁发起”与“以谁执行”的预期分离，不是数据不一致。
- 当前 `bk-audit==1.1.1` 已允许调用方独立设置 `AuditContext.username`，无需升级 SDK。

## 测试设计

### PO Facade

- 创建标准运维任务时，网关客户端仍以 B 创建，请求 headers 携带 A。
- 创建请求失败和响应异常时，headers 传递行为不改变错误处理。
- 任务操作和节点操作均携带当前 PO 登录用户 A，业务请求内容保持不变。
- 浏览器传入同名请求头不会被透传；最终值始终由后端 `request.user.username` 生成。

### 标准运维

- 可信且已验证 app、合法 A：无论 B 的 JWT 用户验证状态如何，解析结果和审计操作人均为 A。
- 未验证或非可信 app：忽略 A，审计操作人为 B。
- A 缺失、空白、超长或包含非法字符：审计操作人为 B。
- `create_task` 的任务 creator 仍为 B，审计 username 为 A。
- `operate_task` 的 Celery/`task_action` 用户仍为 B，审计 username 为 A。
- `operate_node` 的 `nodes_action` 用户仍为 B，审计 username 为 A。
- 现有无委托头调用全部保持 B，原 API 响应不变。

## 发布与验收

1. 先发布标准运维代码，保持 `BK_AUDIT_DELEGATED_OPERATOR_APPS` 为空，确认所有调用仍记录 B。
2. 发布 PO Facade，使三个入口开始发送由后端生成的委托头；此时标准运维仍因白名单为空而记录 B。
3. 在标准运维 API Server 配置 PO Facade 的真实 app code 并滚动发布。
4. 使用 PO 用户 A、业务执行人 B 创建并启动测试任务。
5. 验证标准运维业务日志中 IAM/任务操作用户为 B，委托映射日志为 A/B，审计中心操作人为 A。
6. 验证任务实例 creator/executor 和 PO 本地记录符合身份映射表。
7. 使用非白名单应用伪造委托头，确认审计仍记录其网关认证用户。

回滚时只需清空 `BK_AUDIT_DELEGATED_OPERATOR_APPS`，即可立即恢复“审计操作人等于网关认证用户”的原行为，无需回滚 PO 请求头。
