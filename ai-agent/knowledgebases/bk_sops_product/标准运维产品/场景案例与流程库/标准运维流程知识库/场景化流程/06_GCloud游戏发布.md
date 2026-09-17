# GCloud游戏发布

> 基于 GCloud 平台的游戏发布与版本管理。包括正式发布、预发布、资源包上传、区服导航管理、开区审批等。
>
> **363** 条流程 | 平均节点数基于采样分析

---

## 关键检查点

1. 必须使用 GCloud 标准组件完成发布流程（当前采用率 60%）
2. 发布期间必须屏蔽告警（当前采用率 2%）
3. GCloud 发布前必须有人工确认（当前采用率 4%）
4. 发布前区服入口变灰 → 操作 → 变绿（当前采用率 0%）
5. 版本文件分发后做 MD5 校验（当前采用率 3%）
6. 发布完成后发送通知（当前采用率 20%）
---
## 代表性流程图

**流程 1**（61 个节点）:
```
开始 → 清档前检查 → 蓝鲸监控告警屏蔽 → 发送开服预告至xxx运维群 → 获取新服gcloud的父节点id → 获取新服gcloud的节点id → 新服清档（提单） → 通知 → 新服清档（审批 通知xxx过单） → Webplat-新增区服 → Webplat-发布大区 → 定时三分钟等待ams发布 → 新服ams配置检查 → 通知 → Timer-定时器（开服时间40分钟前执行) → 修改大区隐藏属性_ch1 → 修改大区隐藏属性_ch2 → 修改大区隐藏属性_ch3 → 修改大区隐藏属性_ch4 → 通知 → 通知 → 停指定服world进程 → 新服清档（执行） → 保留表检查 → 检查清档是否成功 → 新服起进程 → 检查进程是否启动 → 检查封印等级 → 获取所有带新荐标注的区服ids → 取消新荐标注_ch3 → 取消新荐标注_ch4 → 取消新荐标注_ch1 → 取消新荐标注_ch2 → [并行] → 新服入口变亮_ch2 → 获取保留旧服gcloud的节点id → 新服入口变亮_ch3 → 保留服设置新标签_ch1 → 新服入口变亮_ch4 → 保留服设置新标签_ch3 → 新服入口变亮_ch1 → 保留服设置新标签_ch4 → 新服设置新标签_ch1 → 保留服设置新标签_ch2 → 新服设置新标签_ch3 → [汇聚] → 新服设置新标签_ch4 → 预发布大区_ch1 → 新服设置新标签_ch2 → 预发布大区_ch2 → 结束
```

**流程 2**（53 个节点）:
```
开始 → [并行] → APK文件分发_非灰度 → APK文件分发_灰度 → [汇聚] → [并行] → 资源文件分发_非灰度 → 资源文件分发_非灰度 → 资源文件分发_灰度 → [汇聚] → [并行] → 获取ch4_list → 获取ch3_list → 获取ch1_list → 获取ch2_list → [汇聚] → [并行] → 更新大区状态aqq → 更新大区状态iwx → 更新大区状态awx → 更新大区状态iqq → [汇聚] → [并行] → 预发布大区aqq → 预发布大区iwx → 预发布大区awx → 预发布大区iqq → [汇聚] → [并行] → 发布大区awx → 发布大区iwx → 发布大区aqq → 发布大区iqq → [汇聚] → 暂停 → [并行] → 创建程序版本_非灰度 → 创建程序版本_非灰度 → 创建程序版本_灰度 → [汇聚] → [并行] → 创建资源版本_灰度 → 创建资源版本_非灰度 → 创建资源版本_非灰度 → [汇聚] → [并行] → APK不可用版本_非灰度 → APK不可用版本_非灰度 → APK不可用版本_灰度 → [汇聚] → 结束
```

**流程 3**（28 个节点）:
```
开始 → 加文件锁 → 根据小区ID获取wid、zid、last_areazoneid → 修改proc_deploy.xml开服时间和白名单 → 生成推送配置 → 释放文件锁 → [并行] → 批量更新区服隐藏状态1大区 → 批量更新区服隐藏状态3大区 → 批量更新区服隐藏状态4大区 → 批量更新区服隐藏状态2大区 → [汇聚] → [并行] → 批量更新区服标注3大区 → 批量更新区服标注1大区 → 批量更新区服标注4大区 → 批量更新区服标注2大区 → [汇聚] → [并行] → 批量更新区服状态1大区 → 批量更新区服状态4大区 → 更新区服状态2大区 → 批量更新区服状态3大区 → [汇聚] → [并行] → 预发布大区3 → 预发布大区2 → 预发布大区4 → 预发布大区1 → [汇聚] → 新区对外开放定时 → [并行] → 发布大区4 → 发布大区2 → 发布大区3 → 发布大区1 → [汇聚] → 修改CC雪球开服时间、加推荐标志 → 消息提醒 → 结束
```

**流程 4**（22 个节点）:
```
开始 → 蓝鲸监控告警屏蔽 → FTP分发服务端版本文件 → 维护 → 限 → 白名单不隐藏 → 预发布大区 → 发布大区 → 取消托管 → 停服 → 服务端文件更新 → 暂停 → 起服 → 托管 → 繁忙 → 热 → 预发布大区 → 发布大区 → 暂停 → 不隐藏 → 预发布大区 → 发布大区 → 解除告警屏蔽 → 结束
```

**流程 5**（18 个节点）:
```
开始 → 服务端文件分发 → tcm_template更新 → 服务端版本校验 → 停进程world → 停全局进程（IDC） → 停cluster级别进程 → tcm_tool更新 → del_map → 版本更新 → 刷配置（world） → 刷新全局进程（IDC） → 刷cluster级别进程 → 服务端版本号修改 → 测试服修改tconnd配置 → 启动cluster级别进程 → 起全局进程（IDC） → 起进程（world） → 测试群通知 → 结束
```

**流程 6**（17 个节点）:
```
开始 → 参数解析 → [条件] → 蓝盾执行流水线资源发布 → bkchat通用开发商 → [条件] → [汇聚] → bkchat通用开发商 → [并行] → 结束 → BkChat通知运维 → qa2发布单个渠道 → qa发布单个渠道 → stag发布单个渠道 → qa4发布单个渠道 → qa3发布单个渠道 → [汇聚] → 添加dolphin版本号信息 → 添加dolphin版本号信息 → 添加dolphin版本号信息 → 添加dolphin版本号信息 → 添加dolphin版本号信息 → [汇聚] → bkchat通用开发商 → BkChat通知运维 → 结束
```

**流程 7**（16 个节点）:
```
开始 → [并行] → 发送通知 → 发送通知 → 暂停 → 暂停 → 批量更新区服状态（渠道A) → 批量更新区服状态（渠道B） → 批量更新区服状态（渠道A) → 批量更新区服状态（渠道D） → [并行] → [并行] → ch3预发布大区 → ch1预发布大区 → ch2预发布大区 → ch4预发布大区 → ch3发布大区 → ch1发布大区 → ch2发布大区 → ch4发布大区 → [汇聚] → [汇聚] → [汇聚] → 结束
```

**流程 8**（14 个节点）:
```
开始 → CC脚本获取已对外小区集群ID → 批量更新区服状态-微信安卓-维护 → 预发布大区 → 发布大区 → 批量更新区服状态-微信IOS-维护 → 预发布大区 → 发布大区 → 批量更新区服状态-QQ安卓-维护 → 预发布大区 → 发布大区 → 批量更新区服状态-QQIOS-维护 → 预发布大区 → 发布大区 → 发送通知 → 结束
```

---

## 通用模式

### 常见标准子流程

**1. GCloud 标准发布序列**
```
GCloud创建资源版本 → GCloud预发布渠道 → GCloud取消旧版本 → GCloud同步区服信息 → GCloud批量更新区服状态（维护） → GCloud预发布大区 → GCloud发布大区 → GCloud批量更新区服状态（正常）
```

**2. 多渠道并行发布**
```
[并行] → GCloud安卓发布 | GCloud苹果发布 | GCloud WeGame发布 → [汇聚] → 通知
```

**3. 区服状态管理序列**
```
GCloud批量更新区服状态（维护） → 执行发布操作 → GCloud批量更新区服状态（正常）
```

---

## 核心组件

| 组件 | 说明 | 使用场景 | 使用次数 |
|------|------|---------|--------|
| `gcloud_pre_publish` | GCloud 预发布 | GCloud 平台预发布操作 | 75 |
| `job_execute_task` | JOB 作业执行 | 执行 JOB 平台预定义的作业模板 | 69 |
| `gcloud_publish` | GCloud 正式发布 | GCloud 平台正式发布操作 | 68 |
| `job_fast_execute_script` | 快速脚本执行 | 通过 JOB 平台快速执行 Shell/Python 脚本 | 64 |
| `gcloud_batch_update_node_flag` | GCloud 批量更新 | GCloud 批量更新区服标记 | 53 |
| `remote_plugin` | 蓝鲸标准插件调用 | 调用蓝鲸标准插件（DBM/AI/BKChat 等） | 44 |
| `gcloud_batch_update_node_tag` | gcloud_batch_update_node_tag | gcloud_batch_update_node_tag | 32 |
| `gcloud_publish_product` | gcloud_publish_product | gcloud_publish_product | 30 |
| `gcloud_batch_update_node_hide_status` | gcloud_batch_update_node_hide_status | gcloud_batch_update_node_hide_status | 29 |
| `bk_notify` | 蓝鲸通知 | 发送邮件/短信/微信通知 | 23 |
| `gcloud_update_version` | gcloud_update_version | gcloud_update_version | 22 |
| `sleep_timer` | 定时等待 | 流程等待指定时间后继续 | 21 |
| `gcloud_pre_publish_product` | gcloud_pre_publish_product | gcloud_pre_publish_product | 20 |
| `pause_node` | 人工确认/暂停 | 流程暂停等待人工确认后继续 | 18 |
| `gcloud_new_app` | gcloud_new_app | gcloud_new_app | 15 |

## 核心插件

| 插件 | 说明 | 使用场景 | 使用次数 |
|------|------|---------|--------|
| `bkchat-sops` | BKChat 集成 | 蓝鲸 ChatOps 消息交互 | 10 |
| `devops-pl-plugin` | 蓝盾流水线 | 触发蓝盾 CI/CD 流水线 | 7 |
| `bkchat-sops-send` | BKChat 消息发送 | 发送消息到企业微信群 | 6 |
| `gcloud-xxx` | gcloud-xxx | gcloud-xxx | 4 |
| `tcompose-exec` | TCompose 执行 | 执行容器编排任务 | 2 |
| `bkchat-broadcast` | BKChat 广播 | 群发广播消息 | 2 |
| `ai-glog-ans-prod` | ai-glog-ans-prod | ai-glog-ans-prod | 2 |
| `bot-approval` | 机器人审批 | 通过企业微信机器人发起审批 | 2 |
| `chaos-atom` | 混沌工程 | 执行混沌工程故障注入 | 2 |
| `gcloud-new` | gcloud-new | gcloud-new | 2 |

---

## 关键参数

### 组件参数

| 参数 | 所属组件 | 说明 | 示例值 |
|------|---------|------|--------|
| `gcloud_access_id` | GCloud 预发布 | gcloud_access_id | xxx |
| `gcloud_access_key` | GCloud 预发布 | gcloud_access_key | xxx |
| `gcloud_game_id` | GCloud 预发布 | gcloud_game_id | ${gcloud_game_id} |
| `gcloud_platform_id` | GCloud 预发布 | gcloud_platform_id | ${result_vars["gcloud_xxx_area_id"]} |
| `gcloud_region` | GCloud 预发布 | gcloud_region | ${gcloud_region} |
| `biz_cc_id` | JOB 作业执行 | biz_cc_id | - |
| `button_refresh` | JOB 作业执行 | button_refresh | - |
| `job_global_var` | JOB 作业执行 | job_global_var | - |
| `job_task_id` | JOB 作业执行 | job_task_id | - |
| `ip_is_exist` | JOB 作业执行 | ip_is_exist | - |
| `job_account` | 快速脚本执行 | job_account | ${job_account} |
| `job_content` | 快速脚本执行 | job_content | - |
| `job_ip_list` | 快速脚本执行 | job_ip_list | ${ip_list} |
| `job_script_param` | 快速脚本执行 | job_script_param | ${android_area} |
| `gcloud_node_flag` | GCloud 批量更新 | gcloud_node_flag | unavailable |
| `gcloud_node_ids` | GCloud 批量更新 | gcloud_node_ids | ${result_vars["gcloud_xxx_node_ids"]} |
| `msg_type` | 蓝鲸标准插件调用 | msg_type | - |
| `receivers` | 蓝鲸标准插件调用 | receivers | - |
| `bk_receiver_group` | 蓝鲸标准插件调用 | bk_receiver_group | - |
| `gcloud_node_tag` | gcloud_batch_update_node_tag | gcloud_node_tag | ${gcloud_node_tag} |

### 流程变量

| 变量 | 名称 | 来源类型 | 出现次数 |
|------|------|---------|--------|
| `${gcloud_game_id}` | 游戏ID | component_inputs | 50 |
| `${gcloud_access_id}` | 访问账号 | component_inputs | 49 |
| `${gcloud_access_key}` | 访问密码 | component_inputs | 49 |
| `${gcloud_platform_id}` | GCloud-大区ID | component_inputs | 25 |
| `${log_outputs}` | JOB全局变量 | component_outputs | 19 |
| `${task_start_time}` | 任务起始时间 | custom | 18 |
| `${task_end_time}` | 任务结束时间 | custom | 17 |
| `${gcloud_region}` | 区域 | component_inputs | 13 |
| `${gcloud_product_id}` | 渠道ID(Android) | component_inputs | 12 |
| `${setid}` | 大区列表 | custom | 9 |
| `${gcloud_version_str}` | Gcloud-版本号 | component_inputs | 8 |
| `${gcloud_node_flag}` | GCloud-小区状态 | component_inputs | 7 |
| `${yw_ip}` | yw_ip | custom | 5 |
| `${job_ip_list}` | Job-快速执行脚本 | custom | 5 |
| `${gcloud_res_version_str}` | 非灰度资源版本号(android) | component_inputs | 5 |

---

## 网关使用

| 网关类型 | 使用次数 | 说明 |
|---------|---------|------|
| ParallelGateway | 37 | 并行执行所有分支 |
| ExclusiveGateway | 14 | 条件选择单一分支 |
| ConvergeGateway | 56 | 等待所有并行分支完成 |
| ConditionalParallelGateway | 5 | 满足条件的分支并行执行 |

---

## 检查清单

| 检查项 | 说明 | 严重程度 |
|--------|------|--------|
| 🔴 区服导航同步 | 操作后是否同步更新区服导航 | 高 |
| 🔴 版本状态管理 | 发布后是否设置版本可用/不可用状态 | 高 |
| 🟡 配置备份 | 变更前是否备份 GCloud 配置 | 中 |
| 🟡 审批确认 | 发布/开区是否有审批确认 | 中 |
| 🟡 多渠道覆盖 | 是否同时处理多个渠道的发布 | 中 |