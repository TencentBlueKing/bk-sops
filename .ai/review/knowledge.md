# bk-sops dev_multi_tenant 审查知识库

## 分支基线

- 核验日期：2026-09-09；目标 `dev_multi_tenant`；base SHA `2cfd1dc62cb520d4c2d16d592c2316eecf7cbf90`。这是独立维护分支的快照，不是 master 的能力清单。
- 运行时：`python-3.11.10`；依赖：`Django==4.2.30`、`bamboo-pipeline==4.0.4`、`celery==5.2.7`、`blueapps[opentelemetry,bkcrypto]==4.16.rc3`。
- 标准运维自身负责项目/模板/任务和应用层协议，执行语义还取决于锁定的 bamboo-pipeline/引擎；升级必须同时考虑历史任务、插件和部署环境。

## 本分支的新增能力边界

本分支有 `gcloud/plugin_gateway/`：catalog、form_schema/native_forms、execution、runner、callbacks/context 等服务，以及 `gcloud/apigw/views/plugin_gateway.py`。插件目录/表单元数据、执行、状态查询和 callback 是不同链路；需要跟踪 task/project、输入上下文、外部身份、持久化和异步恢复，不能把目录可列出等同于可以执行。对应测试在 `gcloud/tests/plugin_gateway/`，包括 runner/execution/callbacks/context/native_forms，不能只验证目录接口。

本分支存在 `mcp_apigw` 装饰器并用于部分 APIGW view，不存在独立 `gcloud/mcp/` 目录；MCP 转换、普通 APIGW 响应、认证用户及请求字段需要分开验证。没有根 `apigw/`，资源仍由 management/commands/data 下 YAML 发布。

中英文 API 文档在 `docs/zh_hans/apidoc/` 与 `docs/en/apidoc/`，设计与计划在 `docs/specs/`、`docs/plans/`。虽有 `.ai/rules/api-change-checklist.mdc`，其中提及的根 MCP YAML 路径并不存在；本次工作流直接载入分支专属 `.ai/review/knowledge.md`、`rules.md`，按实际源码/资源判断，避免旧提示误报。

多租户已经进入 `gcloud/core/models.py` 的 Project.tenant_id，CommonTemplate 查询、任务 project__tenant_id、IAM client/resource 构造使用 request.user.tenant_id。重点查 `gcloud/apigw/views/create_task.py`、`get_task_status.py`、`gcloud/iam_auth/view_interceptors/apigw/task_view.py`、`create_task.py` 与 `gcloud/iam_auth/res_factory.py`；模型有字段不代表所有接口、缓存/队列/回调/插件客户端已完成隔离。不要把非租户 humming_bird 分支的查询复制回来而丢掉 tenant 约束。

跨租户检查从认证用户租户开始，经过项目/模板归属、IAM、返回字段及异步上下文；公共模板与项目模板分别验证。多租户改动还需检查定时/周期任务、缓存 key、下游 SDK header 和迁移旧数据，不能用客户端自报 tenant_id 替代已认证身份。`gcloud/tests/iam_auth/` 与 `gcloud/tests/shortcuts/` 在此分支存在，但测试存在不等于完整租户隔离已验收。

本基线的 `gcloud/plugin_gateway/services/execution.py` 与 `gcloud/apigw/views/plugin_gateway.py` 已加入禁用功能时的错误分支，并有 `gcloud/tests/plugin_gateway/test_feature_switch.py`；不要将较早集成分支缺少该保护的状态套用到这里。`gcloud/apigw/docs/` 同时有 .tgz 和 .tar.gz，消费哪份应读 definition 配置，不凭文件存在判断已经同步。

## 源码职责与调用链

| 入口 | 审查关注点 |
| --- | --- |
| `gcloud/core/models.py` | Project、业务 ID、项目配置、引擎选择；项目主键与 CMDB 业务 ID 不是同一语义。 |
| `gcloud/tasktmpl3/models.py`、`gcloud/template_base/models.py`、`gcloud/common_template/models.py` | 项目/公共模板、变量和流程树、版本与引用；模板变更不等于已经创建的任务同时变更。 |
| `gcloud/taskflow3/models.py`、`gcloud/taskflow3/apis/`、`gcloud/taskflow3/domains/dispatchers/` | 任务记录、普通/职能化生命周期、引擎适配、任务/节点操作与状态；创建任务、启动执行、查询状态是不同动作。 |
| `gcloud/apigw/urls.py`、`decorators.py`、`schemas.py`、`validators/`、`views/` | 外部路由、网关用户/应用、白名单信任、scope/project 注入、请求校验、错误封装。 |
| `gcloud/iam_auth/view_interceptors/apigw/`、`gcloud/iam_auth/res_factory.py` | 按操作构建 IAM 用户、动作与任务/模板/项目资源；查看权不能直接代替编辑/执行权。 |
| `pipeline_plugins/components/collections/`、`pipeline_plugins/variables/` | 版本化插件/变量、执行和调度、输入输出、外部调用、敏感字段；业务插件目录不等于独立插件 SDK/runtime 仓库。 |
| `gcloud/periodictask/`、`gcloud/clocked_task/`、`gcloud/contrib/operate_record/` | 周期/定时任务、实际操作记录及副作用；检查重试、取消、日志和创建身份。 |
| `frontend/desktop/src/`、`frontend/desktop/package.json` | 模板编辑、参数填写、画布/任务操作、接口 envelope 和类型消费；前端校验/隐藏按钮不替代服务端授权。 |

具体链路先从 `gcloud/apigw/views/create_task.py` / `get_task_status.py` 开始：网关认证 → `mark_request_whether_is_trust` → `project_inject` → validator/IAM interceptor → 记录与 dispatcher → 返回数据。`project_inject` 根据请求 scope 解析路由标识后注入 request.project；后续权限、查询和日志应保持同一标识语义。查看 `task_view.py`、创建 `create_task.py`、操作 `task_operate.py` 是不同 interceptor，不能仅看某个装饰器就认定整个数据范围已授权。

create_task 需要同时检查项目模板与公共模板路径、是否删除、提供 pipeline_tree 或由模板生成的分支、constants 覆盖/元变量、exclude/execute 节点、引擎版本、回调/自动重试/节点超时记录。输入配置对象与转换后的值不能混淆，false/0/空列表/空字典、多选值、敏感变量与子流程常量需要保留类型。跨系统执行和数据库记录不是原子事务；客户端重试不得在没有去重证据时重复产生外部副作用。

get_task_status 先检查 project/task 归属和 IAM，再按任务 engine_ver 选择 dispatcher；subprocess_id、with_ex_data、根任务/子流程状态不能混用。缓存与输出字典可能共享，避免原地污染；finish_time、elapsed_time、REVOKED 等语义应查本分支及锁定引擎，历史事故不是当前缺陷。读状态不应顺便启动、重试或改变任务。

## APIGW 发布与文档

本分支实际资源文件是 `gcloud/apigw/management/commands/data/api-resources.yml`，定义文件是 `gcloud/apigw/management/commands/data/api-definition.yml`，由 `gcloud/apigw/management/commands/sync_saas_apigw.py` 使用。路由存在、资源注册、网关权限、文档和发布结果是不同证据。检查 method/path/operationId 唯一性、参数及返回 schema、认证/资源权限与真实 view 一致；不要把内部路由存在当成外部网关已发布。

本次核验没有根 `apigw/` 目录，不应强制使用其他分支的 MCP additions/supplement YAML。文档归档存在 `gcloud/apigw/docs/apigw-docs.tgz`，应以本分支 definition 的 resource_docs 配置确定实际消费产物；不要凭相似文件名新增另一份归档或运行真实网关同步。

## 测试与证据边界

- API 聚焦入口：`gcloud/tests/apigw/views/test_create_task.py`、`test_get_task_status.py`、`test_operate_task.py`、`test_operate_node.py`、`test_get_task_node_data.py`，对应请求形状、创建两条路径、状态与操作。
- 任务/模板入口：`gcloud/tests/taskflow3/`、`gcloud/tests/tasktmpl3/`、`gcloud/tests/template_base/`；插件/变量入口：`pipeline_plugins/tests/`，包括 `pipeline_plugins/tests/variables/collections/test_text_value_select.py`。按实际 diff 选择子包，不把测试名称当作断言覆盖证据。
- `.github/workflows/unittest.yml` 是该分支现有测试环境说明；使用 SQLite、测试环境变量和 IAM skip，部分依赖/下游被替代。可在独立测试环境用 `python manage.py test gcloud.tests.apigw.views.test_create_task gcloud.tests.apigw.views.test_get_task_status` 做聚焦验证；完整命令遵循现有 CI。
- 不在有用户改动的 checkout 中照搬 CI 的删除目录或写 local_settings 操作。CI/本地通过都不等于目标 MySQL、真实 IAM/网关、部署完整 SHA、STAG 或业务验收。
- 本次接入仅验证工作流 YAML、run shell 语法、知识路径与 diff 格式，没有运行应用单测、前端构建或发布。后续 MR 必须报告实际结果，不能沿用知识快照的检查结论。
