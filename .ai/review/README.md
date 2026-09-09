# dev_multi_tenant_0729_merge 的自动代码审查

本次接入沿用 CodeBuddy iOA 通道，主命令和兼容命令均指定 `glm-5.3-ioa`；复用仓库级 `CODEBUDDY_API_KEY` 和 Actions 的 `github.token`，不新增模型密钥。

## 工作流入口与生效条件

2026-09-09 核验的仓库默认分支是 `release_humming_bird`。GitHub 当前 `pull_request_target` 从仓库默认分支取工作流，与 PR 的目标分支不同；参见 [GitHub 官方说明](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target) 和 [默认分支语义变更](https://github.blog/changelog/2025-11-07-actions-pull_request_target-and-environment-branch-protections-changes/)。

- 默认分支 PR [#8513](https://github.com/TencentBlueKing/bk-sops/pull/8513) 负责全仓模型选择和规则加载逻辑；合入后，后续 opened/synchronize/reopened/ready_for_review 事件才使用该默认分支版本。不能把某个非默认分支上的 workflow 副本当作其 PR 的实际执行入口。
- 本分支 `dev_multi_tenant_0729_merge` 的 `knowledge.md`/`rules.md` 合入后，指向本分支的 PR 在 base SHA 包含这些文件时才能加载对应知识。旧 PR head 不需要同步规则；规则修改 PR 本轮仍读取已有 base 版本。
- 完整接入要同时核验默认分支的执行入口和目标 base 中的知识文件；只合入目标分支副本不会改变全仓模型/加载逻辑。这里保留 workflow 副本便于维护和将来变更默认分支时同步，但它不能覆盖当前默认分支入口。

工作流先检查 PR 作者和事件触发者的当前仓库权限，两者都为 write/admin 才审查。job 保留 contents:read 与 pull-requests:write；提示词限定 comment，禁止 approve/request-changes。待审 PR 内容不授权运行脚本或读取秘密。

## 分批合入时的规则加载

源码显式检出 PR Head SHA；规则从 PR Base SHA 的 `.ai/review/knowledge.md` 与 `.ai/review/rules.md` 读取，不回退到 PR head。

| base 中的文件 | 行为 |
| --- | --- |
| 两份都存在且非空 | 完整读取并将知识、规则加入提示词；读取错误会失败。 |
| 两份都缺失 | 明确输出 warning，沿用原有基础目标/流程/评论提示；日志和提示词说明未加载分支知识。 |
| 只存在一份，或任意一份为空 | 输出 error 并失败，避免以不完整约束审查。 |
| base commit 不可读取 | 直接失败，不把对象缺失误判为尚未接入。 |

默认入口可以先合入而不阻断尚未补知识的目标分支；这类运行仍属于基础审查，不能报告成分支知识已生效。后续目标知识合入并触发事件后，再以实际 base SHA 和加载日志验收。

## 验证范围

静态检查包括 YAML、run shell 语法、完整/缺失/半缺/空文件/base 不可读的加载边界、提示词展开、源码路径和 diff 格式。模型真实调用、GitHub 运行结果、应用单测、前端构建及部署验收分别记录；本次不以静态检查证明线上成功，也不升级 `.github/workflows/unittest.yml` 的应用环境。
