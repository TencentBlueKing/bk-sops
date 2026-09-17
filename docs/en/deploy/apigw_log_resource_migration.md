# Migrating log API gateway paths

## When to use this guide

After a backend upgrade, `sync_saas_apigw` may fail with HTTP 400 because these
resource names are already in use:

- `get_task_node_log`
- `get_task_plugin_log`
- `system_get_task_node_log`
- `system_get_task_plugin_log`

Export the target gateway resources and compare them with
`gcloud/apigw/management/commands/data/api-resources.yml` from the release being
deployed. Use this procedure only when the existing resources have the old paths
listed below. Investigate other name or path conflicts separately.

Resource synchronization matches existing resources by HTTP method and path.
The old resources and the new definitions share an `operationId` but have different
paths, so importing the new definitions attempts to create duplicate names.
Reverting the repository paths would leave them incompatible with the current
backend routes and authorization checks.

## Before migrating

1. Save the resource export, the published gateway version and stage, and the IDs
   and existing grants of all four resources.
2. Update callers to supply `task_id` and `bk_biz_id` in the request path.
   With `scope=cmdb_biz` (the default), `bk_biz_id` is a CMDB business ID;
   with `scope=project`, it is a BK-SOPS project ID. Do not interchange these IDs.
3. The ordinary APIs now require user authentication. Prepare valid user
   credentials. The system APIs still do not require user authentication.
   Application authentication, resource permission checks, and backend checks
   binding the task, project and node remain enabled.
4. Coordinate backend and gateway releases. Publish the new gateway paths only
   when the backend supports them. If the backend has not been upgraded yet,
   save resource drafts and publish the gateway version after the backend is ready.

## Update existing resources in place

Edit the existing resources in the gateway management console, preserving their
`operationId`, resource IDs and grants. Update both request and backend paths.
All four resources keep the `GET` method.

| operationId | Old request path | New request path |
| --- | --- | --- |
| `get_task_node_log` | `/get_task_node_log/` | `/get_task_node_log/{task_id}/{bk_biz_id}/` |
| `get_task_plugin_log` | `/get_task_plugin_log/` | `/get_task_plugin_log/{task_id}/{bk_biz_id}/` |
| `system_get_task_node_log` | `/system/get_task_node_log/` | `/system/get_task_node_log/{task_id}/{bk_biz_id}/` |
| `system_get_task_plugin_log` | `/system/get_task_plugin_log/` | `/system/get_task_plugin_log/{task_id}/{bk_biz_id}/` |

Backend paths:

| Resources | New backend path |
| --- | --- |
| `get_task_node_log`, `system_get_task_node_log` | `/{env.api_sub_path}apigw/get_task_node_log/{task_id}/{bk_biz_id}/` |
| `get_task_plugin_log`, `system_get_task_plugin_log` | `/{env.api_sub_path}apigw/get_task_plugin_log/{task_id}/{bk_biz_id}/` |

Change `userVerifiedRequired` from `false` to `true` for the two ordinary APIs;
keep it `false` for the two `system_` APIs. For all four resources, keep
`appVerifiedRequired` and `resourcePermissionRequired` set to `true`, and
`isPublic` and `allowApplyPermission` set to `false`.

Do not delete and recreate resources, rename them to bypass conflicts, disable
authorization, or point their backends at `/inner/` APIs. Internal APIs have
different caller and authentication boundaries. If the console does not support
editing paths in place, ask the gateway administrator to confirm a migration
method supported by that gateway version.

## Synchronize and verify

1. After saving all four resources, export them again and verify their methods,
   paths, names, authentication settings and resource IDs.
2. Run `python manage.py sync_saas_apigw` in the correct application environment,
   or retry deployment. This command synchronizes gateway configuration,
   resources, documentation, the published version and grants; follow the
   environment's release procedure.
3. Confirm resource synchronization succeeds and the subsequent documentation,
   version creation, release and grant steps also succeed. Verify the version
   actually deployed to the target stage and its added resources. An application
   deployment marked successful is insufficient evidence.
4. Verify successful requests to all four APIs using authorized callers and
   rejection of cross-project tasks, unauthorized tasks and nodes outside the
   task. SDK callers must also check the new parameters and the published SDK.

Saving resource drafts does not update an already published gateway version,
and merging the PR does not migrate the target environment. Roll back the
backend, callers and gateway version together when necessary; reverting drafts
alone does not change the published version.

## Environments without ESB

`fetch_esb_public_key` retrieves the JWT verification key for the legacy ESB
entry point, not credentials for the JOB or CMDB gateway SDKs. Some PaaS V3
environments do not provide this entry point and return HTTP 404. Only a
confirmed HTTP 404 from this optional step is skipped, including when
apigw-manager wraps the HTTP error in `SystemExit(1)`.

Fetching the `bk-sops` gateway's own key remains mandatory. ESB authentication
failures, server errors, timeouts and unknown failures still stop deployment.
Keep `set -e` in `bin/pre_release`; do not ignore the entire synchronization
command's exit status. This handling does not migrate legacy ESB clients:
plugins or development tools requesting `/api/c/compapi/` still require a
supported endpoint in the target environment.
