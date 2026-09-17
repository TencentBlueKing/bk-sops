## 问题描述：

AI 调用标准运维 MCP 工具（如 start_task、operate_task）时报 404 错误，错误信息为 `API not found`，原因是 AI 在调用 MCP 时 URL 中的变量（如 `[task_id]`、`[bk_biz_id]`）没有被正确替换填写。

## 解决方法：

切换模型为 **deepseek-v3** 后重试，该模型能正确填写 URL 中的变量参数。