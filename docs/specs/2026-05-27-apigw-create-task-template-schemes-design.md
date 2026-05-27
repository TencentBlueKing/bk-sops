# APIGW Create Task Template Schemes Design

## Context

The APIGW `create_task` interface currently supports selecting task nodes by `exclude_task_nodes_id` and, for `create_task` only, `execute_task_nodes_id`. It does not accept execution scheme IDs directly.

Execution schemes already exist in the product and in nearby APIs:

- `get_template_schemes` exposes scheme IDs to APIGW callers.
- `preview_task_tree_with_schemes` and template form APIs accept scheme IDs and preview a pruned pipeline tree.
- `create_clocked_task` accepts `task_parameters.template_schemes_id` for scheduled task creation.

The new capability should let both APIGW task creation interfaces create tasks from execution schemes while keeping node-selection behavior in one shared code path.

## Goals

- Add execution scheme support to `create_task`.
- Add execution scheme support to `create_and_start_task`.
- Reuse one node-selection resolver across both interfaces.
- Keep existing `exclude_task_nodes_id` and `execute_task_nodes_id` behavior backward compatible.
- Align external scheme IDs with the IDs returned by `get_template_schemes`.
- Return clear parameter errors when callers mix incompatible node-selection methods.
- Update tests, API docs, gateway resource schema, and the APIGW docs package.

## Non-Goals

- Do not change execution scheme management APIs.
- Do not change the internal pipeline preview algorithm.
- Do not add execution scheme support to periodic or clocked task APIs beyond their existing behavior.
- Do not support combining execution schemes with caller-provided `pipeline_tree`.

## API Contract

Both `create_task` and `create_and_start_task` will accept a new optional request body field:

```json
{
  "template_schemes_id": ["47-1", "47-2"]
}
```

`template_schemes_id` accepts either a list of execution scheme unique IDs or one scheme unique ID string returned by `get_template_schemes`. A single string is normalized to a single-item list before node selection.

The field name intentionally matches the existing `create_clocked_task` parameter instead of the DRF preview API's `scheme_id_list`, because these are APIGW-facing create-task APIs.

## Node Selection Rules

The interfaces support these node-selection methods:

- `template_schemes_id`: create the task using one or more execution schemes.
- `exclude_task_nodes_id`: create the task while skipping the given optional nodes.
- `execute_task_nodes_id`: create the task with only the given nodes selected. This remains supported by `create_task` only.

Only one node-selection method may be non-empty in one request.

When `template_schemes_id` is provided together with `exclude_task_nodes_id` or `execute_task_nodes_id`, the API returns `REQUEST_PARAM_INVALID`.

For `create_task`, the existing priority of `execute_task_nodes_id` over `exclude_task_nodes_id` is preserved for legacy calls that do not use `template_schemes_id`. The new conflict validation only applies when multiple node-selection methods are non-empty.

For `create_and_start_task`, `execute_task_nodes_id` remains unsupported unless a separate product decision adds it later.

When `pipeline_tree` is provided to `create_task`, `template_schemes_id` is invalid. A caller-provided tree is already the concrete task definition, so combining it with template-level execution schemes would be ambiguous.

## Shared Resolver

Add a shared APIGW helper, for example `gcloud/apigw/views/task_node_selector.py`, with a focused API such as:

```python
def resolve_exclude_task_nodes_id(
    template,
    pipeline_tree,
    params,
    support_execute_task_nodes=False,
):
    ...
```

Responsibilities:

- Read `template_schemes_id`, `exclude_task_nodes_id`, and optionally `execute_task_nodes_id`.
- Validate that no incompatible node-selection methods are mixed.
- Validate that `template_schemes_id` is either a list or a non-empty string.
- Normalize a string `template_schemes_id` into a single-item list.
- Resolve scheme unique IDs against the current template's `pipeline_template.id`.
- Fail if any requested scheme does not exist or belongs to another template.
- Convert the resolved scheme records to an `exclude_task_nodes_id` list by reusing `PipelineTemplateWebPreviewer.get_template_exclude_task_nodes_with_schemes`.
- Convert `execute_task_nodes_id` to `exclude_task_nodes_id` using the existing `get_exclude_nodes_by_execute_nodes` behavior for `create_task`.
- Return the final `exclude_task_nodes_id` list and let callers continue through the existing `create_pipeline_instance_exclude_task_nodes` path.

The resolver should raise a narrow validation exception or return a structured error that each view maps to:

```json
{
  "result": false,
  "code": REQUEST_PARAM_INVALID,
  "message": "..."
}
```

## Scheme ID Semantics

`get_template_schemes` returns `TemplateScheme.unique_id` as `id`. The new create-task fields must use those same values.

The resolver should query schemes by:

- `template_id=template.pipeline_template.id`
- `unique_id__in=params["template_schemes_id"]`

It should not expose or require database primary keys. The existing preview helper consumes database primary keys, so the resolver will map unique IDs to primary keys before calling that helper.

## Integration Points

### `create_task`

Add defaults for `template_schemes_id` after request validation setup.

When `pipeline_tree` is not provided, replace the local `execute_task_nodes_id` / `exclude_task_nodes_id` decision with the shared resolver:

- pass `support_execute_task_nodes=True`
- pass the template pipeline tree
- pass params

When `pipeline_tree` is provided and `template_schemes_id` is non-empty, return `REQUEST_PARAM_INVALID`.

### `create_and_start_task`

Add defaults for `template_schemes_id`.

Before calling `create_pipeline_instance_exclude_task_nodes`, call the shared resolver:

- pass `support_execute_task_nodes=False`
- pass the template pipeline tree
- pass params

Use the returned `exclude_task_nodes_id` in the existing task creation path, then keep the current async start behavior unchanged.

## Validation And Error Handling

Return `REQUEST_PARAM_INVALID` for:

- `template_schemes_id` is neither a list nor a non-empty string.
- `template_schemes_id` contains unknown scheme IDs.
- `template_schemes_id` contains schemes from another template.
- `template_schemes_id` is combined with non-empty `exclude_task_nodes_id`.
- `template_schemes_id` is combined with non-empty `execute_task_nodes_id`.
- `create_task` receives both `pipeline_tree` and non-empty `template_schemes_id`.

Keep existing `UNKNOWN_ERROR` behavior for unexpected pipeline preview or pipeline instance creation errors.

## Tests

Add focused unit tests for the resolver:

- Resolves scheme unique IDs to excluded optional nodes.
- Rejects unknown scheme IDs.
- Rejects mixed node-selection methods.
- Preserves non-optional nodes through the existing previewer behavior.

Add APIGW view tests:

- `create_task` succeeds with `template_schemes_id`.
- `create_task` rejects `template_schemes_id` plus `exclude_task_nodes_id`.
- `create_task` rejects `template_schemes_id` plus `execute_task_nodes_id`.
- `create_task` rejects `template_schemes_id` plus `pipeline_tree`.
- `create_task` legacy `execute_task_nodes_id` behavior still works.
- `create_and_start_task` succeeds with `template_schemes_id`.
- `create_and_start_task` rejects mixed node-selection methods.
- `create_and_start_task` keeps dispatching `prepare_and_start_task` after successful creation.

## Documentation And Gateway Resources

Update both Chinese and English API docs:

- `docs/zh_hans/apidoc/create_task.md`
- `docs/en/apidoc/create_task.md`
- `docs/zh_hans/apidoc/create_and_start_task.md`
- `docs/en/apidoc/create_and_start_task.md`

Update gateway resource schema so `template_schemes_id` appears in request body for both APIs.

`create_task` is already present in `gcloud/apigw/management/commands/data/api-resources.yml`. `create_and_start_task` is registered in Django URLs and documented, but it is not currently present in that resource file. During implementation, search the repository gateway resource files for the owning `create_and_start_task` resource. If a resource exists, update that file. If no resource exists, add or supplement the resource according to the repository API change checklist.

Regenerate `gcloud/apigw/docs/apigw-docs.tgz` after APIGW docs change.

## Rollout

This is backward compatible for callers that do not send `template_schemes_id`.

The only newly rejected requests are ambiguous requests that combine execution schemes with another non-empty node-selection method, or with a caller-provided `pipeline_tree`.

## Implementation Checks

- Before editing gateway resources, confirm which file owns `create_and_start_task`; add or supplement it only if no existing resource is found.
- Preserve `create_task` legacy behavior when `exclude_task_nodes_id` and `execute_task_nodes_id` are both non-empty and `template_schemes_id` is empty. In that case, `execute_task_nodes_id` continues to take priority.
