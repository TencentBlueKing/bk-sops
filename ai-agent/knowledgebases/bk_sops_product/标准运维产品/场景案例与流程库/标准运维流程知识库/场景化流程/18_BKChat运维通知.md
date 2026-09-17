# 运维通知

> 基于 BKChat/企业微信的自动化通知与交互。包括长文本通知、Job 日志推送、告警通知等。
>
> **358** 条流程 | 平均节点数基于采样分析

---

## 关键检查点

1. 通知流程必须包含消息发送节点（当前采用率 7%）
2. 消息发送后需确认送达（当前采用率 0%）
---
## 代表性流程图

**流程 1**（37 个节点）:
```
开始 → 测试 → facade发布流程审批 → [条件] → BkChat通知插件 → BkChat通知插件 → 快速执行脚本 → [汇聚] → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → bkchat通用消息通知 → 结束
```

**流程 2**（29 个节点）:
```
开始 → SA申请机器 → SA申请机器单据轮询 → 【常用】【SA】【Linux】空闲检查 → 【常用】【SA】【Linux】初始化 → 【常用】【SA】配置UDNS → 【安装】【IDC】主机bifrost/bksam初始化【正式】 → 磁盘挂载data改成data1 → 【安装】手游secagent安装 → 插件操作 → 插件操作 → 蓝鲸监控告警屏蔽 → 集群创建 → 处理更新主机所属业务模块参数 → 处理修改集群属性参数 → 批量更新集群属性 → CC-主机所属模块修改 → 按规则修改主机名 → 分发文件前初始化 → 分发jq → 生成配置文件 → 文件分发后初始化 → 部署crontab → 在线库权限申请 → 【bkhcm海垒 2.0】RS规则上线 → 在线库权限申请（另外一个账号） → 定时 → 解除告警屏蔽 → 结束
```

**流程 3**（13 个节点）:
```
开始 → BKChat会话填参 → [条件] → 进入IOS逻辑 → 进入AN逻辑 → 取消执行发布版本成功 → 进入PC逻辑 → 脚本GetPublishDiff → 结束 → [条件] → 发布失败 → BKChat会话填参 → [条件] → 再次向用户确认是否确认发布？ → 取消执行发布版本成功 → [条件] → 用户发布前取消 → 脚本PublishGlobal → 发布成功 → 结束
```

**流程 4**（11 个节点）:
```
开始 → BKChat会话填参 → [条件] → 脚本GetVersion → 结束 → 选择起始版本 → 选择结束版本 → BkChat通知插件 → 验证待删除版本是否正确 → [条件] → BkChat通知插件 → BKChat会话填参 → [条件] → BkChat通知插件 → 脚本DeleteBatchVersion → BkChat通知插件 → 结束
```

**流程 5**（8 个节点）:
```
开始 → BKChat会话填参 → [条件] → 脚本GetResLog → 结束 → 选择想要恢复的版本 → [条件] → BkChat通知插件 → BKChat会话填参 → [条件] → BkChat通知插件 → 脚本RestoreVersion → BkChat通知插件 → 结束
```

**流程 6**（7 个节点）:
```
开始 → 获取大区oss ip → 蓝鲸审批 → 分发本地文件 → 快速执行脚本 → 快速执行脚本 → 传输log文件到tcm机器 → 快速执行脚本 → 结束
```

**流程 7**（7 个节点）:
```
开始 → 文件检查 → 清空传输目录v1 → 全业务快速分发文件 → [条件] → 清空临时目录并文件复制 → 文件生成cos链接 → 快速分发文件 → bkchat通用消息通知（开发商） → 结束
```

**流程 8**（7 个节点）:
```
开始 → 获取通知人 → 获取文件下载链接 → 获取文件路径 → 获取文件md5 → 获取文件上报时间 → 获取文件上报openid → 发送通知 → 结束
```

---

## 通用模式

### 常见标准子流程

**1. 标准通知序列**
```
数据/事件获取 → 内容格式化 → BKChat API发送 → 确认送达
```

**2. 带审批的通知序列**
```
BKChat发送审批消息 → 等待审批结果 → 根据结果执行操作 → BKChat通知结果
```

---

## 核心组件

| 组件 | 说明 | 使用场景 | 使用次数 |
|------|------|---------|--------|
| `remote_plugin` | 蓝鲸标准插件调用 | 调用蓝鲸标准插件（DBM/AI/BKChat 等） | 160 |
| `job_fast_execute_script` | 快速脚本执行 | 通过 JOB 平台快速执行 Shell/Python 脚本 | 58 |
| `wechat_work_send_message` | 企业微信消息 | 发送企业微信群/个人消息 | 20 |
| `job_execute_task` | JOB 作业执行 | 执行 JOB 平台预定义的作业模板 | 18 |
| `bk_notify` | 蓝鲸通知 | 发送邮件/短信/微信通知 | 14 |
| `bk_http_request` | HTTP 请求 | 发送 HTTP/HTTPS 请求调用外部 API | 7 |
| `all_biz_job_fast_push_file` | all_biz_job_fast_push_file | all_biz_job_fast_push_file | 6 |
| `job_fast_push_file` | 快速文件分发 | 通过 JOB 快速推送文件到目标机器 | 5 |
| `job_fetch_task_log` | JOB 日志获取 | 获取 JOB 任务执行日志 | 4 |
| `sleep_timer` | 定时等待 | 流程等待指定时间后继续 | 4 |
| `job_push_local_files` | 本地文件推送 | 推送本地文件到远程机器 | 2 |
| `tcm_execute_task` | TCM 配置管理 | 执行 TCM 配置检查/安装/启用/禁用 | 2 |
| `nodeman_plugin_operate` | 节点管理插件 | 操作节点管理平台插件 | 2 |
| `all_biz_job_fast_execute_script` | all_biz_job_fast_execute_script | all_biz_job_fast_execute_script | 2 |
| `bk_display` | 消息展示 | 在流程中展示信息供查看 | 1 |

## 核心插件

| 插件 | 说明 | 使用场景 | 使用次数 |
|------|------|---------|--------|
| `bkchat-sops-send` | BKChat 消息发送 | 发送消息到企业微信群 | 53 |
| `bkchat-sops` | BKChat 集成 | 蓝鲸 ChatOps 消息交互 | 47 |
| `tcompose-exec` | TCompose 执行 | 执行容器编排任务 | 21 |
| `bkchat-input` | bkchat-input | bkchat-input | 14 |
| `bkchat-csutomsg` | bkchat-csutomsg | bkchat-csutomsg | 4 |
| `ai-jk` | ai-jk | ai-jk | 2 |
| `onclock` | onclock | onclock | 2 |
| `devops-pl-plugin` | 蓝盾流水线 | 触发蓝盾 CI/CD 流水线 | 2 |
| `bkdbm-authorize` | DBM 授权 | 数据库管理平台授权 | 2 |
| `tcompose-bkapp` | tcompose-bkapp | tcompose-bkapp | 2 |

---

## 关键参数

### 组件参数

| 参数 | 所属组件 | 说明 | 示例值 |
|------|---------|------|--------|
| `msg_type` | 蓝鲸标准插件调用 | msg_type | markdown |
| `mentioned_members` | 蓝鲸标准插件调用 | mentioned_members | - |
| `msg_content` | 蓝鲸标准插件调用 | msg_content | - |
| `biz_cc_id` | 快速脚本执行 | biz_cc_id | - |
| `job_account` | 快速脚本执行 | job_account | root |
| `job_content` | 快速脚本执行 | job_content | - |
| `job_ip_list` | 快速脚本执行 | job_ip_list | ${job_ip_list} |
| `job_script_list_general` | 快速脚本执行 | job_script_list_general | - |
| `message_content` | 企业微信消息 | message_content | ${message} |
| `msgtype` | 企业微信消息 | msgtype | text |
| `wechat_work_chat_id` | 企业微信消息 | wechat_work_chat_id | xxx |
| `wechat_work_mentioned_members` | 企业微信消息 | wechat_work_mentioned_members | ${wechat_work_mentioned_members} |
| `button_refresh` | JOB 作业执行 | button_refresh | - |
| `job_global_var` | JOB 作业执行 | job_global_var | - |
| `job_task_id` | JOB 作业执行 | job_task_id | - |
| `button_refresh_2` | JOB 作业执行 | button_refresh_2 | - |
| `bk_notify_content` | 蓝鲸通知 | bk_notify_content | ${_system.task_start_time} |
| `bk_notify_title` | 蓝鲸通知 | bk_notify_title | ${_system.task_url} |
| `bk_notify_type` | 蓝鲸通知 | bk_notify_type | - |
| `bk_receiver_info` | 蓝鲸通知 | bk_receiver_info | - |

### 流程变量

| 变量 | 名称 | 来源类型 | 出现次数 |
|------|------|---------|--------|
| `${log_outputs}` | JOB全局变量 | component_outputs | 19 |
| `${result_vars}` | 结果变量 | component_outputs | 9 |
| `${_result}` | 执行结果 | component_outputs | 8 |
| `${user}` | 执行用户 | custom | 8 |
| `${title}` | 标题 | custom | 6 |
| `${message}` | 内容 | custom | 6 |
| `${task_parameters}` | 任务参数信息 | custom | 6 |
| `${task_status}` | 任务状态 | custom | 6 |
| `${wechat_work_mentioned_members}` | 提醒人 | component_inputs | 6 |
| `${message_content}` | 消息内容 | component_inputs | 5 |
| `${content}` | QQ群内容 | custom | 5 |
| `${job_task_log}` | 任务日志 | component_outputs | 5 |
| `${VersionStr}` | VersionStr | custom | 5 |
| `${access_id}` | access_id | custom | 5 |
| `${access_key}` | access_key | custom | 5 |

---

## 网关使用

| 网关类型 | 使用次数 | 说明 |
|---------|---------|------|
| ParallelGateway | 4 | 并行执行所有分支 |
| ExclusiveGateway | 28 | 条件选择单一分支 |
| ConvergeGateway | 8 | 等待所有并行分支完成 |
| ConditionalParallelGateway | 2 | 满足条件的分支并行执行 |

---

## 检查清单

| 检查项 | 说明 | 严重程度 |
|--------|------|--------|
| 🟡 消息格式 | 通知内容是否包含关键信息（操作人、时间、结果） | 中 |
| 🔴 失败通知 | 操作失败时是否有告警通知 | 高 |
| 🟡 接收人配置 | 通知接收人是否正确配置 | 中 |
| 🟢 消息类型 | 是否选择合适的消息类型（text/markdown/file） | 低 |