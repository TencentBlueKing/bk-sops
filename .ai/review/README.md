# dev_multi_tenant_0729_merge 的自动代码审查

本分支通过 `.github/workflows/code_review.yml` 使用现有 CodeBuddy iOA 通道，主命令和兼容命令均指定 `glm-5.3-ioa`。沿用仓库级 `CODEBUDDY_API_KEY` 和 GitHub Actions 的 `github.token`，不需要新增模型密钥。

## 何时生效

工作流、`knowledge.md` 和 `rules.md` 合入目标分支 `dev_multi_tenant_0729_merge` 后，针对该目标分支的 PR 在 opened、synchronize、reopened 或 ready_for_review 事件触发时才会使用本方案。仅把文件提交到接入 PR 的 head，或只合入 master，不代表本目标分支已经接入。既有 PR 需要在目标分支合入后再次产生上述事件；本次文档和静态检查不是线上审查成功的证据。

工作流先检查 PR 作者和事件触发者的当前仓库权限，两者都为 write 或 admin 才执行审查。审查 job 保留 contents:read 和 pull-requests:write，用于读取 PR、提交评论；提示词要求仅提交 comment，禁止 approve 或 request-changes。模型遵守提示词的结果仍需通过实际运行核验。

## 规则与源码来自哪里

- `knowledge.md` 说明本分支实际源码、依赖、协议和测试入口；`rules.md` 说明审查约束。分支演进时同步维护，不能直接套用 master 或其他 LTS 的目录与能力。
- 审查源码检出 PR Head SHA；规则通过 `git show <PR Base SHA>:.ai/review/knowledge.md` 与 `git show <PR Base SHA>:.ai/review/rules.md` 读取并直接加入提示词。旧 PR head 没有新规则文件也可以审查；PR 自己修改规则时，本轮仍采用目标 base 中的版本。
- 缺失规则文件会使读取步骤失败，不静默改读 PR head。遇到缺失时先检查事件记录的 base SHA 是否已经包含接入提交。
- 不运行 PR 中的测试、安装或部署脚本，不把凭据、完整 MCP 配置、敏感任务参数写入日志或评论；保留当前可信贡献者与凭据边界。

## 验证范围

接入检查包括 YAML 解析、工作流静态检查、run 脚本语法、规则加载与源码路径，以及 diff 格式。应用单测、前端构建、真实 CodeBuddy 模型调用、GitHub 上的运行结果和部署验收需要分别记录，不能互相替代。已有应用测试环境见 `.github/workflows/unittest.yml`；本次不升级 Python、依赖或其 runner。
