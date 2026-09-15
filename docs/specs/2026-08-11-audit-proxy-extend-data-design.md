# 委托审计代理执行人扩展字段设计

## 背景

PO 通过免登录网关调用 api-server 时，标准运维已经能够保持两类身份相互独立：

- PO 登录用户 A 作为审计事件的最终操作人 `username`。
- PO 业务配置中的任务执行人 B 继续用于 IAM 权限校验和任务执行。

当前 api-server 只在本地 `delegated_operator_resolved` 日志中记录 B，审计 SDK 上报的事件不包含该信息。审计中心因此可以检索 A，但无法从事件本身追溯代理执行人 B。

## 目标

可信委托生效时，在不改变现有身份语义的前提下，将代理执行人写入审计事件：

```json
{
  "username": "operator_a",
  "extend_data": {
    "proxy_username": "executor_b"
  }
}
```

本期不新增审计动作或资源，不调整 IAM 权限主体、任务执行人及现有审计操作人。

## 方案对比

### 方案一：使用 `extend_data`（采用）

BK Audit SDK 1.1.1 的 `add_event` 原生支持 `extend_data`，并将其序列化到 `AuditEvent.extend_data`。该字段适合承载不改变标准操作人语义的辅助上下文。

优点：不污染标准身份字段和资源快照，兼容现有审计事件结构；普通调用可以保持原样。

### 方案二：复用 `user_identify_src_username`（不采用）

该字段描述最终操作人的账号来源信息，不是代理执行人。复用会导致审计中心对操作主体的解释产生歧义。

### 方案三：写入 `instance_data`（不采用）

任务实例数据用于资源快照。代理执行人属于事件上下文而不是任务资源属性，写入会污染前后快照和差异展示。

## 设计

### 委托身份解析

保留现有 `get_audit_username(request)` 的信任校验和回退逻辑，新增 `get_audit_event_kwargs(request)` 统一生成事件身份参数：

```python
{
    "username": audit_username,
    "extend_data": {"proxy_username": proxy_username},
}
```

只有同时满足以下条件时才包含 `proxy_username`：

1. 现有可信应用和委托用户名校验已经接受 A；
2. 请求中存在非空代理执行人 B；
3. A 与 B 不相同。

普通登录调用、未携带委托操作人、应用不可信、委托用户名无效以及 A 与 B 相同的场景，`extend_data` 均为空，不把普通操作误标记为代理操作。

### 审计事件上报

`bk_audit_add_event_on_commit` 和 `bk_audit_add_event` 增加可选参数 `extend_data=None`：

1. 事务提交回调继续透传该字段；
2. 上报前复用 `sanitize_audit_data` 清理敏感字段；
3. 调用 `bk_audit_client.add_event(..., extend_data=safe_extend_data)`。

未传 `extend_data` 的全部存量调用行为保持不变。

### 接入范围

本期只调整已支持 PO 委托审计的三个 APIGW 写操作入口：

- 创建任务 `create_task`；
- 操作任务 `operate_task`；
- 操作节点 `operate_node`。

三个入口从只传 `username=get_audit_username(request)` 调整为解包 `get_audit_event_kwargs(request)`，避免各接口重复实现 A/B 判断。

## 异常与安全边界

- `proxy_username` 仅来自 api-server 已认证请求对象的 `request.user.username`，不直接信任新增外部 Header。
- 委托 Header 不可信或格式非法时沿用现有回退策略，审计操作人和执行人均为 B，且不生成代理扩展字段。
- `extend_data` 继续遵守审计数据脱敏规则；审计 SDK 异常仍只记录错误日志，不阻断业务请求。
- 审计中心是否将 `extend_data.proxy_username` 展示为独立检索字段，由审计中心字段映射配置决定；本设计保证事件原始数据包含该字段。

## 测试与验收

单元测试覆盖：

1. 可信委托 A/B 不同时生成 `extend_data.proxy_username=B`；
2. 免登录网关用户未验证但应用可信时仍生成代理字段；
3. 普通调用、回退调用及 A/B 相同时不生成代理字段；
4. `bk_audit_add_event_on_commit` 将扩展字段传递到实际上报函数；
5. `bk_audit_add_event` 清理扩展数据后传给 BK Audit SDK；
6. 三个 APIGW 写入口均使用统一事件参数。

Stage 验收以同一 trace 中的以下结果为准：

- IAM 权限主体仍为 B；
- 审计事件 `username` 为 A；
- 审计事件原始数据包含 `extend_data.proxy_username=B`；
- api-server 记录 `bk_audit add_event: success`。

## 非目标

- 不修改 PO Facade Header 协议；
- 不把 B 改为最终审计操作人；
- 不调整审计动作、资源或审计中心展示配置；
- 不为普通非委托操作补充 `proxy_username`。
