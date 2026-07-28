# APIGW Create Task Template Schemes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let APIGW `create_task` and `create_and_start_task` create tasks by execution scheme IDs returned from `get_template_schemes`.

**Architecture:** Add one shared APIGW node-selection resolver that converts `template_schemes_id` into `exclude_task_nodes_id`, while preserving existing direct node-selection behavior. Both task creation views call the resolver before their existing `create_pipeline_instance_exclude_task_nodes` path.

**Tech Stack:** Django views, jsonschema, `pipeline.models.TemplateScheme`, `PipelineTemplateWebPreviewer`, existing APIGW unittest-style tests, Markdown API docs, APIGW YAML resources.

---

## File Structure

- Create `gcloud/apigw/views/task_node_selector.py`: shared node-selection resolver and validation exception.
- Create `gcloud/tests/apigw/views/test_task_node_selector.py`: focused resolver unit tests.
- Modify `gcloud/apigw/views/create_task.py`: import resolver, set defaults, reject `pipeline_tree + template_schemes_id`, and use resolver for template-based creation.
- Modify `gcloud/apigw/views/create_and_start_task.py`: import resolver, set defaults, and use resolver.
- Modify `gcloud/apigw/schemas.py`: add `template_schemes_id` to both create-task schemas.
- Modify `gcloud/tests/apigw/views/test_create_task.py`: add APIGW behavior coverage for schemes and conflicts.
- Modify `gcloud/tests/apigw/views/test_create_and_start_task.py`: add APIGW behavior coverage for schemes and conflicts.
- Modify `docs/zh_hans/apidoc/create_task.md` and `docs/en/apidoc/create_task.md`: document `template_schemes_id`.
- Modify `docs/zh_hans/apidoc/create_and_start_task.md` and `docs/en/apidoc/create_and_start_task.md`: document `template_schemes_id`.
- Modify `gcloud/apigw/management/commands/data/api-resources.yml`: document `template_schemes_id` for `create_task`.
- Inspect `apigw/*.yaml` and `gcloud/apigw/management/commands/data/api-resources.yml`: find or add the `create_and_start_task` gateway resource, then document `template_schemes_id`.
- Regenerate `gcloud/apigw/docs/apigw-docs.tgz`.

## Task 1: Shared Node-Selection Resolver

**Files:**
- Create: `gcloud/apigw/views/task_node_selector.py`
- Create: `gcloud/tests/apigw/views/test_task_node_selector.py`

- [ ] **Step 1: Write failing resolver tests**

Create `gcloud/tests/apigw/views/test_task_node_selector.py`:

```python
# -*- coding: utf-8 -*-
from types import SimpleNamespace
from unittest import mock

from django.test import TestCase

from gcloud.apigw.views.task_node_selector import (
    TaskNodeSelectionValidationError,
    resolve_exclude_task_nodes_id,
)


class ResolveExcludeTaskNodesIdTestCase(TestCase):
    def setUp(self):
        self.template = SimpleNamespace(pipeline_template=SimpleNamespace(id=47))
        self.pipeline_tree = {
            "activities": {
                "node1": {"id": "node1", "optional": True},
                "node2": {"id": "node2", "optional": False},
                "node3": {"id": "node3", "optional": True},
            }
        }

    @mock.patch("gcloud.apigw.views.task_node_selector.PipelineTemplateWebPreviewer")
    @mock.patch("gcloud.apigw.views.task_node_selector.TemplateScheme")
    def test_resolve_with_template_schemes_id(self, mock_template_scheme, mock_previewer):
        mock_template_scheme.objects.filter.return_value = [
            SimpleNamespace(id=101, unique_id="47-1"),
            SimpleNamespace(id=102, unique_id="47-2"),
        ]
        mock_previewer.get_template_exclude_task_nodes_with_schemes.return_value = ["node3"]

        result = resolve_exclude_task_nodes_id(
            template=self.template,
            pipeline_tree=self.pipeline_tree,
            params={"template_schemes_id": ["47-1", "47-2"], "exclude_task_nodes_id": []},
            support_execute_task_nodes=True,
        )

        mock_template_scheme.objects.filter.assert_called_once_with(
            template_id=47, unique_id__in=["47-1", "47-2"]
        )
        mock_previewer.get_template_exclude_task_nodes_with_schemes.assert_called_once_with(
            self.pipeline_tree, [101, 102], check_schemes_exist=True
        )
        self.assertEqual(result, ["node3"])

    @mock.patch("gcloud.apigw.views.task_node_selector.TemplateScheme")
    def test_reject_unknown_template_scheme(self, mock_template_scheme):
        mock_template_scheme.objects.filter.return_value = [SimpleNamespace(id=101, unique_id="47-1")]

        with self.assertRaises(TaskNodeSelectionValidationError) as ctx:
            resolve_exclude_task_nodes_id(
                template=self.template,
                pipeline_tree=self.pipeline_tree,
                params={"template_schemes_id": ["47-1", "47-missing"], "exclude_task_nodes_id": []},
                support_execute_task_nodes=True,
            )

        self.assertIn("47-missing", str(ctx.exception))

    def test_reject_scheme_and_exclude_nodes_together(self):
        with self.assertRaises(TaskNodeSelectionValidationError):
            resolve_exclude_task_nodes_id(
                template=self.template,
                pipeline_tree=self.pipeline_tree,
                params={"template_schemes_id": ["47-1"], "exclude_task_nodes_id": ["node3"]},
                support_execute_task_nodes=True,
            )

    def test_execute_task_nodes_keep_legacy_priority(self):
        result = resolve_exclude_task_nodes_id(
            template=self.template,
            pipeline_tree=self.pipeline_tree,
            params={
                "template_schemes_id": [],
                "exclude_task_nodes_id": ["node3"],
                "execute_task_nodes_id": ["node1"],
            },
            support_execute_task_nodes=True,
        )

        self.assertEqual(result, {"node2", "node3"})
```

- [ ] **Step 2: Run resolver tests and verify they fail**

Run:

```bash
python -m pytest gcloud/tests/apigw/views/test_task_node_selector.py -v
```

Expected: FAIL with `ModuleNotFoundError` or import error because `gcloud.apigw.views.task_node_selector` does not exist yet.

- [ ] **Step 3: Implement the shared resolver**

Create `gcloud/apigw/views/task_node_selector.py`:

```python
# -*- coding: utf-8 -*-
from pipeline.core.constants import PE
from pipeline.models import TemplateScheme

from pipeline_web.preview_base import PipelineTemplateWebPreviewer


class TaskNodeSelectionValidationError(Exception):
    pass


def get_exclude_nodes_by_execute_nodes(execute_nodes, pipeline_tree):
    all_nodes = set()
    for aid in pipeline_tree[PE.activities]:
        all_nodes.add(aid)
    execute_nodes = set(execute_nodes).intersection(all_nodes)
    return all_nodes - execute_nodes


def _resolve_template_scheme_pks(template, scheme_unique_ids):
    schemes = TemplateScheme.objects.filter(
        template_id=template.pipeline_template.id,
        unique_id__in=scheme_unique_ids,
    )
    scheme_by_unique_id = {scheme.unique_id: scheme for scheme in schemes}
    missing_scheme_ids = set(scheme_unique_ids) - set(scheme_by_unique_id.keys())
    if missing_scheme_ids:
        raise TaskNodeSelectionValidationError(
            "template_schemes_id contains invalid scheme ids: {}".format(
                sorted(missing_scheme_ids)
            )
        )
    return [scheme_by_unique_id[scheme_unique_id].id for scheme_unique_id in scheme_unique_ids]


def resolve_exclude_task_nodes_id(
    template,
    pipeline_tree,
    params,
    support_execute_task_nodes=False,
):
    template_schemes_id = params.get("template_schemes_id", [])
    exclude_task_nodes_id = params.get("exclude_task_nodes_id", [])
    execute_task_nodes_id = params.get("execute_task_nodes_id", [])

    if isinstance(template_schemes_id, str):
        template_schemes_id = [template_schemes_id]
        params["template_schemes_id"] = template_schemes_id

    if template_schemes_id and (exclude_task_nodes_id or execute_task_nodes_id):
        raise TaskNodeSelectionValidationError(
            "template_schemes_id cannot be used with exclude_task_nodes_id or execute_task_nodes_id"
        )

    if template_schemes_id:
        if not isinstance(template_schemes_id, list):
            raise TaskNodeSelectionValidationError("template_schemes_id must be a list or string")
        scheme_pks = _resolve_template_scheme_pks(template, template_schemes_id)
        return PipelineTemplateWebPreviewer.get_template_exclude_task_nodes_with_schemes(
            pipeline_tree, scheme_pks, check_schemes_exist=True
        )

    if support_execute_task_nodes and execute_task_nodes_id:
        return get_exclude_nodes_by_execute_nodes(execute_task_nodes_id, pipeline_tree)

    return exclude_task_nodes_id
```

- [ ] **Step 4: Run resolver tests and verify they pass**

Run:

```bash
python -m pytest gcloud/tests/apigw/views/test_task_node_selector.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit resolver**

Run:

```bash
git add gcloud/apigw/views/task_node_selector.py gcloud/tests/apigw/views/test_task_node_selector.py
git commit -m "feat: 增加任务节点选择解析器 --story=134672928"
```

Expected: commit succeeds. If pre-commit fails because `python3.6` is unavailable, stop and fix the local hook environment before committing implementation code.

## Task 2: Integrate `create_task`

**Files:**
- Modify: `gcloud/apigw/views/create_task.py`
- Modify: `gcloud/apigw/schemas.py`
- Modify: `gcloud/tests/apigw/views/test_create_task.py`

- [ ] **Step 1: Write failing `create_task` scheme success test**

Append this test method to `CreateTaskAPITest` in `gcloud/tests/apigw/views/test_create_task.py`:

```python
    @mock.patch(
        "gcloud.apigw.views.create_task.resolve_exclude_task_nodes_id",
        MagicMock(return_value=["node_from_scheme"]),
    )
    @mock.patch(TASKINSTANCE_CREATE_PIPELINE, MagicMock(return_value=TEST_DATA))
    @mock.patch(TASKINSTANCE_CREATE, MagicMock(return_value=MockTaskFlowInstance(id=TEST_TASKFLOW_ID)))
    @mock.patch(APIGW_CREATE_TASK_VALIDATE_WEB_PIPELINE_TREE, MagicMock())
    @mock.patch(APIGW_CREATE_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    def test_create_task__success_with_template_schemes_id(self):
        pt1 = MockPipelineTemplate(id=1, name="pt1")
        tmpl = MockTaskTemplate(id=1, pipeline_template=pt1)
        proj = MockProject(
            project_id=TEST_PROJECT_ID,
            name=TEST_PROJECT_NAME,
            bk_biz_id=TEST_BIZ_CC_ID,
            from_cmdb=True,
        )

        with mock.patch(PROJECT_GET, MagicMock(return_value=proj)):
            with mock.patch(TASKTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl))):
                response = self.client.post(
                    path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                    data=json.dumps(
                        {
                            "name": "name",
                            "constants": {},
                            "template_schemes_id": ["1-方案A"],
                            "flow_type": "common",
                        }
                    ),
                    content_type="application/json",
                    HTTP_BK_APP_CODE=TEST_APP_CODE,
                    HTTP_BK_USERNAME=TEST_USERNAME,
                )

        data = json.loads(response.content)
        self.assertTrue(data["result"], msg=data)
        create_task.resolve_exclude_task_nodes_id.assert_called_once_with(
            template=tmpl,
            pipeline_tree=tmpl.pipeline_tree,
            params=mock.ANY,
            support_execute_task_nodes=True,
        )
        TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes.assert_called_once_with(
            tmpl,
            {"name": "name", "creator": TEST_USERNAME, "description": ""},
            {},
            ["node_from_scheme"],
            [],
            tmpl.pipeline_tree,
        )
```

- [ ] **Step 2: Write failing `pipeline_tree + template_schemes_id` conflict test**

Append this test method to `CreateTaskAPITest`:

```python
    @mock.patch(APIGW_CREATE_TASK_VALIDATE_WEB_PIPELINE_TREE, MagicMock())
    @mock.patch(APIGW_CREATE_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    def test_create_task__reject_pipeline_tree_with_template_schemes_id(self):
        pt1 = MockPipelineTemplate(id=1, name="pt1")
        tmpl = MockTaskTemplate(id=1, pipeline_template=pt1)
        proj = MockProject(
            project_id=TEST_PROJECT_ID,
            name=TEST_PROJECT_NAME,
            bk_biz_id=TEST_BIZ_CC_ID,
            from_cmdb=True,
        )

        with mock.patch(PROJECT_GET, MagicMock(return_value=proj)):
            with mock.patch(TASKTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl))):
                response = self.client.post(
                    path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                    data=json.dumps(
                        {
                            "name": "name",
                            "constants": {},
                            "pipeline_tree": TEST_PIPELINE_TREE,
                            "template_schemes_id": ["1-方案A"],
                        }
                    ),
                    content_type="application/json",
                    HTTP_BK_APP_CODE=TEST_APP_CODE,
                    HTTP_BK_USERNAME=TEST_USERNAME,
                )

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)
        self.assertIn("template_schemes_id", data["message"])
```

- [ ] **Step 3: Run the new `create_task` tests and verify they fail**

Run:

```bash
python -m pytest \
  gcloud/tests/apigw/views/test_create_task.py::CreateTaskAPITest::test_create_task__success_with_template_schemes_id \
  gcloud/tests/apigw/views/test_create_task.py::CreateTaskAPITest::test_create_task__reject_pipeline_tree_with_template_schemes_id \
  -v
```

Expected: FAIL because `create_task.resolve_exclude_task_nodes_id` is not imported and `pipeline_tree + template_schemes_id` is not rejected.

- [ ] **Step 4: Update schema**

Modify `APIGW_CREATE_TASK_PARAMS` in `gcloud/apigw/schemas.py`:

```python
        "template_schemes_id": {
            "oneOf": [
                TEMPLATE_SCHEME_ID,
                {"type": "array", "items": TEMPLATE_SCHEME_ID},
            ]
        },
```

Place it next to `exclude_task_nodes_id` and `execute_task_nodes_id`.

- [ ] **Step 5: Update `create_task` imports**

Modify `gcloud/apigw/views/create_task.py` imports:

```python
from gcloud.apigw.views.task_node_selector import (
    TaskNodeSelectionValidationError,
    resolve_exclude_task_nodes_id,
)
```

Remove the local `get_exclude_nodes_by_execute_nodes` function from `create_task.py` after this import is added.

- [ ] **Step 6: Update `create_task` defaults and conflict handling**

In `create_task`, add the default:

```python
        params.setdefault("template_schemes_id", [])
```

Right after `create_with_tree = "pipeline_tree" in params`, add:

```python
    if create_with_tree and params["template_schemes_id"]:
        return {
            "result": False,
            "message": "template_schemes_id cannot be used with pipeline_tree",
            "code": err_code.REQUEST_PARAM_INVALID.code,
        }
```

- [ ] **Step 7: Replace local node-selection logic**

Replace the current `execute_task_nodes_id` / `exclude_task_nodes_id` block in the non-`pipeline_tree` branch with:

```python
        try:
            exclude_task_nodes_id = resolve_exclude_task_nodes_id(
                template=tmpl,
                pipeline_tree=pipeline_tree,
                params=params,
                support_execute_task_nodes=True,
            )
        except TaskNodeSelectionValidationError as e:
            return {"result": False, "message": str(e), "code": err_code.REQUEST_PARAM_INVALID.code}
```

Keep the existing `create_pipeline_instance_exclude_task_nodes` call unchanged except that it now receives the resolver output.

- [ ] **Step 8: Run targeted `create_task` tests**

Run:

```bash
python -m pytest \
  gcloud/tests/apigw/views/test_create_task.py::CreateTaskAPITest::test_create_task__success \
  gcloud/tests/apigw/views/test_create_task.py::CreateTaskAPITest::test_create_task__success_with_template_schemes_id \
  gcloud/tests/apigw/views/test_create_task.py::CreateTaskAPITest::test_create_task__reject_pipeline_tree_with_template_schemes_id \
  gcloud/tests/apigw/views/test_create_task.py::CreateTaskAPITest::test_create_task_success_with_execute_task_nodes \
  -v
```

Expected: PASS.

- [ ] **Step 9: Commit `create_task` integration**

Run:

```bash
git add gcloud/apigw/views/create_task.py gcloud/apigw/schemas.py gcloud/tests/apigw/views/test_create_task.py
git commit -m "feat: create_task支持执行方案创建任务 --story=134672928"
```

Expected: commit succeeds.

## Task 3: Integrate `create_and_start_task`

**Files:**
- Modify: `gcloud/apigw/views/create_and_start_task.py`
- Modify: `gcloud/apigw/schemas.py`
- Modify: `gcloud/tests/apigw/views/test_create_and_start_task.py`

- [ ] **Step 1: Write failing `create_and_start_task` scheme success test**

Add `from gcloud.apigw.views import create_and_start_task` near the imports in `gcloud/tests/apigw/views/test_create_and_start_task.py`.

Append this method to `CreateAndStartTaskAPITest`:

```python
    @mock.patch(
        "gcloud.apigw.views.create_and_start_task.resolve_exclude_task_nodes_id",
        MagicMock(return_value=["node_from_scheme"]),
    )
    @mock.patch(TASKINSTANCE_CREATE_PIPELINE, MagicMock(return_value=TEST_DATA))
    @mock.patch(TASKINSTANCE_CREATE, MagicMock(return_value=MockTaskFlowInstance(id=TEST_TASKFLOW_ID)))
    @mock.patch(APIGW_CREATE_ADN_STATRT_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    def test_create_and_start_task__success_with_template_schemes_id(self):
        pt = MockPipelineTemplate(id=1, name="pt")
        tmpl = MockCommonTemplate(id=1, pipeline_template=pt)
        proj = MockProject(
            project_id=TEST_PROJECT_ID,
            name=TEST_PROJECT_NAME,
            bk_biz_id=TEST_BIZ_CC_ID,
            from_cmdb=True,
        )
        prepare_and_start_task = MagicMock()

        with mock.patch(PROJECT_GET, MagicMock(return_value=proj)):
            with mock.patch(COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl))):
                with mock.patch(APIGW_CREATE_AND_START_TASK_PREPARE_AND_START_TASK, prepare_and_start_task):
                    response = self.client.post(
                        path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                        data=json.dumps(
                            {
                                "name": "name",
                                "constants": {},
                                "template_source": "common",
                                "flow_type": "common",
                                "template_schemes_id": ["1-方案A"],
                            }
                        ),
                        content_type="application/json",
                        HTTP_BK_APP_CODE=TEST_APP_CODE,
                    )

        data = json.loads(response.content)
        self.assertTrue(data["result"], msg=data)
        create_and_start_task.resolve_exclude_task_nodes_id.assert_called_once_with(
            template=tmpl,
            pipeline_tree=tmpl.pipeline_tree,
            params=mock.ANY,
            support_execute_task_nodes=False,
        )
        TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes.assert_called_once_with(
            tmpl,
            {"name": "name", "creator": "", "description": ""},
            {},
            ["node_from_scheme"],
        )
        prepare_and_start_task.apply_async.assert_called_once()
```

- [ ] **Step 2: Write failing conflict test**

Append this method to `CreateAndStartTaskAPITest`:

```python
    @mock.patch(APIGW_CREATE_ADN_STATRT_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    def test_create_and_start_task__reject_template_schemes_with_exclude_nodes(self):
        pt = MockPipelineTemplate(id=1, name="pt")
        tmpl = MockCommonTemplate(id=1, pipeline_template=pt)
        proj = MockProject(
            project_id=TEST_PROJECT_ID,
            name=TEST_PROJECT_NAME,
            bk_biz_id=TEST_BIZ_CC_ID,
            from_cmdb=True,
        )

        with mock.patch(PROJECT_GET, MagicMock(return_value=proj)):
            with mock.patch(COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl))):
                response = self.client.post(
                    path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
                    data=json.dumps(
                        {
                            "name": "name",
                            "constants": {},
                            "template_source": "common",
                            "template_schemes_id": ["1-方案A"],
                            "exclude_task_nodes_id": ["node1"],
                        }
                    ),
                    content_type="application/json",
                    HTTP_BK_APP_CODE=TEST_APP_CODE,
                )

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertIn("template_schemes_id", data["message"])
```

- [ ] **Step 3: Run new `create_and_start_task` tests and verify they fail**

Run:

```bash
python -m pytest \
  gcloud/tests/apigw/views/test_create_and_start_task.py::CreateAndStartTaskAPITest::test_create_and_start_task__success_with_template_schemes_id \
  gcloud/tests/apigw/views/test_create_and_start_task.py::CreateAndStartTaskAPITest::test_create_and_start_task__reject_template_schemes_with_exclude_nodes \
  -v
```

Expected: FAIL because the view does not import or call the resolver.

- [ ] **Step 4: Update schema**

Modify `APIGW_CREATE_AND_START_TASK_PARAMS` in `gcloud/apigw/schemas.py`:

```python
        "template_schemes_id": {
            "oneOf": [
                TEMPLATE_SCHEME_ID,
                {"type": "array", "items": TEMPLATE_SCHEME_ID},
            ]
        },
```

Place it next to `exclude_task_nodes_id`.

- [ ] **Step 5: Update `create_and_start_task` imports**

Modify `gcloud/apigw/views/create_and_start_task.py` imports:

```python
from gcloud.apigw.views.task_node_selector import (
    TaskNodeSelectionValidationError,
    resolve_exclude_task_nodes_id,
)
```

- [ ] **Step 6: Update defaults and resolver call**

Add the default:

```python
        params.setdefault("template_schemes_id", [])
```

Before `create_pipeline_instance_exclude_task_nodes`, add:

```python
    pipeline_tree = tmpl.pipeline_tree
    try:
        exclude_task_nodes_id = resolve_exclude_task_nodes_id(
            template=tmpl,
            pipeline_tree=pipeline_tree,
            params=params,
            support_execute_task_nodes=False,
        )
    except TaskNodeSelectionValidationError as e:
        return {"result": False, "message": str(e), "code": err_code.REQUEST_PARAM_INVALID.code}
```

Then change the create call to:

```python
        data = TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes(
            tmpl, pipeline_instance_kwargs, params["constants"], exclude_task_nodes_id
        )
```

- [ ] **Step 7: Run targeted `create_and_start_task` tests**

Run:

```bash
python -m pytest \
  gcloud/tests/apigw/views/test_create_and_start_task.py::CreateAndStartTaskAPITest::test_create_and_start_task__success \
  gcloud/tests/apigw/views/test_create_and_start_task.py::CreateAndStartTaskAPITest::test_create_and_start_task__success_with_template_schemes_id \
  gcloud/tests/apigw/views/test_create_and_start_task.py::CreateAndStartTaskAPITest::test_create_and_start_task__reject_template_schemes_with_exclude_nodes \
  -v
```

Expected: PASS.

- [ ] **Step 8: Commit `create_and_start_task` integration**

Run:

```bash
git add gcloud/apigw/views/create_and_start_task.py gcloud/apigw/schemas.py gcloud/tests/apigw/views/test_create_and_start_task.py
git commit -m "feat: create_and_start_task支持执行方案创建任务 --story=134672928"
```

Expected: commit succeeds.

## Task 4: API Docs, Gateway Resources, And Docs Package

**Files:**
- Modify: `docs/zh_hans/apidoc/create_task.md`
- Modify: `docs/en/apidoc/create_task.md`
- Modify: `docs/zh_hans/apidoc/create_and_start_task.md`
- Modify: `docs/en/apidoc/create_and_start_task.md`
- Modify: `gcloud/apigw/management/commands/data/api-resources.yml`
- Possibly modify: `apigw/*.yaml`
- Modify: `gcloud/apigw/docs/apigw-docs.tgz`

- [ ] **Step 1: Update `create_task` docs**

In `docs/zh_hans/apidoc/create_task.md`, add this parameter row after `exclude_task_nodes_id`:

```markdown
|   template_schemes_id | list/string/integer |   否   | 执行方案 ID 列表或单个执行方案 ID，支持 get_template_schemes 返回的字符串 ID 和执行方案整型 ID；与 exclude_task_nodes_id、execute_task_nodes_id 同时存在非空值时会返回参数错误 |
```

In `docs/en/apidoc/create_task.md`, add this parameter row after `exclude_task_nodes_id`:

```markdown
| template_schemes_id | list/string/integer | NO | execution scheme ID list or single execution scheme ID. Supports string IDs returned by get_template_schemes and integer TemplateScheme IDs. It cannot be used together with non-empty exclude_task_nodes_id or execute_task_nodes_id |
```

Add `"template_schemes_id": ["1-方案A"]` to both request examples.

- [ ] **Step 2: Update `create_and_start_task` docs**

In `docs/zh_hans/apidoc/create_and_start_task.md`, add this parameter row after `exclude_task_nodes_id`:

```markdown
|   template_schemes_id | list/string/integer | 否 | 执行方案 ID 列表或单个执行方案 ID，支持 get_template_schemes 返回的字符串 ID 和执行方案整型 ID；与 exclude_task_nodes_id 同时存在非空值时会返回参数错误 |
```

In `docs/en/apidoc/create_and_start_task.md`, add this parameter row after `exclude_task_nodes_id`:

```markdown
| template_schemes_id | list/string/integer | NO | execution scheme ID list or single execution scheme ID. Supports string IDs returned by get_template_schemes and integer TemplateScheme IDs. It cannot be used together with non-empty exclude_task_nodes_id |
```

Add `"template_schemes_id": ["1-方案A"]` to both request examples.

- [ ] **Step 3: Update `create_task` resource schema**

In `gcloud/apigw/management/commands/data/api-resources.yml`, under `/create_task/{template_id}/{bk_biz_id}/` request body properties, add:

```yaml
                template_schemes_id:
                  oneOf:
                  - type: string
                    minLength: 1
                  - type: integer
                    minimum: 1
                  - type: array
                    items:
                      oneOf:
                      - type: string
                        minLength: 1
                      - type: integer
                        minimum: 1
                  description: 执行方案ID列表或单个执行方案ID，支持get_template_schemes返回的字符串ID和执行方案整型ID；与exclude_task_nodes_id、execute_task_nodes_id同时存在非空值时会返回参数错误
```

- [ ] **Step 4: Locate or add `create_and_start_task` resource schema**

Run:

```bash
rg -n "create_and_start_task" apigw gcloud/apigw/management/commands/data/api-resources.yml
```

Expected before editing in the current checkout: no resource is found.

If a resource is found, add:

```yaml
                template_schemes_id:
                  oneOf:
                  - type: string
                    minLength: 1
                  - type: integer
                    minimum: 1
                  - type: array
                    items:
                      oneOf:
                      - type: string
                        minLength: 1
                      - type: integer
                        minimum: 1
                  description: 执行方案ID列表或单个执行方案ID，支持get_template_schemes返回的字符串ID和执行方案整型ID；与exclude_task_nodes_id同时存在非空值时会返回参数错误
```

If no resource is found, add the missing `create_and_start_task` resource to `gcloud/apigw/management/commands/data/api-resources.yml`. Place it near the other task operation resources with this structure:

```yaml
  /create_and_start_task/{template_id}/{bk_biz_id}/:
    post:
      operationId: create_and_start_task
      description: 通过业务流程模板创建并开始执行任务
      tags:
      - 通用接口
      responses:
        '200':
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                    description: 错误码
                  data:
                    type: object
                    properties:
                      task_id:
                        type: integer
                        description: 任务实例ID
                      task_url:
                        type: string
                        description: 任务实例链接
                      pipeline_tree:
                        type: object
                        description: 任务实例树
                  result:
                    type: boolean
                    description: true/false 操作是否成功
                  message:
                    type: string
                    description: result=false 时错误信息
                  trace_id:
                    type: string
                    description: open telemetry trace_id
      parameters:
      - in: path
        name: template_id
        schema:
          type: string
        required: true
        description: 模板ID
      - in: path
        name: bk_biz_id
        schema:
          type: string
        required: true
        description: 模板所属业务ID
      - in: query
        name: scope
        schema:
          type: string
          default: cmdb_biz
        required: false
        description: bk_biz_id 检索的作用域
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
              - name
              properties:
                name:
                  type: string
                  description: 任务名称
                constants:
                  type: object
                  description: 任务全局参数
                  additionalProperties: true
                flow_type:
                  type: string
                  default: common
                  description: '任务流程类型，common: 常规流程，common_func：职能化流程'
                description:
                  type: string
                  description: 任务描述
                template_source:
                  type: string
                  default: business
                  description: 流程模板来源，business:业务流程，common：公共流程
                exclude_task_nodes_id:
                  type: array
                  items:
                    type: string
                  description: 跳过执行的节点ID列表
                template_schemes_id:
                  type: array
                  items:
                    type: string
                  description: 执行方案ID列表，ID来源于get_template_schemes接口；与exclude_task_nodes_id同时存在非空值时会返回参数错误
        required: true
        description: ''
      x-bk-apigateway-resource:
        isPublic: true
        allowApplyPermission: true
        matchSubpath: false
        backend:
          type: HTTP
          method: post
          path: /{env.api_sub_path}apigw/create_and_start_task/{template_id}/{bk_biz_id}/
          matchSubpath: false
          timeout: 0
          upstreams: {}
          transformHeaders: {}
        authConfig:
          userVerifiedRequired: true
        disabledStages: []
```

- [ ] **Step 5: Validate YAML**

Run:

```bash
python3 -c "import yaml; yaml.safe_load(open('gcloud/apigw/management/commands/data/api-resources.yml')); print('YAML is valid')"
```

Expected: `YAML is valid`.

If an `apigw/*.yaml` file was modified, run the same command against that file.

- [ ] **Step 6: Regenerate APIGW docs package**

Run:

```bash
tmpdir=$(mktemp -d)
mkdir -p "$tmpdir/zh" "$tmpdir/en"
cp docs/zh_hans/apidoc/*.md "$tmpdir/zh/"
cp docs/en/apidoc/*.md "$tmpdir/en/"
tar -czf gcloud/apigw/docs/apigw-docs.tgz -C "$tmpdir" zh en
rm -rf "$tmpdir"
```

Expected: `gcloud/apigw/docs/apigw-docs.tgz` is updated.

- [ ] **Step 7: Commit docs and resources**

Run:

```bash
git add \
  docs/zh_hans/apidoc/create_task.md \
  docs/en/apidoc/create_task.md \
  docs/zh_hans/apidoc/create_and_start_task.md \
  docs/en/apidoc/create_and_start_task.md \
  gcloud/apigw/management/commands/data/api-resources.yml \
  gcloud/apigw/docs/apigw-docs.tgz
git add apigw/*.yaml
git commit -m "docs: 补充执行方案创建任务网关文档 --story=134672928"
```

Expected: commit succeeds. If `git add apigw/*.yaml` finds no modified file, it may print nothing and the commit should still proceed.

## Task 5: Final Verification

**Files:**
- No new files.

- [ ] **Step 1: Run focused tests**

Run:

```bash
python -m pytest \
  gcloud/tests/apigw/views/test_task_node_selector.py \
  gcloud/tests/apigw/views/test_create_task.py::CreateTaskAPITest::test_create_task__success \
  gcloud/tests/apigw/views/test_create_task.py::CreateTaskAPITest::test_create_task__success_with_template_schemes_id \
  gcloud/tests/apigw/views/test_create_task.py::CreateTaskAPITest::test_create_task__reject_pipeline_tree_with_template_schemes_id \
  gcloud/tests/apigw/views/test_create_task.py::CreateTaskAPITest::test_create_task_success_with_execute_task_nodes \
  gcloud/tests/apigw/views/test_create_and_start_task.py::CreateAndStartTaskAPITest::test_create_and_start_task__success \
  gcloud/tests/apigw/views/test_create_and_start_task.py::CreateAndStartTaskAPITest::test_create_and_start_task__success_with_template_schemes_id \
  gcloud/tests/apigw/views/test_create_and_start_task.py::CreateAndStartTaskAPITest::test_create_and_start_task__reject_template_schemes_with_exclude_nodes \
  -v
```

Expected: PASS.

- [ ] **Step 2: Run schema and docs checks**

Run:

```bash
python3 -c "import yaml; yaml.safe_load(open('gcloud/apigw/management/commands/data/api-resources.yml')); print('YAML is valid')"
tar -tzf gcloud/apigw/docs/apigw-docs.tgz | head
```

Expected:

```text
YAML is valid
zh/
```

The tar output should include `zh/create_task.md`, `zh/create_and_start_task.md`, `en/create_task.md`, and `en/create_and_start_task.md`.

- [ ] **Step 3: Inspect final diff**

Run:

```bash
git status --short
git log --oneline -5
git diff upstream/master...HEAD --stat
```

Expected:

- `git status --short` shows no unstaged intended files.
- Recent commits include the design commit and implementation commits with `--story=134672928`.
- Diff stat only includes files named in this plan, plus any confirmed owning gateway resource file for `create_and_start_task`.

- [ ] **Step 4: Push branch**

Run:

```bash
git push -u origin feat/apigw-task-template-schemes
```

Expected: branch is pushed to the user's fork.
