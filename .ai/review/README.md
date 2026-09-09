# AI 自动代码审查

本仓库通过 CodeBuddy 公司通道运行 AI 审查。模型由仓库 Actions variable `AI_REVIEW_MODEL` 集中选择；Actions、任务和评论标题固定使用通用名称，切换模型无需改标题或脚本。审查仅辅助人工决策，不替代既有 lint、单测、发布检查或真实集成验收。

## 触发与权限

- PR 新建、更新、重新打开或退出草稿时运行；PR 作者和事件发起人都必须拥有仓库 write/maintain/admin 权限。外部贡献者的 PR 会明确跳过，可由维护者人工审查；不能靠加标签放开凭据。
- 管理员在 GitHub 仓库 Actions Secrets 中配置 `CODEBUDDY_API_KEY`，值为公司 CodeBuddy API key；不使用 OpenClaw OAuth token。缺少或失效会失败，不发布“无问题”结论。密钥到期前由维护者更新该 Secret。
- 管理员在同一设置页的 Variables 中配置 `AI_REVIEW_MODEL` 为公司通道可用的模型 ID。该值不是秘密，所有维护分支共用；缺少或格式无效会在启动 CLI 前失败，不静默回退到其他模型。本地验证真实调用时也须提供该环境变量；无凭据单测使用测试模型值。
- `pull_request_target` 从仓库默认分支读取工作流；本工作流再显式检出 PR Base SHA，只执行该目标分支已合入的审查脚本和知识。接入 PR 的检查不证明其 head 配置已经生效；后续 PR 事件才会加载已合入的方案。
- 不创建自动合入、自动批准或发布任务；暂不把 AI 判断设为必需合入门禁。

## LTS 与开发分支覆盖

默认分支的工作流是全仓触发入口；每条 PR 目标分支还必须拥有审查脚本和知识规则。默认分支已经接入、工作流没有 `branches` 过滤，都不意味着其他 LTS 自动获得完整审查。新建或保留维护分支时，将六份接入文件一起补齐，并按该分支真实模块、版本和兼容约束调整知识与规则；各分支的工作流副本供维护回移使用，当前执行入口仍来自默认分支。

目标 base 完全没有审查脚本/两份规则时，工作流明确标记尚未接入并跳过模型调用；仅缺少部分文件则失败，避免不完整配置静默运行。合入 LTS 的完整接入文件后，后续事件才执行该 LTS 的审查。工作流逻辑变更还必须合入默认分支，单独修改 LTS 的工作流副本不会改变当前入口。

仓库级 `CODEBUDDY_API_KEY` Secret 由同一仓库的分支共享，无需逐分支创建。合入后用新的维护 PR 验证 `review` 调用模型、`publish` 发布对应 head 的评论；仅 `validate` 通过只能证明 runner 单测通过。已有 PR 不会因目标分支补接入而自动重跑，需要后续更新、重新打开或退出草稿事件。

## 审查上下文

- `.ai/review/knowledge.md`：仓库模块、依赖与协议事实。
- `.ai/review/rules.md`：按改动范围追踪的约束及证据要求。
- 每次针对 merge-base 到事件 head 的完整 diff；不依赖单次 webhook 的增量片段。模型可以用 Read/Glob/Grep 阅读 head 的普通文件快照，不能执行 PR 脚本、测试或修改文件；StructuredOutput 只提交结构化结果。
- PR 中的新规则仅作为待审查内容，本轮使用已合入目标分支的规则，避免 PR 自行改变审查标准。
- 不加载项目/用户 CodeBuddy 设置或 MCP；Read/Glob/Grep 使用快照目录的默认读取边界，目录外请求在非交互模式下拒绝；快照排除符号链接、Git/Agent 配置和大于 250 KB 的文件。过滤清单进入提示和结果边界，diff 仍保留相关改动。diff 超过 400 KB、差异定位结构超过 96 KB 或快照超过 60 MB 会失败并提示拆分，避免把不完整阅读报成全量通过。

## 输出与故障处理

最多报告 8 个有触发条件、调用链、影响和修复建议的 P1/P2 问题，用中文输出到一条可更新的 PR 评论，附本次 commit 的源码行链接。仅允许引用本次新增/删除行。重复运行更新同一评论，也兼容旧模型命名版本的评论标记，将其更新为通用标题；发布前重新检查 head 和 base，过期结果不发布。

模型任务只有仓库只读权限；评论发布在独立 job 中持有 PR 写权限。CLI 原始输出由私有临时文件接收，避免进程退出时尚未写完的管道造成长 JSON 截断；文件关闭即删除。仅传递验证后的结果和提交元数据，不上传原始对话、源码快照或配置目录。Actions 固定到提交 SHA，CLI 固定 `@tencent-ai/codebuddy-code@2.147.0`。

模型调用、JSON 校验或凭据失败会使检查失败；查看失败步骤处理，不能据“没有评论”认定通过。更新依赖或约束后先跑下列验证，再用正常业务 PR 检查结果。AI 输出有误由人工判定，修正知识规则后随 PR 更新重跑。

## 额度与信任范围

写权限检查包含 GitHub 团队/组织继承的有效权限，不是个人名单。模型只收到模型调用凭据，不收到 GitHub token；不读取 PR 讨论评论，不允许命令执行、编辑、网络工具或 MCP。PR 中的代码、规则和文本都只是待审数据。

每次最多 24 个 agent turns，模型进程最多运行 900 秒，审查 job 最多 25 分钟。同一 PR 的新事件会取消旧运行；这些限制不是每日 token/金额硬预算，也不会退回已发生的调用费用。密钥应优先使用公司批准的 CI 专用身份，并在服务端设置预算、频率与告警。账号级每日总限额可能影响该账号的其他产品，不能当作本仓库独享额度；工作流本身不签发专用身份或管理服务端预算。

## 验证

```bash
python3 -I -m unittest discover -s .github/scripts -p test_ai_review.py -v
```

该测试不需要模型凭据，覆盖作者/触发者权限、模型配置、通用标题与旧评论迁移、diff 定位、返回结构、链接与提及转义、路径穿越/符号链接、export-ignore/export-subst、特殊文件名、过期结果和评论更新；同时验证模型进程不继承 GitHub 凭据、runner 命令文件和外部工具授权，以及超过 1 MB 的 CLI JSON 在立即退出后仍完整读取。工作流的 `pull_request` 校验 job 不接收模型 Secret；业务代码应另按知识库列出的现有测试执行。

参考：[GitHub Actions 安全指南](https://docs.github.com/en/actions/reference/security/secure-use)、[pull_request_target 默认分支语义](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)。
