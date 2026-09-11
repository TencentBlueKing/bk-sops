# bk-sops master 审查知识库

## 分支基线

- 核验日期：2026-09-09；目标 `master`；base SHA `8c62c86cca084a7938d5449a428eaafbbb71a81f`。仓库默认分支当前是 `release_humming_bird`；这里的 master 名称不代表 GitHub 工作流执行入口。
- `runtime.txt` 为 `python-3.6.12`；`requirements.txt` 锁定 `Django==3.2.25`、`bamboo-pipeline==3.24.19`、`celery==4.4.0`、`blueapps[opentelemetry,bkcrypto]==4.14.0`。不能按 humming_bird 的 Python 3.11/Django 4 或旧 LTS 的更早引擎版本审查。
- 本分支仍无 Project.tenant_id 和多租户 IAM client/resource 构造；新增隔离需求应按实际需求检查，不能把 dev_multi_tenant 的字段/能力当成本分支已存在。

## 当前 API、MCP 与插件网关

`gcloud/apigw/views/create_task.py` 同时支持显式 pipeline_tree 与模板生成路径，使用 `gcloud/apigw/views/task_node_selector.py` 归一化 template_schemes_id 和排除/执行节点。显式树与模板方案有互斥限制；text_value_select 多选默认字符串已按类型转换列表，不能沿用旧 PR 的未修复结论。须核对最终执行树、两条创建路径、变量覆盖/默认值、真实执行用户与审计用户；`gcloud/contrib/audit/` 的事件在 on_commit 边界发布。

MCP 由 `gcloud/apigw/decorators.py` 的 `mcp_apigw`/请求识别与现有 view 包装实现，没有独立 `gcloud/mcp/`。create_task 的 MCP 响应排除 data.pipeline_tree，并区分 API/MCP create_method；其他 view 的 exclude/trim 和 include 参数按各自装饰器判断。`_apply_mcp_transforms` 会原地修改传入字典，涉及缓存或复用数据时检查是否需要副本；普通 APIGW 和 MCP 返回不能互相替代。

`gcloud/plugin_gateway/` 不是独立插件 SDK/runtime 仓库，也不叫 `gcloud/plugin_service/`。本分支已有如下链路：

- `gcloud/apigw/views/plugin_gateway.py` 和 `gcloud/plugin_gateway/serializers.py` 负责目录、表单、执行、查询、取消及内部回调入口；追踪网关 app/user、payload operator、来源配置与真实下游身份。执行记录读取和取消按 caller_app_code 校验归属，不能把应用归属自动视作业务/项目或用户执行授权。
- `gcloud/plugin_gateway/models.py` 保留 uniform_api v4 的 open_plugin_run_id/task_tag 协议名，约束 caller_app_code+client_request_id 唯一。`services/execution.py` 进行同键内容冲突检查、加密 callback_token，只有新建才投递执行；已有此实现不能报告成当前完全无幂等。检查外层事务与 Celery 投递、失败恢复、重复/并发请求，不把数据库原子块等同于下游原子执行。
- `gcloud/plugin_gateway/services/context.py` 根据 scope、CMDB 业务映射、来源配置和默认项目解析执行/表单上下文；传递 operator/project/bk_biz_id/task/node 等字段。默认项目回退不是授权证明。callback URL 校验使用来源配置域名白名单；回调重试、重定向、token 解密和日志需追到 `services/callbacks.py`。
- `gcloud/plugin_gateway/services/runner.py` 直接驱动组件 Service 的 execute/schedule，不创建普通引擎任务；第三方插件绑定 remote_plugin 1.0.0 组件。`gcloud/plugin_gateway/tasks.py` 负责异步分发、轮询、回调与超时；普通节点回调和插件网关回调必须保持各自路由，取消记录不代表底层外部任务必然停止。
- `gcloud/plugin_gateway/services/catalog.py`、`form_schema.py`、`builtin_form_schema.py`、`native_forms.py` 区分统一字段元数据、JSON Schema 和原生 component.js/RenderForm。保留空表单、对象/列表/false/0、插件版本、绝对 URL 与上下文，不把转换后的 schema 当成原生脚本。

本 master 没有 dev_multi_tenant 新增的 PluginGatewayDisabledError/test_feature_switch.py，必须按当前源码判断功能开关能力。中英文文档在 `docs/zh_hans/apidoc/`、`docs/en/apidoc/`，设计/计划在 `docs/specs/`、`docs/plans/`。`.ai/rules/api-change-checklist.mdc` 存在但其中根 MCP YAML 引用并不存在，工作流使用 `.ai/review/` 中这份实际路径知识。

## master 的测试入口

- `gcloud/tests/apigw/views/test_create_task.py` 包含代理执行/审计用户、模板方案、显式树互斥、多选默认值两条路径的测试；`test_get_task_status.py` 是状态入口，不能把两个基础测试当作根任务/子流程/终态的完整覆盖。
- `gcloud/tests/plugin_gateway/test_execution.py` 有应用维度幂等、同键冲突、加密 token、新建投递、取消和超时测试；`test_callback_routing.py` 区分网关/普通节点回调，另有 runner/dispatch/callbacks/context/cors/native_forms/form_schema 相关测试。只引用实际文件与断言，不能使用其他分支的 feature switch 测试作证。
- `.github/workflows/unittest.yml` 使用 ubuntu-22.04、clang 和 pyenv 构建 Python 3.6.12，固定 PYENV_GIT_TAG=v2.6.31，运行 coverage + Django tests；这不同于旧 LTS ubuntu-20.04，也不同于 humming_bird Python 3.11。Node 18 是 AI 工具环境，不改变应用版本。

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

- 本分支资源版本为 `openapi: 3.0.1`；按 OpenAPI 3 的 parameters、POST requestBody 及 responses核对请求/返回 schema，不因其他分支使用不同版本就要求迁移整个资源文件。definition 中模板表达式按模板格式处理，不能将合法模板误报为裸 YAML 语法错误。
- 中英文接口文档分别位于 `docs/zh_hans/apidoc/` 和 `docs/en/apidoc/`，应包含功能说明、参数表、请求示例、返回示例和字段说明，并与实际路由、校验器、返回值逐项核对。
- 归档消费路径是 `gcloud/apigw/docs/apigw-docs.tgz`；接口文档正文布局为 `zh/*.md` 与 `en/*.md`，中文不是 zh_hans。区分已有归档元数据与本次新增变动，不把历史产物差异自动当作当前 PR 缺陷。公共只读审查 runner 不打包文档或同步真实网关。
- 项目/业务/scope、receiver_group 等组名或 ID、路径参数及下游查询语义需一致；JSON 解析和 int 等转换的错误边界应受控，在查询前验证类型与结构，不能仅凭出现转换函数就报错。
- 更新副作用按实际 model.save 覆写、signal receiver、update_fields 条件、通知/审计/队列调用追踪；Django save(update_fields=...) 并不普遍绕过 pre_save/post_save。权限资源一致性、命名语义和副作用回归用例按 diff 选择，审查模型不执行测试。
