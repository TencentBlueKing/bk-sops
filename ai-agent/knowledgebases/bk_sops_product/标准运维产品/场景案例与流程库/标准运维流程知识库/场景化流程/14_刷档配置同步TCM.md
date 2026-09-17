# 配置同步TCM

> 游戏配置数据的刷新与同步。包括 TCM 配置管理、七彩石推送、现网配置提取等。
>
> **559** 条流程 | 平均节点数基于采样分析

---

## 关键检查点

1. 必须遵循 TCM 标准序列（checkconf → disable → install → enable）（当前采用率 8%）
2. 配置下发前必须有人工确认（当前采用率 14%）
3. 配置同步后必须执行检查验证（当前采用率 2%）
4. 刷档前备份当前配置（当前采用率 3%）
5. 配置同步完成后发送通知（当前采用率 25%）
---
## 代表性流程图

**流程 1**（52 个节点）:
```
开始 → [并行] → 服务端停服 → 服务端停服 → 服务端停服 → 服务端停服 → 删除全部已注册的xxx服务 → 删除全部已注册的xxx服务 → 删除全部已注册的xxx服务 → 删除全部已注册的xxx服务 → 上传Region.zip到服务器 → 上传Region.zip到服务器 → 上传Region.zip到服务器 → 上传Region.zip到服务器 → Region.zip解压 → Region.zip解压 → Region.zip解压 → Region.zip解压 → 解压region.zip并创建目录以及服务注册脚本 → 解压region.zip并创建目录以及服务注册脚本 → 解压region.zip并创建目录以及服务注册脚本 → 解压region.zip并创建目录以及服务注册脚本 → 服务注册 → 服务注册 → 服务注册 → 服务注册 → 修改目录属主为Administrator → 修改目录属主为Administrator → 修改目录属主为Administrator → 修改目录属主为Administrator → Config.csv配置文件更新 → Config.csv配置文件更新 → Config.csv配置文件更新 → Config.csv配置文件更新 → Station下的5个csv文件更新 → Station下的5个csv文件更新 → Station下的5个csv文件更新 → Station下的5个csv文件更新 → Schema下四个xml文件更新 → Schema下四个xml文件更新 → Schema下四个xml文件更新 → Schema下四个xml文件更新 → game目录下tlog_cfg.xml更新 → game目录下tlog_cfg.xml更新 → game目录下tlog_cfg.xml更新 → game目录下tlog_cfg.xml更新 → InitConfig.ini更新 → InitConfig.ini更新 → InitConfig.ini更新 → InitConfig.ini更新 → 结束
```

**流程 2**（32 个节点）:
```
开始 → [并行] → tcm-xml和bkcc的ds机器比较 → tcm-xml和bkcc的ds机器比较 → tcm-xml和bkcc的ds机器比较 → tcm-xml和bkcc的ds机器比较 → dfw和bkcc的ds机器比较 → dfw和bkcc的ds机器比较 → dfw和bkcc的ds机器比较 → dfw和bkcc的ds机器比较 → 查询是否为故障机 - 地域A → 查询是否为故障机 - 地域B → 查询是否为故障机 - 地域C → 查询是否为故障机 - 地域D → dfw和故障机比较 → dfw和故障机比较 → dfw和故障机比较 → dfw和故障机比较 → 上报监控指标 - 地域A → 上报监控指标 - 地域B → 上报监控指标 - 地域C → 上报监控指标 - 地域D → 上报监控事件 - 地域A → 上报监控事件 - 地域B → 上报监控事件 - 地域C → 上报监控事件 - 地域D → 向 ds热更审核 推送消息 → 向 ds热更审核 推送消息 → 向 ds热更审核 推送消息 → 向 ds热更审核 推送消息 → 对比是否成功 → 对比是否成功 → 对比是否成功 → 对比是否成功 → [汇聚] → 结束
```

**流程 3**（30 个节点）:
```
开始 → 【TCM】检查TCM是否在使用中并加锁 → 实例id参数重载 → 实例参数优化 → 【TCM】释放锁 → QA审核 → 【通用】告警屏蔽 → 等待玩家退出 → 检查ds服务器对局数为0 → 开发审批停服确认 → 【TCM】检查TCM是否在使用中并加锁 → stop进程 → [条件] → [汇聚] → 释放TCM使用标识退出 → 等待30s → 确认停服成功 → stop 执行成功 → kill ds 的 father 进程 → 清理 ramfs 目录 → 解压缩 → [条件] → [汇聚] → 释放TCM使用标识退出 → Genshell → [条件] → [汇聚] → 释放TCM使用标识退出 → 开发审批起服确认 → start进程 → [条件] → 释放TCM使用标识退出 → start 执行成功 → start 执行失败 → [汇聚] → 查找进程主机信息 → 【TCM】释放锁 → 开发确认现网情况 → 【公共模板】解除告警屏蔽 → 结束
```

**流程 4**（24 个节点）:
```
开始 → [并行] → 打包user00目录 → 安装boto3 → [汇聚] → 安装tcm_filter需要的包 → 分发 → tcm-user00目录初始化 → 解压打包文件 → 运维机生成初始化包 → 暂停 → 解压初始化打包文件 → 启动tcm → 将tcm_filter目录放置在正确目录下 → 屏蔽tagent-cron告警 → 更新tagent.xml → 新tcm机器检查agent → 解除屏蔽 → 更新tmonitr注册IP → 创建tmobitor任务测试是否通信正常 → 启动proc相关的定时任务 → [条件] → 启动tcm_filter → 继续 → 启动filter监控 → [汇聚] → 根据环境对应实际情况修改nonstop上的转发配置 → 清理旧机器定时任务 → 停止tcm进程 → 结束
```

**流程 5**（21 个节点）:
```
开始 → 临时大区基本信息确认 → 暂停 → 暂停 → 确认修改临时大区配置 → 暂停 → 暂停 → 暂停 → 暂停 → 暂停 → 暂停 → 暂停 → 暂停 → 暂停 → 暂停 → 暂停 → 暂停 → 暂停 → 暂停 → 暂停 → 暂停 → 暂停 → 结束
```

**流程 6**（17 个节点）:
```
开始 → BK-消息通知 → 暂停 → 创建zonesvr进程配置 → 下发zonesvr进程配置 → 重启zonesvr进程 → 审核 → 暂停 → BK-消息通知 → 暂停 → 【现网】生成zonesvr配置文件 → 【游客服】下发zonesvr配置文件 → 【游客服】重启zonesvr → 暂停 → 【正式服】下发zonesvr配置文件 → 【正式服】灰度重启zonesvr → 【正式服】重启zonesvr → BK-消息通知 → 结束
```

**流程 7**（16 个节点）:
```
开始 → 全量备份cfg.json → 环境A-预发布审核 → 环境A-预发布业务接入执行 → 环境A-预发布业务接入检查 → 环境A-正式发布审核（第一批） → 环境A-正式发布业务接入执行（第一批） → 环境A-正式发布业务接入检查（第一批） → 环境A-正式发布审核（第二批） → 环境A-正式发布业务接入执行（第二批） → 环境A-正式发布业务接入检查（第二批） → 环境A-正式发布审核（第三批） → 环境A-正式发布业务接入执行（第三批） → 环境A-正式发布业务接入检查（第三批） → 环境A-正式发布审核（第四批） → 环境A-正式发布业务接入执行（第四批） → 环境A-正式发布业务接入检查（第四批） → 结束
```

**流程 8**（15 个节点）:
```
开始 → qq服stop停服 → wx服stop停服 → 人工确认 → 备份 tcm 文件 → 人工确认 → sq分发本地文件 → wx分发本地文件 → 人工确认 → qq服刷新tbus → qq服启动 → 人工确认 → wx服刷新tbus → wx服启动 → 人工确认 → 给服务质量用 → 结束
```

---

## 通用模式

### 常见标准子流程

**1. TCM 标准部署序列**
```
TCM检查配置(checkconf) → TCM禁用autoload(disable) → TCM安装版本(install) → TCM启用autoload(enable) → 人工确认
```

**2. TCM 配置下发序列**
```
人工确认 → TCM配置下发 → TCM检查配置 → 人工确认 → 通知
```

**3. 批量刷档序列**
```
备份当前配置 → [并行] → 刷档区服A | 刷档区服B → [汇聚] → 检查配置一致性 → 通知
```

---

## 核心组件

| 组件 | 说明 | 使用场景 | 使用次数 |
|------|------|---------|--------|
| `job_fast_execute_script` | 快速脚本执行 | 通过 JOB 平台快速执行 Shell/Python 脚本 | 258 |
| `job_execute_task` | JOB 作业执行 | 执行 JOB 平台预定义的作业模板 | 220 |
| `remote_plugin` | 蓝鲸标准插件调用 | 调用蓝鲸标准插件（DBM/AI/BKChat 等） | 115 |
| `pause_node` | 人工确认/暂停 | 流程暂停等待人工确认后继续 | 68 |
| `tcm_execute_task` | TCM 配置管理 | 执行 TCM 配置检查/安装/启用/禁用 | 44 |
| `job_fast_push_file` | 快速文件分发 | 通过 JOB 快速推送文件到目标机器 | 41 |
| `job_push_local_files` | 本地文件推送 | 推送本地文件到远程机器 | 31 |
| `sleep_timer` | 定时等待 | 流程等待指定时间后继续 | 18 |
| `bk_notify` | 蓝鲸通知 | 发送邮件/短信/微信通知 | 18 |
| `bk_approve` | 审批节点 | 流程审批确认 | 11 |
| `wechat_work_send_message` | 企业微信消息 | 发送企业微信群/个人消息 | 8 |
| `gsekit_job_exec` | GseKit 进程管理 | 通过 GseKit 执行进程启停操作 | 7 |
| `server_file_dispatch` | 服务端文件分发 | 分发服务端版本包到目标机器 | 6 |
| `all_biz_job_fast_execute_script` | all_biz_job_fast_execute_script | all_biz_job_fast_execute_script | 5 |
| `sa_create_task` | SA 任务创建 | 创建 SA 工单任务 | 5 |

## 核心插件

| 插件 | 说明 | 使用场景 | 使用次数 |
|------|------|---------|--------|
| `bkchat-sops` | BKChat 集成 | 蓝鲸 ChatOps 消息交互 | 23 |
| `tcompose-exec` | TCompose 执行 | 执行容器编排任务 | 18 |
| `bksops-itsm` | ITSM 对接 | 与 ITSM 工单系统对接 | 13 |
| `bkchat-csutomsg` | bkchat-csutomsg | bkchat-csutomsg | 9 |
| `bkm-dimension` | bkm-dimension | bkm-dimension | 8 |
| `bot-approval` | 机器人审批 | 通过企业微信机器人发起审批 | 6 |
| `ai-common-cfgc` | ai-common-cfgc | ai-common-cfgc | 5 |
| `ai-tcm-topo-c` | ai-tcm-topo-c | ai-tcm-topo-c | 4 |
| `devops-pl-plugin` | 蓝盾流水线 | 触发蓝盾 CI/CD 流水线 | 4 |
| `bkchat-sops-send` | BKChat 消息发送 | 发送消息到企业微信群 | 4 |

---

## 关键参数

### 组件参数

| 参数 | 所属组件 | 说明 | 示例值                               |
|------|---------|------|-----------------------------------|
| `biz_cc_id` | 快速脚本执行 | biz_cc_id | -                                 |
| `job_account` | 快速脚本执行 | job_account | root                              |
| `job_content` | 快速脚本执行 | job_content | -                                 |
| `job_ip_list` | 快速脚本执行 | job_ip_list | ${ip_list}                        |
| `job_script_param` | 快速脚本执行 | job_script_param | ${name}  ${the_key}  ${the_value} |
| `job_task_id` | JOB 作业执行 | job_task_id | -                                 |
| `button_refresh` | JOB 作业执行 | button_refresh | -                                 |
| `job_global_var` | JOB 作业执行 | job_global_var | -                                 |
| `button_refresh_2` | JOB 作业执行 | button_refresh_2 | -                                 |
| `bk_receiver_group` | 蓝鲸标准插件调用 | bk_receiver_group | -                                 |
| `message_content` | 蓝鲸标准插件调用 | message_content | -                                 |
| `msg_type` | 蓝鲸标准插件调用 | msg_type | -                                 |
| `description` | 人工确认/暂停 | description | ${config_type}                    |
| `tcm_app_id` | TCM 配置管理 | tcm_app_id | ${tcm_app_id}                     |
| `tcm_executor` | TCM 配置管理 | tcm_executor | xxx                               |
| `tcm_fail_ignore` | TCM 配置管理 | tcm_fail_ignore | -                                 |
| `tcm_template_id` | TCM 配置管理 | tcm_template_id | ${tcm_template_id}                |
| `tcm_workjson` | TCM 配置管理 | tcm_workjson | -                                 |
| `job_source_files` | 快速文件分发 | job_source_files | -                                 |
| `job_timeout` | 快速文件分发 | job_timeout | 120                               |

### 流程变量

| 变量 | 名称 | 来源类型 | 出现次数 |
|------|------|---------|--------|
| `${tcm_ip}` | tcm机器 | custom | 26 |
| `${task_start_time}` | 任务起始时间 | custom | 23 |
| `${log_outputs}` | JOB全局变量 | component_outputs | 22 |
| `${task_end_time}` | 任务结束时间 | custom | 20 |
| `${job_ip_list}` | Job-快速执行脚本 | custom | 18 |
| `${job_local_files}` | 本地文件 | component_inputs | 18 |
| `${env}` | 服务环境 | custom | 12 |
| `${job_local_files_info}` | 上传文件 | component_inputs | 9 |
| `${ywj}` | 运维机IP | custom | 8 |
| `${iplist}` | 执行ip | custom | 8 |
| `${job_target_ip_list}` | Job- | custom | 8 |
| `${output}` | Output | component_outputs | 7 |
| `${_result}` | 执行结果 | component_outputs | 7 |
| `${bk_timing}` | 定时时间 | component_inputs | 6 |
| `${chat_id}` | 群会话ID | custom | 6 |

---

## 网关使用

| 网关类型 | 使用次数 | 说明 |
|---------|---------|------|
| ParallelGateway | 19 | 并行执行所有分支 |
| ExclusiveGateway | 48 | 条件选择单一分支 |
| ConvergeGateway | 61 | 等待所有并行分支完成 |
| ConditionalParallelGateway | 5 | 满足条件的分支并行执行 |

---

## 检查清单

| 检查项 | 说明 | 严重程度 |
|--------|------|--------|
| 🔴 TCM 标准序列 | 是否遵循 checkconf → disable → install → enable 标准序列 | 高 |
| 🔴 配置校验 | 推送后是否有配置正确性校验 | 高 |
| 🟡 版本 diff | 是否有配置版本 diff 对比 | 中 |
| 🟡 回滚能力 | 是否有配置回滚机制 | 中 |
| 🟢 多环境同步 | 是否支持跨环境配置同步 | 低 |