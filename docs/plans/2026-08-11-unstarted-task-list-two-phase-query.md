# Unstarted Task List Two-Phase Query Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Multi-agent execution is not used for this task.

**Goal:** Reduce the explicitly filtered unstarted task-list request from roughly 70 seconds to the verified 3-4 second ID-scan range without changing API results, ordering, pagination, or other status-filter paths.

**Architecture:** Add a narrowly gated list-view branch that asks `TaskFlowInstanceManager` for a page using two phases. Phase one compiles the fully filtered queryset as an ID-only query and injects the existing production composite-index hint; phase two reapplies the same queryset filters to those IDs, loads `pipeline_instance` and `project` in one query, and restores the phase-one order. Non-MySQL databases and schemas without the production index keep the original ORM path.

**Tech Stack:** Python 3.6, Django ORM, Django REST Framework, MySQL 5.7-compatible SQL, `django.test`, `mock`.

## Global Constraints

- Design source: `docs/specs/2026-08-11-unstarted-task-list-two-phase-query-design.md`.
- Do not add or alter database indexes or migrations.
- Preserve `TaskFlowInstance.id DESC`, `limit`, `offset`, response fields, IAM injection, and template-info injection.
- Only the explicit `pipeline_instance__is_started=false` and `is_child_taskflow=false` list path with `without_count` and default ordering may opt in.
- `is_started=true`, absent status, explicit ordering, name search, “我的动态”, `task_instance_status`, count, retrieve, and other endpoints must retain their existing path.
- Do not silently retry a failed phase-one SQL query.
- The current primary worktree is dirty; execution must use an isolated worktree based on the latest `upstream/master` without stashing or modifying user changes.
- Repository commits must reference TAPD Bug `1010131351162150454`：`任务列表筛选“未执行”时接口耗时过长`。

---

### Task 1: Add manager-level two-phase page retrieval

**Files:**
- Modify: `gcloud/taskflow3/models.py:570-610`
- Test: `gcloud/tests/taskflow3/models/test_taskflow_instance_manager.py`

**Interfaces:**
- Consumes: a fully filtered, unsliced `QuerySet[TaskFlowInstance]`, integer `limit`, and integer `offset`.
- Produces: `TaskFlowInstanceManager.fetch_unstarted_task_list_page_two_phase(queryset, limit, offset) -> list[TaskFlowInstance]`.
- Produces: `TaskFlowInstanceManager.has_unstarted_task_list_covering_index() -> bool`, cached per process and safe for non-MySQL databases.

- [ ] **Step 1: Write failing tests for index-hint injection, ID execution, detail preloading, and order restoration**

Add manager tests that construct an ID-only SQL string, return cursor rows `[(9,), (4,), (2,)]`, and assert:

```python
result = TaskFlowInstance.objects.fetch_unstarted_task_list_page_two_phase(
    queryset=queryset,
    limit=15,
    offset=5,
)

assert [instance.id for instance in result] == [9, 4, 2]
cursor.execute.assert_called_once_with(expected_sql_with_force_index, expected_params)
detail_queryset.select_related.assert_called_once_with("pipeline_instance", "project")
```

The mock queryset records `values_list("id", flat=True)`, slicing with `slice(5, 20)`, `filter(id__in=[9, 4, 2])`, and the `select_related` call. Add a separate assertion that an empty ID result does not execute phase two.

- [ ] **Step 2: Run the focused manager tests and verify the new API is absent**

Run:

```bash
pytest -q gcloud/tests/taskflow3/models/test_taskflow_instance_manager.py
```

Expected: the new tests fail because `fetch_unstarted_task_list_page_two_phase` and the covering-index capability method do not exist; the existing ignore-primary tests continue to pass.

- [ ] **Step 3: Implement cached index capability detection**

In `TaskFlowInstanceManager`, add constants:

```python
TASK_LIST_UNSTARTED_COVERING_INDEX = "idx_proj_del_child_id_pipe"
FORCE_UNSTARTED_COVERING_INDEX_HINT_SQL = "FORCE INDEX (`idx_proj_del_child_id_pipe`)"
```

Add a process-cached method that returns `False` for non-MySQL connections, otherwise executes:

```python
cursor.execute(
    "SHOW INDEX FROM `taskflow3_taskflowinstance` WHERE Key_name = %s",
    ["idx_proj_del_child_id_pipe"],
)
```

It returns whether `cursor.fetchone()` is present. Catch `django.db.DatabaseError`, log one warning through the module `logger`, and cache `False`. Expose `cache_clear()` through the decorated function so tests can isolate cached state.

- [ ] **Step 4: Implement the ID-only query and filtered detail reload**

Implement the method with this exact flow:

```python
if not self.has_unstarted_task_list_covering_index():
    return list(queryset[offset : offset + limit])

id_queryset = queryset.values_list("id", flat=True)[offset : offset + limit]
sql, params = id_queryset.query.sql_with_params()
sql = self._inject_unstarted_covering_index_hint(sql)

with connection.cursor() as cursor:
    cursor.execute(sql, params)
    task_ids = [row[0] for row in cursor.fetchall()]

if not task_ids:
    return []

instances = queryset.filter(id__in=task_ids).select_related("pipeline_instance", "project")
instance_by_id = {instance.id: instance for instance in instances}
return [instance_by_id[task_id] for task_id in task_ids if task_id in instance_by_id]
```

Reapplying the original queryset in phase two prevents a task that starts, expires, or is deleted between statements from being returned with stale filter semantics. Missing IDs are omitted without backfilling, matching a concurrent-change race rather than issuing another large scan.

- [ ] **Step 5: Run manager tests**

Run:

```bash
pytest -q gcloud/tests/taskflow3/models/test_taskflow_instance_manager.py
```

Expected: all existing and new manager tests pass.

### Task 2: Gate the optimization in the task-list endpoint

**Files:**
- Modify: `gcloud/core/apis/drf/viewsets/taskflow.py:321-352`
- Test: `gcloud/tests/core/apis/drf/views_set/test_task_instance_view.py`

**Interfaces:**
- Consumes: `request.query_params` from `TaskFlowInstanceViewSet.list`.
- Produces: `TaskFlowInstanceViewSet._should_use_two_phase_unstarted_task_list(request) -> bool`.
- Calls: `TaskFlowInstance.objects.fetch_unstarted_task_list_page_two_phase(queryset, limit, offset)` only when the guard returns `True`.

- [ ] **Step 1: Write a failing positive-path endpoint test**

Add a request with:

```python
query_params = {
    "project__id": self.test_project.id,
    "pipeline_instance__is_started": False,
    "is_child_taskflow": False,
    "without_count": True,
    "limit": 15,
    "offset": 0,
}
```

Patch `fetch_unstarted_task_list_page_two_phase` to return `[]`; assert it is called once with the filtered queryset, `limit=15`, and `offset=0`, while `fetch_task_list_page_ignore_primary_index` is not called.

- [ ] **Step 2: Write guard regression tests for unaffected paths**

Use `SimpleNamespace(query_params=params)` to assert the guard returns `False` for these exact dictionaries:

```python
{"project__id": "1", "pipeline_instance__is_started": "true", "is_child_taskflow": "false"}
{"project__id": "1", "is_child_taskflow": "false"}
{"project__id": "1", "pipeline_instance__is_started": "false", "is_child_taskflow": "false", "order_by": "-pipeline_instance__create_time"}
{"project__id": "1", "pipeline_instance__is_started": "false", "is_child_taskflow": "false", "pipeline_instance__name__icontains": "demo"}
{"project__id": "1", "pipeline_instance__is_started": "false", "is_child_taskflow": "false", "creator_or_executor": "user"}
{"project__id": "1", "pipeline_instance__is_started": "false", "is_child_taskflow": "false", "task_instance_status": "failed"}
{"project__id": "1", "pipeline_instance__is_started": "false", "is_child_taskflow": "true"}
```

Also assert both string forms `"false"` and `"0"`, plus the boolean `False`, are accepted for the two Boolean query parameters.

- [ ] **Step 3: Run the focused view tests and verify they fail**

Run:

```bash
pytest -q gcloud/tests/core/apis/drf/views_set/test_task_instance_view.py -k "two_phase or task_name_search_without_count"
```

Expected: new tests fail because the guard and manager call are not wired; the existing name-search optimization test passes.

- [ ] **Step 4: Implement the narrow request guard and list branch**

Add a Boolean parser:

```python
@staticmethod
def _is_false_query_param(value):
    return value is False or str(value).lower() in {"false", "0"}
```

Add `_should_use_two_phase_unstarted_task_list` requiring project ID, false `pipeline_instance__is_started`, false `is_child_taskflow`, and the absence of `order_by`, `pipeline_instance__name__icontains`, `creator_or_executor`, and `task_instance_status`.

Inside the existing `without_count` branch, order the decisions as:

```python
if self._should_use_two_phase_unstarted_task_list(request):
    page = TaskFlowInstance.objects.fetch_unstarted_task_list_page_two_phase(
        queryset=queryset,
        limit=self.paginator.limit,
        offset=self.paginator.offset,
    )
elif self._should_ignore_primary_index_for_task_list(request):
    page = TaskFlowInstance.objects.fetch_task_list_page_ignore_primary_index(
        queryset=queryset,
        limit=self.paginator.limit,
        offset=self.paginator.offset,
    )
else:
    page = list(queryset[self.paginator.offset : self.paginator.offset + self.paginator.limit])
```

- [ ] **Step 5: Run the focused view tests**

Run:

```bash
pytest -q gcloud/tests/core/apis/drf/views_set/test_task_instance_view.py -k "two_phase or task_name_search_without_count"
```

Expected: all selected tests pass.

### Task 3: Verify response semantics and regressions

**Files:**
- Test: `gcloud/tests/core/apis/drf/views_set/test_task_instance_view.py`
- Test: `gcloud/tests/taskflow3/models/test_taskflow_instance_manager.py`

**Interfaces:**
- Consumes: the manager and view interfaces completed in Tasks 1 and 2.
- Produces: regression evidence that response semantics and unaffected query paths remain stable.

- [ ] **Step 1: Add an integration-style order and serialization test**

Create three unstarted pipeline/task pairs in the test database. Patch only the capability check to return `True` and patch phase-one cursor rows to descending task IDs. Call `/api/v3/taskflow/` with the target parameters and assert:

```python
assert [item["id"] for item in response.data["data"]["results"]] == expected_ids_desc
assert all(item["is_started"] is False for item in response.data["data"]["results"])
assert all(item["project"]["id"] == self.test_project.id for item in response.data["data"]["results"])
```

Assert the response continues to use `count == -1` for `without_count`.

- [ ] **Step 2: Add empty and fewer-than-limit cases**

Return `[]` and then 13 phase-one IDs; assert the endpoint does not issue a supplemental scan and returns exactly zero or 13 records in the requested order.

- [ ] **Step 3: Run the complete affected test files**

Run:

```bash
pytest -q \
  gcloud/tests/taskflow3/models/test_taskflow_instance_manager.py \
  gcloud/tests/core/apis/drf/views_set/test_task_instance_view.py
```

Expected: both files pass with no regressions.

- [ ] **Step 4: Run formatting and static checks on changed Python files**

Run:

```bash
pre-commit run --files \
  gcloud/taskflow3/models.py \
  gcloud/core/apis/drf/viewsets/taskflow.py \
  gcloud/tests/taskflow3/models/test_taskflow_instance_manager.py \
  gcloud/tests/core/apis/drf/views_set/test_task_instance_view.py
```

Expected: all configured hooks pass. If `pre-commit` is unavailable, run the repository's configured Python formatter and report the missing hook runner explicitly.

- [ ] **Step 5: Review the final diff and commit with the TAPD Bug**

Run:

```bash
git diff --check
git status --short
```

Expected: only the design, plan, two implementation files, and two test files belong to this task. Commit with `perf: 优化未执行任务列表查询 --bug=1010131351162150454`.
