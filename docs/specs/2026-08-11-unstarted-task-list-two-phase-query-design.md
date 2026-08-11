# 未执行任务列表两阶段查询优化设计

## 背景

`GET /api/v3/taskflow/` 在同时使用以下参数时出现稳定慢查询：

- `without_count=true`
- `project__id` 已设置为目标项目 ID
- `pipeline_instance__is_started=false`
- `is_child_taskflow=false`
- 默认按 `TaskFlowInstance.id DESC` 排序

生产执行计划显示，原查询为了避免排序而从
`taskflow3_taskflowinstance.PRIMARY` 倒序扫描，然后逐条通过
`pipeline_instance_id` 查询 `pipeline_pipelineinstance`。目标项目在最近一千万条候选任务中实际只有
13 条满足“180 天内、未启动、未过期”，不足 `LIMIT 15`，因此数据库无法提前结束扫描。

已验证的真实耗时：

- 原接口：约 70 秒以上。
- 仅查询任务 ID，强制使用现有
  `idx_proj_del_child_id_pipe`：首次 4.13 秒，预热后 2.99 秒。

## 目标

1. 保持接口路径、请求参数、响应结构和权限语义不变。
2. 保持 `TaskFlowInstance.id DESC` 排序和 `limit/offset` 分页语义不变。
3. 仅优化明确的“未执行任务”慢查询，不改变其他状态查询的执行路径。
4. 不新增数据库索引。
5. 在索引不存在或数据库不是 MySQL 时安全退回原查询。

## 非目标

- 不修改 `pipeline_instance__is_started=true` 查询。
- 不修改未传 `pipeline_instance__is_started` 的任务列表。
- 不修改 `task_instance_status`、“我的动态”、任务数量和任务详情接口。
- 不改变默认排序为 `pipeline.create_time`。
- 本期不引入 Redis 缓存或任务列表读模型。

## 触发条件

仅当请求同时满足以下条件时启用两阶段查询：

1. 当前 action 为普通任务列表 `list`。
2. 请求包含 `without_count`。
3. 请求包含有效的 `project__id`。
4. `pipeline_instance__is_started` 明确为 false。
5. `is_child_taskflow` 明确为 false。
6. 未传入显式 `order_by`。
7. 不包含 `creator_or_executor`。
8. 不包含 `task_instance_status`。
9. 不包含 `pipeline_instance__name__icontains`，避免与现有名称搜索优化路径重叠。

不满足任一条件时，继续使用现有 ORM 分页逻辑。

## 查询设计

### 第一阶段：覆盖索引只取 ID

在完成现有 FilterSet、过期过滤和 180 天过滤后，基于最终 queryset 生成仅查询
`TaskFlowInstance.id` 的分页 SQL：

```sql
SELECT t.id
FROM taskflow3_taskflowinstance AS t
    FORCE INDEX (idx_proj_del_child_id_pipe)
INNER JOIN pipeline_pipelineinstance AS p
    ON p.id = t.pipeline_instance_id
WHERE ...
ORDER BY t.id DESC
LIMIT %s OFFSET %s
```

SQL 条件继续由 Django queryset 生成和参数化，索引提示通过对已编译 SQL 的固定表名注入完成。
数据库游标只返回整数 ID，避免把 RawQuerySet 的延迟字段带入第二阶段。

### 第二阶段：批量加载详情

根据第一阶段返回的最多 `limit` 个 ID 执行一次 ORM 查询：

```python
queryset.filter(id__in=task_ids).select_related(
    "pipeline_instance", "project"
)
```

`TaskFlowInstanceListSerializer` 会读取 `pipeline_instance` 的名称、创建时间、开始/结束时间和状态，
并嵌套序列化 `project`，因此必须使用 `select_related` 避免 N+1 查询。

数据库不保证 `IN` 查询返回顺序。第二阶段完成后，按照第一阶段 ID 列表建立位置映射并在内存中恢复顺序。

## 数据库兼容与回退

现有生产库包含 `idx_proj_del_child_id_pipe`，字段顺序为：

```text
project_id, is_deleted, is_child_taskflow, id, pipeline_instance_id
```

但该索引未在当前源码迁移中声明。因此启用前必须同时满足：

- `connection.vendor == "mysql"`；
- 数据库表中存在 `idx_proj_del_child_id_pipe`。

索引能力检查按进程缓存，避免每次请求执行 `SHOW INDEX`。若数据库不是 MySQL、索引不存在或能力检查失败，则不注入索引提示，直接使用原查询路径。

两阶段查询只读取数据。第一阶段执行异常不进行静默重试，避免同一请求先执行慢 SQL 再重复执行；异常按现有数据库异常处理链上报。索引缺失通过执行前能力检查规避。

## 分页与响应

- 沿用现有 paginator 的 `limit`、`offset`、`count=-1` 和 `request`。
- 第一阶段 ID 查询直接应用相同的 `LIMIT/OFFSET`。
- 返回不足 `limit` 条时不补查，因为这表示过滤结果已耗尽。
- 序列化、任务权限注入、模板权限和模板信息注入继续使用现有逻辑。
- API 响应字段和 HTTP 状态码不变。

## 测试设计

### 单元测试

1. 仅在显式“未执行”参数组合下触发两阶段路径。
2. `is_started=true`、未传状态、显式排序、名称搜索、“我的动态”和 `task_instance_status` 均不触发。
3. 第一阶段 SQL 包含 `FORCE INDEX (idx_proj_del_child_id_pipe)` 且参数仍由数据库驱动参数化。
4. 第二阶段包含 `select_related("pipeline_instance", "project")`。
5. 第二阶段结果严格恢复第一阶段 ID 顺序。
6. 结果少于 15 条和空结果正确返回。
7. 非 MySQL或索引不存在时回退原逻辑。
8. `offset > 0` 时分页语义保持不变。

### 回归测试

- 任务列表已有测试集全部通过。
- 对序列化查询数增加断言，避免引入 pipeline/project N+1。
- 验证权限注入和模板信息注入收到的实例顺序与响应顺序一致。

### 生产验证

灰度观察以下指标：

- 目标 URL 的 P50、P95、P99；
- API worker timeout 数量；
- 第一阶段 SQL 耗时和扫描行数；
- DB CPU、IO 和 Buffer Pool 命中率；
- `is_started=true` 和无状态筛选的延迟不发生回归。

## 发布与回退

两阶段路径使用独立判断函数封装，便于快速禁用。若灰度期间出现查询计划或兼容性回归，将判断函数关闭并恢复原 ORM 分页，不涉及数据回滚或数据库 DDL。
