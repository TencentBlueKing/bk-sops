# 跨 Skill 转交协议

> 本模块为 SOPS Skill 公共依赖，在打包时内联到各 Skill 的 SKILL.md 中。定义 Skill 之间工作转交的上下文传递格式、分级规则与全局路由表。

---

## 1. 核心原则

Skill 之间的工作转交必须携带结构化的上下文包，避免目标 Skill 重复收集已有信息。

---

## 2. Handoff 上下文包格式

当 Skill A 需要将工作转交给 Skill B 时，按以下格式组装上下文包：

```markdown
## Handoff 上下文

| 字段 | 值 |
|------|-----|
| 来源 Skill | {skill 名称} |
| 目标 Skill | {skill 名称} |
| 转交原因 | {一句话说明} |
| 业务 ID | {bk_biz_id} |
| 用户标识 | {当前用户} |

### 已收集数据
{来源 skill 已通过 API 获取的关键数据摘要，避免目标 skill 重复调用}

### 已执行操作
{来源 skill 已尝试的操作及结果}

### 用户已确认信息
{用户在来源 skill 中已确认的选择和偏好}
```

---

## 3. Handoff 分级

| 分级 | 含义 | 处理方式 |
|------|------|---------|
| **强制前置** | 目标 skill 是当前操作的必要前提，不完成则阻塞 | 在执行前自动触发，不询问用户"要不要做" |
| **强制后置** | 当前操作完成后必须衔接的下一步 | 完成后自动引导，不仅仅"建议" |
| **建议** | 有价值但非必须的衔接 | 向用户推荐，由用户决定 |

---

## 4. 全局 Handoff 规则表

| 来源 Skill | 条件 | 目标 Skill | 分级 | 传递的关键上下文 |
|-----------|------|-----------|------|----------------|
| task-runner | 目标环境含 prod | change-validator | 强制前置 | 模板信息、参数、目标主机列表 |
| task-runner | 任务创建并启动成功 | task-monitor | 强制后置 | task_id、流程名称、预期耗时 |
| task-monitor | 快速分析不足（未匹配已知问题 或 重试 2 次仍失败） | troubleshooter | 强制后置 | task_id、失败节点、已获取日志、已尝试操作 |
| troubleshooter | 错误分类为权限类 | permission-manager | 强制后置 | 错误信息、涉及的 API、已排查路径 |
| flow-builder | 编排生成完成 | flow-review | 强制后置 | pipeline_tree、场景类型、知识库匹配结果 |
| health-checker | 发现高失败率流程 | flow-review | 建议 | 流程模板 ID、失败统计数据 |
| health-checker | 发现反复失败的任务 | troubleshooter | 建议 | 任务 ID、失败模式摘要 |
| troubleshooter | 根因为流程设计缺陷 | flow-review | 建议 | 问题节点、缺陷描述 |
| audit-reporter | 发现异常模式 | ops-insight | 建议 | 异常数据摘要 |

---

## 5. 使用规则

- 在执行写操作前，检查 §4 表中是否有以当前 skill 为「来源」、分级为「强制前置」的规则 → 若匹配，先组装上下文包并触发目标 skill
- 在完成核心工作后，检查 §4 表中是否有以当前 skill 为「来源」、分级为「强制后置」的规则 → 若匹配，自动引导并传递上下文
- 「建议」类 handoff 在合适时机向用户推荐，不强制
