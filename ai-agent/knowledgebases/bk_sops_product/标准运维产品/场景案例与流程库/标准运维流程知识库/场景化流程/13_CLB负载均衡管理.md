# CLB负载均衡

> CLB 规则管理。包括 RS 上下线、权重调整、端口管理、规则查询与备份等。
>
> **734** 条流程 | 平均节点数基于采样分析

---

## 关键检查点

1. 必须使用标准 CLB 组件操作（当前采用率 46%）
2. CLB 变更前必须有人工确认（当前采用率 4%）
3. CLB 变更后必须验证连通性（当前采用率 0%）
4. CLB 变更完成后发送通知（当前采用率 11%）
5. CLB 操作前必须查询当前 CLB 规则并备份，操作完成后需验证 CLB 规则状态（对比变更前后）
---
## 代表性流程图

**流程 1**（25 个节点）:
```
开始 → 批量绑定安全组 2.0 → 获取原先的hostname → 临时修改主机名称 → [并行] → 获取分配的Vport → 获取分配的Vport → 获取分配的Vport → 定时60S → 定时30S → 定时5S → 相关人员 clb 规则上线 2.0 → 相关人员 clb 规则上线 2.0 → 相关人员 clb 规则上线 2.0 → 更新Vport记录 → 更新Vport记录 → 检查是否存在lobby目录 → CLB规则信息通知 → CLB规则信息通知 → lobby_check文件分发 → DS XML配置文件生成 → RouteTrip XML配置文件生成 → 生成lobby-clb规则文件 → [汇聚] → lobby-clb规则检查 → 回退主机名称 → 更新Vport记录 → 结束 → CLB规则信息通知 → 结束
```

**流程 2**（24 个节点）:
```
开始 → 用户信息搜集 → 规则类型 → [条件] → 执行封禁 → 是否合规（暂停） → [汇聚] → [条件] → 结束 → 用户信息二次确认 → 用户信息二次确认 → 客户整改 → 客户整改（24h） → [汇聚] → 客户整改（24h） → 用户信息二次确认 → 用户信息二次确认 → 执行封禁 → 执行封禁 → 是否合规（操作） → 是否合规（操作） → 是否合规（操作） → 执行封禁 → 执行封禁 → [条件] → [条件] → [条件] → 用户信息二次确认 → [汇聚] → 用户信息二次确认 → [汇聚] → 用户信息二次确认 → [汇聚] → 执行封禁 → 执行封禁 → 执行封禁 → 结束
```

**流程 3**（22 个节点）:
```
开始 → 获取clb规则 → 查询负载均衡列表 → [条件] → [条件] → 查询负载均衡列表（地域B） → [条件] → [条件] → [条件] → 调整RS权重-HTTPHTTPS → 暂停（检查规则是否已存在） → 追加RS-HTTPS → 调整RS权重-UDP → 调整RS权重-TCP → 暂停（手动在页面解绑RS） → [条件] → [条件] → 删除监听器-UDP → 删除监听器-TCP → [条件] → 规则上线-udp-新 → 规则上线-tcp-新 → 结束 → 追加RS-HTTPS → [条件] → [条件] → 调整RS权重-HTTPHTTPS → [条件] → [条件] → 调整RS权重-UDP → 调整RS权重-TCP → 暂停（手动在页面解绑RS） → 地域B - 规则上线-udp-新 → 地域B - 规则上线-tcp-新 → 删除监听器-UDP → 删除监听器-TCP → 结束
```

**流程 4**（20 个节点）:
```
开始 → 地域A 查询RSIP TCP → 消息展示 → 人工确认 → 地域A 解绑RS-TCP → 地域A 查询RSIP UDP → 消息展示 → 人工确认 → 地域A 解绑RS-UDP → 地域B 查询RSIP TCP → 消息展示 → 地域B 解绑RS-TCP → 地域B 查询RSIP UDP → 消息展示 → 地域B 解绑RS-UDP → 地域C 查询RSIP TCP → 消息展示 → 地域C 解绑RS-TCP → 地域C 查询RSIP UDP → 消息展示 → 地域C 解绑RS-UDP → 结束
```

**流程 5**（20 个节点）:
```
开始 → [并行] → 循环开始通知 → 循环开始通知 → 循环开始通知 → 循环开始通知 → 输出本次参数 → 输出本次参数 → 输出本次参数 → 输出本次参数 → 检查负载均衡安全组是否与预设相同 → 检查负载均衡安全组是否与预设相同 → 检查负载均衡安全组是否与预设相同 → 检查负载均衡安全组是否与预设相同 → [条件] → [条件] → [条件] → [条件] → [汇聚] → 通知存在多或少安全组绑定的负载均衡 → 通知存在多或少安全组绑定的负载均衡 → [汇聚] → [汇聚] → 通知存在多或少安全组绑定的负载均衡 → 通知存在多或少安全组绑定的负载均衡 → [汇聚] → [条件] → [条件] → [条件] → [条件] → 结束通知 → 结束通知 → 结束通知 → 结束通知 → [汇聚] → 结束
```

**流程 6**（20 个节点）:
```
开始 → SA-初始化_xxx_init → [并行] → SA-初始化_install_L5AGENT → SA-初始化_yum_source_update → SA-初始化_install_ldap → [汇聚] → 安装gseagent → 合服机-重新分发tools监控管理脚本 → 获取主机名 → 修改主机名称 → 服务器初始化 → 调整新服脚本位置 → 从xxx分发start.sh → [并行] → 打包旧服务器 → 快速分发文件 → 解压初始化 → 解压初始化 → 建立日志软连 → 建立日志软连 → [汇聚] → 定时任务添加 → 修改本机ip配置 → 服务器初始化环境 -- 修改odbc.ini软连接 → 结束
```

**流程 7**（19 个节点）:
```
开始 → [并行] → 循环开始通知 → 循环开始通知 → 循环开始通知 → 循环开始通知 → 循环开始通知 → 循环开始通知 → 输出本次参数 → 输出本次参数 → 输出本次参数 → 输出本次参数 → 输出本次参数 → 输出本次参数 → 地域A-ds → 地域B-ds → 地域C-ds → 地域D-lobby → 地域E-ds → 地域F-ds → [条件] → [条件] → [条件] → [条件] → [条件] → [条件] → [汇聚] → [汇聚] → [汇聚] → [汇聚] → [汇聚] → [汇聚] → [汇聚] → 全体结束通知 → 结束
```

**流程 8**（19 个节点）:
```
开始 → 蓝鲸监控指标上报 → 定时1分钟 → 蓝鲸监控指标上报 → 定时1分钟 → 蓝鲸监控指标上报 → 定时1分钟 → 蓝鲸监控指标上报 → 定时1分钟 → 蓝鲸监控指标上报 → 定时1分钟 → 蓝鲸监控指标上报 → 定时1分钟 → 蓝鲸监控指标上报 → 定时1分钟 → 蓝鲸监控指标上报 → 定时1分钟 → 蓝鲸监控指标上报 → 定时1分钟 → 蓝鲸监控指标上报 → 结束
```

---

## 通用模式

### 常见标准子流程

**1. RS 上线标准流程**
```
CLB查询RS列表 → 添加RS（clb_add_rs） → 设置初始权重 → 逐步提升权重 → 人工确认 → 验证连通性
```

**2. RS 下线标准流程**
```
CLB修改权重为0 → 等待连接排空 → CLB移除RS → 人工确认
```

**3. 权重调整序列**
```
CLB查询当前权重 → CLB修改权重（批次1） → 人工确认 → CLB修改权重（批次2） → 人工确认 → CLB恢复全量权重 → 通知
```

**4. 监听器管理流程**
```
CLB创建监听器 → 配置转发规则 → 绑定RS → 健康检查配置 → 验证
```

---

## 核心组件

| 组件 | 说明 | 使用场景 | 使用次数 |
|------|------|---------|--------|
| `remote_plugin` | 蓝鲸标准插件调用 | 调用蓝鲸标准插件（DBM/AI/BKChat 等） | 280 |
| `job_fast_execute_script` | 快速脚本执行 | 通过 JOB 平台快速执行 Shell/Python 脚本 | 101 |
| `clb_del_rs` | clb_del_rs | clb_del_rs | 67 |
| `clb_modify_weight` | clb_modify_weight | clb_modify_weight | 48 |
| `clb_add_rule` | clb_add_rule | clb_add_rule | 39 |
| `bk_notify` | 蓝鲸通知 | 发送邮件/短信/微信通知 | 37 |
| `job_execute_task` | JOB 作业执行 | 执行 JOB 平台预定义的作业模板 | 36 |
| `bk_http_request` | HTTP 请求 | 发送 HTTP/HTTPS 请求调用外部 API | 32 |
| `pause_node` | 人工确认/暂停 | 流程暂停等待人工确认后继续 | 26 |
| `sleep_timer` | 定时等待 | 流程等待指定时间后继续 | 19 |
| `clb_add_rs` | clb_add_rs | clb_add_rs | 15 |
| `wechat_work_send_message` | 企业微信消息 | 发送企业微信群/个人消息 | 11 |
| `bk_display` | 消息展示 | 在流程中展示信息供查看 | 9 |
| `clb_del_rule` | clb_del_rule | clb_del_rule | 7 |
| `job_fast_push_file` | 快速文件分发 | 通过 JOB 快速推送文件到目标机器 | 5 |

## 核心插件

| 插件 | 说明 | 使用场景 | 使用次数 |
|------|------|---------|--------|
| `hcm-lbl-rs-tcp` | HCM TCP RS | 管理 CLB TCP RS 上下线 | 45 |
| `hcm-clb-query` | HCM CLB 查询 | 查询 CLB 规则和 RS 信息 | 34 |
| `clb-copy` | clb-copy | clb-copy | 28 |
| `bkm-reporter` | bkm-reporter | bkm-reporter | 24 |
| `hcm-weight-four` | HCM 四层权重 | 管理 CLB 四层 RS 权重 | 19 |
| `bkchat-sops` | BKChat 集成 | 蓝鲸 ChatOps 消息交互 | 13 |
| `hcm-rs-offline` | hcm-rs-offline | hcm-rs-offline | 13 |
| `tcompose-lbcopy` | tcompose-lbcopy | tcompose-lbcopy | 11 |
| `hcm-lbl-rs-http` | hcm-lbl-rs-http | hcm-lbl-rs-http | 10 |
| `hcm-lbl-del` | hcm-lbl-del | hcm-lbl-del | 8 |

---

## 关键参数

### 组件参数

| 参数 | 所属组件 | 说明 | 示例值 |
|------|---------|------|--------|
| `account_id` | 蓝鲸标准插件调用 | account_id | xxx |
| `vendor` | 蓝鲸标准插件调用 | vendor | xxx |
| `rule_query_list` | 蓝鲸标准插件调用 | rule_query_list | - |
| `biz_cc_id` | 快速脚本执行 | biz_cc_id | - |
| `job_account` | 快速脚本执行 | job_account | ${job_account} |
| `job_content` | 快速脚本执行 | job_content | - |
| `job_ip_list` | 快速脚本执行 | job_ip_list | ${operation} |
| `job_script_param` | 快速脚本执行 | job_script_param | ${job_local_files_info['job_push_multi_local_files... |
| `clb_input_method` | clb_del_rs | clb_input_method | auto |
| `clb_rules_auto` | clb_del_rs | clb_rules_auto | ${clb_rules_auto} |
| `clb_rules_manual` | clb_del_rs | clb_rules_manual | ${clb_rules_manual} |
| `clb_weight` | clb_modify_weight | clb_weight | ${load} |
| `clb_rule_detail_table` | clb_add_rule | clb_rule_detail_table | ${clb_rule_detail_table} |
| `clb_rule_add_method` | clb_add_rule | clb_rule_add_method | auto |
| `clb_separator` | clb_add_rule | clb_separator | , |
| `bk_notify_content` | 蓝鲸通知 | bk_notify_content | ${bk_notify_content} |
| `bk_notify_title` | 蓝鲸通知 | bk_notify_title | ${bk_notify_title} |
| `bk_notify_type` | 蓝鲸通知 | bk_notify_type | - |
| `bk_receiver_info` | 蓝鲸通知 | bk_receiver_info | - |
| `button_refresh` | JOB 作业执行 | button_refresh | - |

### 流程变量

| 变量 | 名称 | 来源类型 | 出现次数 |
|------|------|---------|--------|
| `${log_outputs}` | JOB全局变量 | component_outputs | 25 |
| `${clb_ids}` | CLB的云实例ID | component_outputs | 24 |
| `${clb_vips}` | CLB的VIP地址或域名 | component_outputs | 24 |
| `${rsip}` | RS_IP | custom | 14 |
| `${rs_ip}` | RS_IP | custom | 14 |
| `${_loop}` | 循环次数 | component_outputs | 12 |
| `${vport}` | VPORT | custom | 11 |
| `${clb_rules_auto}` | clb-规则选择器 | component_inputs | 11 |
| `${rsport}` | RS_PORT | custom | 9 |
| `${task_end_time}` | 任务结束时间 | custom | 9 |
| `${task_start_time}` | 任务起始时间 | custom | 9 |
| `${job_ip_list}` | Job-快速执行脚本 | custom | 8 |
| `${iplist}` | 调整IP | custom | 8 |
| `${region}` | 区域类型 | custom | 7 |
| `${vip}` | 负载均衡VIP | custom | 7 |

---

## 网关使用

| 网关类型 | 使用次数 | 说明 |
|---------|---------|------|
| ParallelGateway | 9 | 并行执行所有分支 |
| ExclusiveGateway | 68 | 条件选择单一分支 |
| ConvergeGateway | 51 | 等待所有并行分支完成 |
| ConditionalParallelGateway | 6 | 满足条件的分支并行执行 |

---

## 检查清单

| 检查项 | 说明 | 严重程度 |
|--------|------|--------|
| 🔴 权重配对 | RS 下线是否有对应的上线/恢复操作 | 高 |
| 🔴 规则备份与验证 | CLB 操作前是否查询并备份当前规则，操作后是否对比变更前后验证规则状态 | 高 |
| 🟡 健康检查 | 操作后是否验证 CLB 健康状态 | 中 |
| 🟡 批量操作 | 批量 RS 操作是否有确认步骤 | 中 |