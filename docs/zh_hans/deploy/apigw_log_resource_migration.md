# 日志网关接口路径迁移

## 适用场景

升级后端后，`sync_saas_apigw` 同步资源报 HTTP 400，提示以下资源名称已被占用：

- `get_task_node_log`
- `get_task_plugin_log`
- `system_get_task_node_log`
- `system_get_task_plugin_log`

先导出目标网关的资源配置，与当前发布版本的
`gcloud/apigw/management/commands/data/api-resources.yml` 对比。
只有确认现有资源仍使用下表中的旧路径时，才按本文迁移。
其他同名资源或不同路径冲突需要单独核对，不能直接覆盖。

资源同步按请求方法和路径匹配现有资源。旧资源与新配置的 `operationId` 相同，
但路径不同，因此导入新配置会被判定为创建同名资源。
修改仓库中的路径为旧格式无法解决后端路由和权限校验的兼容问题。

## 迁移前检查

1. 保存目标网关资源导出、当前已发布版本及环境、这 4 个资源的 ID 和已有授权。
2. 核对调用方，准备在请求路径中传入 `task_id` 和 `bk_biz_id`。
   `scope=cmdb_biz`（默认）表示 `bk_biz_id` 是 CMDB 业务 ID；
   `scope=project` 表示它是标准运维项目 ID，不能混用。
3. 普通接口现在要求用户认证，确认调用方传递有效用户身份；系统接口仍不要求用户认证。
   应用认证和应用资源权限校验继续开启，后端的任务、项目、节点归属校验仍然生效。
4. 协调后端和网关的发布时机：新资源路径必须对应已经支持新路径的后端。
   若当前后端尚未升级，只保存资源草稿，待后端就绪后再发布网关版本。

## 原地更新现有资源

在网关管理端打开现有资源进行编辑，保留 `operationId`、资源 ID 和已有授权，
修改请求路径与后端路径。以下 4 个资源的方法均保持 `GET`。

| operationId | 旧请求路径 | 新请求路径 |
| --- | --- | --- |
| `get_task_node_log` | `/get_task_node_log/` | `/get_task_node_log/{task_id}/{bk_biz_id}/` |
| `get_task_plugin_log` | `/get_task_plugin_log/` | `/get_task_plugin_log/{task_id}/{bk_biz_id}/` |
| `system_get_task_node_log` | `/system/get_task_node_log/` | `/system/get_task_node_log/{task_id}/{bk_biz_id}/` |
| `system_get_task_plugin_log` | `/system/get_task_plugin_log/` | `/system/get_task_plugin_log/{task_id}/{bk_biz_id}/` |

后端转发配置：

| 资源 | 新后端路径 |
| --- | --- |
| `get_task_node_log`、`system_get_task_node_log` | `/{env.api_sub_path}apigw/get_task_node_log/{task_id}/{bk_biz_id}/` |
| `get_task_plugin_log`、`system_get_task_plugin_log` | `/{env.api_sub_path}apigw/get_task_plugin_log/{task_id}/{bk_biz_id}/` |

两个普通接口的 `userVerifiedRequired` 从 `false` 改为 `true`；
两个 `system_` 接口保持 `false`。四者的 `appVerifiedRequired` 和
`resourcePermissionRequired` 均保持 `true`，`isPublic` 和 `allowApplyPermission` 均保持 `false`。

不要删除资源后重建，也不要通过改名或关闭权限校验绕过冲突。
不要把后端改为 `/inner/` 接口；内部接口有不同的调用与认证边界。
如果管理端无法原地编辑路径，先由网关管理员确认该版本支持的迁移方式。

## 重新同步和验收

1. 保存全部 4 个资源后，再次导出配置，核对方法、路径、名称、认证配置和资源 ID。
2. 在正确的应用运行环境中重新执行 `python manage.py sync_saas_apigw`，或重试部署。
   此命令会同步网关配置、资源、文档、发布版本和授权，应按环境发布流程执行。
3. 确认资源同步成功，后续文档同步、版本创建与发布、授权同步也执行成功。
   检查目标环境实际绑定的新版本及新增资源，不能仅以应用部署页面显示成功为依据。
4. 用有权限的调用方验证四个接口正常返回，并验证跨项目、无权限任务、
   不属于任务的节点请求被拒绝。使用 SDK 的调用方还需核对新版本参数和发布后的 SDK。

迁移草稿不会自动更新已经发布的网关版本，PR 合并也不会自动完成目标环境迁移。
回退时需配套回退后端、调用方和网关版本；只回退资源草稿不能改变已发布版本。

## 多租户部署不再初始化 ESB

多租户分支的发布初始化不再执行 `fetch_esb_public_key`，应用启动也不再通过旧 ESB 获取公钥。
因此不需要目标环境提供 `bk-esb` 网关或 ESB 公钥接口。

`bk-sops` 自身的 API Gateway 配置、资源、版本、授权和公钥同步仍必须成功。
保留 `bin/pre_release` 的 `set -e` 和正常数据库 `migrate`，相关失败仍会中止发布。
API Gateway 的上下文表和 JWT 验签仍在使用，不能随 ESB 初始化一起移除。

旧插件开发工具的系统列表、接口列表及 ESB 插件代码生成接口已移除；轻应用只使用 PaaS V3 实现。
此项清理不迁移旧版节点管理 `nodeman_create_task:legacy` 或其他自定义插件中的 ESB 调用。
