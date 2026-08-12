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
- 仅查询任务 ID：约 3.8 至 4.9 秒。

需要注意的是，慢查询的成因是优化器在“未执行任务极稀疏”的项目上误选了 `PRIMARY` 倒序扫描，
而不是缺少可用索引。未执行任务较多的项目上，优化器本来就能选到按 `id` 有序的
`project_id` 索引并提前结束扫描，耗时约 20 毫秒。因此优化手段必须只排除错误计划，
不能把计划锁死到某个具体索引。

## 目标

1. 保持接口路径、请求参数、响应结构和权限语义不变。
2. 保持 `TaskFlowInstance.id DESC` 排序和 `limit/offset` 分页语义不变。
3. 仅优化明确的“未执行任务”慢查询，不改变其他状态查询的执行路径。
4. 不新增数据库索引，也不依赖某个未在迁移中声明的运维侧索引。
5. 在数据库不是 MySQL 时安全退回原查询。

## 非目标

- 不修改 `pipeline_instance__is_started=true` 查询。
- 不修改未传 `pipeline_instance__is_started` 的任务列表。
- 不修改按 `TaskFlowInstance.id` 精确查询的任务列表。
- 不修改 `task_instance_status`、“我的动态”、任务数量和任务详情接口。
- 不改变默认排序为 `pipeline.create_time`。
- 本期不引入 Redis 缓存或任务列表读模型。

## 触发条件

采用请求参数白名单，仅当请求参数是以下集合的子集时才可能启用两阶段查询：

```text
without_count, project__id, pipeline_instance__is_started, is_child_taskflow, limit, offset
```

并且同时满足：

1. 当前 action 为普通任务列表 `list`。
2. 请求包含 `without_count`。
3. 请求包含有效的 `project__id`。
4. `pipeline_instance__is_started` 明确为 false。
5. `is_child_taskflow` 明确为 false。

不满足任一条件时，继续使用现有 ORM 分页逻辑。

之所以用白名单而不是逐个排除已知的坏组合：生产验证显示，只要带上任意附加筛选条件，
MySQL 往往存在比两阶段查询更优的计划。例如按创建时间区间筛选时，优化器会从
`pipeline_pipelineinstance.create_time` 索引驱动，只需 0.3 至 0.8 秒；而改写成只取 ID 后
优化器转向按项目扫描，退化到 3.5 秒。这类组合无法穷举，白名单可以保证以后新增
FilterSet 字段时不会静默落入优化路径。

## 查询设计

### 第一阶段：只取 ID 并排除 PRIMARY

在完成现有 FilterSet、过期过滤和 180 天过滤后，基于最终 queryset 生成仅查询
`TaskFlowInstance.id` 的分页 SQL：

```sql
SELECT t.id
FROM taskflow3_taskflowinstance AS t
    IGNORE INDEX (`PRIMARY`)
INNER JOIN pipeline_pipelineinstance AS p
    ON p.id = t.pipeline_instance_id
WHERE ...
ORDER BY t.id DESC
LIMIT %s OFFSET %s
```

只取 ID 让分页查询能落在索引上，省掉逐行回表；`IGNORE INDEX (PRIMARY)` 只排除掉造成慢查询的
全表倒序扫描，把索引选择权留给优化器。索引提示复用现有的
`TaskFlowInstanceManager._inject_ignore_primary_index_hint`，与任务名称搜索优化保持同一套实现。

这里不使用 `FORCE INDEX`。生产验证显示强制 `idx_proj_del_child_id_pipe` 会让未执行任务较多的项目
从 20 毫秒退化到 1.1 秒，因为该索引在 ORM 生成的条件下无法提供按 `id` 有序的访问路径，必须
filesort 扫完整个项目。

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

索引提示是 MySQL 语法，因此只有 `connection.vendor == "mysql"` 时才启用两阶段查询，其余数据库直接使用原 ORM 分页。

`IGNORE INDEX (PRIMARY)` 不依赖任何特定索引存在，因此不需要运行期探测表结构，也不存在探测结果被错误缓存的问题。

两阶段查询只读取数据。第一阶段执行异常不进行静默重试，避免同一请求先执行慢 SQL 再重复执行；异常按现有数据库异常处理链上报。

## 分页与响应

- 沿用现有 paginator 的 `limit`、`offset`、`count=-1` 和 `request`。
- 第一阶段 ID 查询直接应用相同的 `LIMIT/OFFSET`。
- 返回不足 `limit` 条时不补查，因为这表示过滤结果已耗尽。
- 序列化、任务权限注入、模板权限和模板信息注入继续使用现有逻辑。
- API 响应字段和 HTTP 状态码不变。

## 测试设计

### 单元测试

1. 仅在显式“未执行”参数组合下触发两阶段路径。
2. `is_started=true`、未传状态、显式排序、名称搜索、“我的动态”、`task_instance_status`、任务 ID 精确查询，
   以及模板、创建方式、创建人、创建时间区间等白名单外的任意附加筛选条件均不触发。
3. 第一阶段 SQL 包含 `IGNORE INDEX (\`PRIMARY\`)` 且参数仍由数据库驱动参数化。
4. 第二阶段包含 `select_related("pipeline_instance", "project")`。
5. 第二阶段结果严格恢复第一阶段 ID 顺序。
6. 结果少于 15 条和空结果正确返回。
7. 非 MySQL 时回退原逻辑且不访问游标。
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

生产 WebConsole 对 3 个真实任务 ID 和 1 个不存在 ID 的复测显示，原路径耗时约
`5-22ms`，强制使用 `idx_proj_del_child_id_pipe` 的两阶段路径耗时约 `222-238ms`，
且强制索引计划会从 `PRIMARY + const` 单行查询退化为扫描项目复合索引。因此任务 ID
精确查询必须留在原 ORM 分页路径。

生产 WebConsole 在两个数据分布相反的项目上对比了三种方案，结果决定了最终选型
（`MAX_EXECUTION_TIME` 上限 8 秒）：

| 项目 | 场景 | 原路径 | 两阶段 + FORCE 覆盖索引 | 两阶段 + IGNORE PRIMARY |
| --- | --- | --- | --- | --- |
| 5001537，224 万任务、13 条未执行 | 纯未执行 | 超时 | 4348ms | 3802ms |
| 5001537 | 附加最近 1 天创建时间 | 339ms | 3552ms | 3553ms |
| 5001537 | 附加 7 至 8 天创建时间区间 | 393ms | 3689ms | 3490ms |
| 5000122，578 万任务、未执行较多 | 纯未执行 | 23.2ms | 1151ms | 21.6ms |
| 5000122 | 附加最近 1 天创建时间 | 397.7ms | 1163ms | 350.4ms |
| 5000122 | 附加 7 至 8 天创建时间区间 | 376.1ms | 超时 | 366.4ms |

由此得到两条结论：`FORCE INDEX` 会在未执行任务较多的项目上造成数量级回退，必须改用
`IGNORE INDEX (PRIMARY)`；带创建时间区间的组合即使改用 `IGNORE PRIMARY` 仍会回退约 9 至 10 倍，
必须由参数白名单挡在优化路径之外。

同时记录一个未在本期解决的问题：Django 把 `is_deleted=False` 一类布尔过滤编译成 `NOT col`
而非 `col = 0`，`NOT col` 无法作为 ref 的 key part，导致
`idx_proj_del_child_id_pipe` 在 ORM 查询下只用到首列 `project_id`，后续列形同虚设并被迫 filesort。
手写等值条件的同一查询可以用满前三列且无需 filesort。彻底解决稀疏项目的秒级耗时需要消除跨表
状态判断（例如把 `is_started` 冗余到任务表并配套索引），应另立需求跟进。

## 发布与回退

两阶段路径使用独立判断函数封装，便于快速禁用。若灰度期间出现查询计划或兼容性回归，将判断函数关闭并恢复原 ORM 分页，不涉及数据回滚或数据库 DDL。

灰度期需要重点观察未执行任务较多的项目：这类项目原本就是毫秒级返回，一旦出现秒级延迟即说明
优化器又选回了需要 filesort 的计划，应立即关闭该路径。
