# 开放插件网关 Implementation Plan

**Goal:** 将开放插件网关实现统一收敛到 `gcloud.apigw` 分层下，并同步补齐中英文文档、APIGW 资源定义与资源文档归档。

**Architecture:** 领域模型和服务逻辑放在 `gcloud.plugin_gateway`，对外网关视图放在 `gcloud.apigw.views.plugin_gateway`，所有接口统一挂载到 `/apigw/plugin-gateway/` 前缀下。

**Tech Stack:** Django, API Gateway, Markdown, OpenAPI YAML

**Spec:** `docs/specs/2026-04-21-open-plugin-gateway-design.md`

---

## File Structure

| 文件 | 操作 | 说明 |
|------|------|------|
| `docs/specs/2026-04-21-open-plugin-gateway-design.md` | 更新 | 反映 `plugin_gateway` 模块分层与接口路径 |
| `docs/plans/2026-04-21-open-plugin-gateway.md` | 更新 | 记录当前交付范围 |
| `docs/zh_hans/deploy/open_plugin_gateway_deploy.md` | 更新 | 中文部署指南 |
| `docs/zh_hans/guide/open_plugin_gateway_access.md` | 更新 | 中文接入指南 |
| `docs/en/deploy/open_plugin_gateway_deploy.md` | 新增 | 英文部署指南 |
| `docs/en/guide/open_plugin_gateway_access.md` | 新增 | 英文接入指南 |
| `docs/zh_hans/apidoc/*.md` | 新增 | 中文 APIGW 资源文档 |
| `docs/en/apidoc/*.md` | 新增 | 英文 APIGW 资源文档 |
| `gcloud/apigw/management/commands/data/api-resources.yml` | 更新 | 新增插件网关资源定义 |
| `gcloud/apigw/docs/apigw-docs.tgz` | 更新 | 重新打包资源文档 |

---

## Task 1: 调整实现分层

**Files:**
- Update: `gcloud/apigw/urls.py`
- Create: `gcloud/apigw/views/plugin_gateway.py`
- Update: `config/urls_custom.py`
- Rename: `gcloud/open_plugins` -> `gcloud/plugin_gateway`

- [ ] 将对外接口统一切换到 `/apigw/plugin-gateway/`
- [ ] 清理根路径下的重复路由
- [ ] 保持领域逻辑与 APIGW 视图分层明确

## Task 2: 修复实现风险

**Files:**
- Update: `gcloud/plugin_gateway/services/*.py`
- Update: `gcloud/plugin_gateway/models.py`
- Update: `gcloud/plugin_gateway/migrations/0001_initial.py`

- [ ] 将幂等约束收敛到 `(caller_app_code, client_request_id)`
- [ ] 对重复幂等请求做关键字段冲突校验
- [ ] 将空白名单语义调整为默认拒绝
- [ ] 运行时动态注入 detail/list URL
- [ ] 为回调失败增加日志和重试
- [ ] 对回调 token 做加密存储

## Task 3: 补齐接口文档与资源定义

**Files:**
- Create: `docs/zh_hans/apidoc/plugin_gateway_*.md`
- Create: `docs/en/apidoc/plugin_gateway_*.md`
- Update: `gcloud/apigw/management/commands/data/api-resources.yml`
- Update: `gcloud/apigw/docs/apigw-docs.tgz`

- [ ] 为 7 个插件网关接口补齐中英文 APIGW 文档
- [ ] 在资源定义中注册对应的 APIGW 路径
- [ ] 重新打包资源文档归档

## Task 4: 补齐部署与接入说明

**Files:**
- Update: `docs/zh_hans/deploy/open_plugin_gateway_deploy.md`
- Update: `docs/zh_hans/guide/open_plugin_gateway_access.md`
- Create: `docs/en/deploy/open_plugin_gateway_deploy.md`
- Create: `docs/en/guide/open_plugin_gateway_access.md`

- [ ] 统一更新模块名、模型名与路由前缀
- [ ] 明确空白名单拒绝与应用级幂等语义
- [ ] 明确当前版本仍未自动调度真实插件执行

## Task 5: 自检

**Files:**
- Verify: 上述所有改动文件

- [ ] 检查旧的 `open_plugins` 路径和命名引用是否已清理
- [ ] 检查文档、资源定义和实际实现是否一致
- [ ] 运行测试与基础格式检查
