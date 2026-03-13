# OpenClaw SOPS Skill 编写规范

## AI 来源标识（必须）

所有 OpenClaw Skill 在调用 SOPS API 时，**必须**在 HTTP 请求头中携带以下 Header：

| Header | 值 | 必传 | 说明 |
|---|---|---|---|
| `X-Bkapi-Ai-Platform` | `openclaw` | 是 | 固定值，标识请求来自 OpenClaw 平台 |
| `X-Bkapi-Ai-Skill` | 当前 skill 名称 | 是 | 如 `sops-task-execution`、`sops-template-query` |

### 示例

调用 SOPS API 时，请求头应包含：

```
X-Bkapi-Ai-Platform: openclaw
X-Bkapi-Ai-Skill: sops-task-execution
```

### 说明

- 这些 Header 用于 SOPS 后端进行调用来源统计（调用次数、用户数、业务分布等）
- 不传 Header 不会影响 API 功能，但会导致该次调用无法被统计为 AI 来源
- `X-Bkapi-Ai-Platform` 的值当前固定为 `openclaw`，后续如有其他 AI 平台接入会分配不同的值
