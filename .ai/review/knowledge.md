# bk-sops V3.28_lts 审查知识库

## 分支基线

- 核验日期：2026-09-09；目标 `V3.28_lts`；base SHA `ce4fb766d30b8f5f4e36603091e3b9e2924e3c2c`。这是独立维护分支的快照，不是 master 的能力清单。
- 运行时：`python-3.6.12`；依赖：`Django==3.2.15`、`bamboo-pipeline==3.24.2`、`celery==4.4.0`、`blueapps[opentelemetry]==4.7.0`。
- 标准运维自身负责项目/模板/任务和应用层协议，执行语义还取决于锁定的 bamboo-pipeline/引擎；升级必须同时考虑历史任务、插件和部署环境。

## 本 LTS 的边界

本分支仍保留，虽然最近提交较早，仍需覆盖向该 LTS 提交的修复。Python 3.6.12、Django 3.2/Celery 4 是本分支兼容基线，不能照搬 Python 3.11、Django 4/Celery 5 的 API 或依赖，也不能为接入 Node 18 审查工具改变应用运行时。

本分支没有 `gcloud/plugin_gateway/`、MCP 包装或多租户 Project 字段；审查不能要求不存在的新插件网关测试、MCP YAML 或 tenant manager。标准插件仍在 `pipeline_plugins/components/collections/`，外部插件相关实现在 `gcloud/external_plugins/`；是否需要增加新隔离能力取决于本次需求，不能把其他分支架构强加给普通修复。

中英文 API 文档在 `docs/apidoc/zh_hans/` 和 `docs/apidoc/en/`；其他文档在 `docs/develop/`、`docs/install/`、`docs/ops/`、`docs/overview/`。本分支没有 `docs/zh_hans/`、`docs/en/`、`docs/specs/`、`docs/plans/` 或旧工作流假定的 `.ai/rules/` 文件。API 文档打包按实际 definition/archive 路径核对。

现有 Unittest 使用 Python 3.6 和 ubuntu-20.04，runner/旧依赖是否仍能安装需要另行验证；新 AI 审查工作流使用独立 Node CLI，不证明旧应用 CI 已恢复，也不在本次变更中改其 runner。现有创建/状态测试仍是 LTS 回归入口。

V3.28 的 create_task 已使用 TaskCreateMethod.API 枚举，锁定 bamboo-pipeline 3.24.2；它与 V3.26 的依赖/实现不同，回移应核对当前代码而不是只改变补丁上下文。

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

本次核验没有根 `apigw/` 目录，不应强制使用其他分支的 MCP additions/supplement YAML。本分支由 `config/default.py` 的 `BK_APIGW_RESOURCE_DOCS_ARCHIVE_FILE` 配置消费 `gcloud/apigw/docs/apigw-docs.tgz`，`gcloud/apigw/management/commands/data/api-definition.yml` 的 resource_docs 引用该配置。以实际消费路径核对文档更新；两种相似后缀的文件同时存在不代表都应生成或更新，不强制改用其他分支路径。

## 测试与证据边界

- API 聚焦入口：`gcloud/tests/apigw/views/test_create_task.py`、`test_get_task_status.py`、`test_operate_task.py`、`test_operate_node.py`、`test_get_task_node_data.py`，对应请求形状、创建两条路径、状态与操作。
- 任务/模板入口：`gcloud/tests/taskflow3/`、`gcloud/tests/tasktmpl3/`、`gcloud/tests/template_base/`；插件/变量入口：`pipeline_plugins/tests/`，包括 `pipeline_plugins/tests/variables/collections/test_text_value_select.py`。按实际 diff 选择子包，不把测试名称当作断言覆盖证据。
- `.github/workflows/unittest.yml` 是该分支现有测试环境说明；使用 SQLite、测试环境变量和 IAM skip，部分依赖/下游被替代。可在独立测试环境用 `python manage.py test gcloud.tests.apigw.views.test_create_task gcloud.tests.apigw.views.test_get_task_status` 做聚焦验证；完整命令遵循现有 CI。
- 不在有用户改动的 checkout 中照搬 CI 的删除目录或写 local_settings 操作。CI/本地通过都不等于目标 MySQL、真实 IAM/网关、部署完整 SHA、STAG 或业务验收。
- `.github/scripts/test_ai_review.py` 验证审查 runner 的安全与输出边界，不替代本分支应用单测、前端构建或发布验证。后续 MR 必须报告实际运行结果，不能沿用知识快照的检查结论。

## API 文档、资源与更新细则

- 本分支资源版本为 `swagger: '2.0'`；按 Swagger 2.0 的 body parameter（`in: body`）及 responses核对请求/返回 schema，不因其他分支使用不同版本就要求迁移整个资源文件。definition 中模板表达式按模板格式处理，不能将合法模板误报为裸 YAML 语法错误。
- 中英文接口文档分别位于 `docs/apidoc/zh_hans/` 和 `docs/apidoc/en/`，应包含功能说明、参数表、请求示例、返回示例和字段说明，并与实际路由、校验器、返回值逐项核对。
- 归档消费路径是 `gcloud/apigw/docs/apigw-docs.tgz`；接口文档正文布局为 `zh/*.md` 与 `en/*.md`，中文不是 zh_hans。区分已有归档元数据与本次新增变动，不把历史产物差异自动当作当前 PR 缺陷。公共只读审查 runner 不打包文档或同步真实网关。
- 项目/业务/scope、receiver_group 等组名或 ID、路径参数及下游查询语义需一致；JSON 解析和 int 等转换的错误边界应受控，在查询前验证类型与结构，不能仅凭出现转换函数就报错。
- 更新副作用按实际 model.save 覆写、signal receiver、update_fields 条件、通知/审计/队列调用追踪；Django save(update_fields=...) 并不普遍绕过 pre_save/post_save。权限资源一致性、命名语义和副作用回归用例按 diff 选择，审查模型不执行测试。
