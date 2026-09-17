# 日志Core处理

> 游戏日志的打包、清理、迁移，以及 coredump 文件的收集、分析、上传。
>
> **818** 条流程 | 平均节点数基于采样分析

---

## 关键检查点

1. 日志处理完成后发送通知（当前采用率 20%）
2. Core 文件分析后需验证结果（当前采用率 0%）
---
## 代表性流程图

**流程 1**（18 个节点）:
```
开始 → [并行] → SA-主机密码修改 → 暂停 → CC-故障机替换 → [汇聚] → [并行] → CC-故障机改为待回收 → 修改主机名 → CC-修改主机自定义属性 → Job-打包传输 → 修改TCM配置 → 暂停 → 暂停-ODM删除旧IP → [汇聚] → [并行] → ODM-新增大区 → Job-环境初始化 → Job-传监控脚本 → TCM-配置刷新 → 授权数据库 → [汇聚] → [并行] → Job-重启tlog进程 → TCM-热启大区进程 → 暂停-域名切换 → [汇聚] → 结束
```

**流程 2**（11 个节点）:
```
开始 → 告警内容解析 → 判断当前corefile是否存在且是否已经写完 → 通过core文件获得对应的exe文件信息 → [条件] → 推送失败信息 → [并行] → 结束 → 将文件发送到备份机 → 文件备份信息推送 → [汇聚] → [条件] → [并行] → 删除复制文件 → 备份成功信息推送 → 在备份机上执行GDB操作 → [汇聚] → gdb相关信息推送 → 推送gdb结果文件 → 结束
```

**流程 3**（11 个节点）:
```
开始 → 生成修改配置 → 审批 → 灰度服务器修改配置 → 审批 → reload灰度 → 审批 → 全量服务器修改配置 → 确认全量操作方式 → [条件] → 全量reload → 全量reloadhost → [汇聚] → 通知完成 → 结束
```

**流程 4**（11 个节点）:
```
开始 → 重载参数 → [并行] → WXxxx大区 → QQ-20个跨区 → WXxxx大区 → WX-前15个跨区 → WXxxx大区 → WX-后15个跨区 → QQxxx大区-10000 → QQxxx大区-20000 → WXxxx大区 → [汇聚] → 【全量日志备份】log_bak服务器上传cos → 结束
```

**流程 5**（11 个节点）:
```
开始 → 获取服务进程运行IP → 输出参数-server_ips → [条件] → 组合抓取日志命令 → 发送错误信息 → 抓取日志-脚本执行 → 结束 → 创建日志保存路径 → 获取日志-接口请求 → 输出参数-all_file_path → 上传cos（蓝鲸ceph） → 输出参数-cos_url → 发送日志消息 → 结束
```

**流程 6**（10 个节点）:
```
开始 → 生成UUID → 汇合最后的 cmd → 日志查找 → ywj 生成接受目录 → 日志文件分发运维机 → 判断是否有日志 → [条件] → BkChat通知插件 → 运维机打包 → 结束 → 日志文件上传COS并生成临时下载链接 → BkChat通知插件 → 结束
```

**流程 7**（10 个节点）:
```
开始 → 获取服务进程运行IP → 输出参数-server_ips → 组合抓取日志命令 → 抓取日志-脚本执行 → 创建日志保存路径 → 获取日志-接口请求 → 输出参数-all_file_path → 上传cos（蓝鲸ceph） → 输出参数-cos_url → 发送日志消息 → 结束
```

**流程 8**（10 个节点）:
```
开始 → 获取服务进程运行IP → 输出参数-server_ips → 抓取日志 → 输出内容 → 创建日志保存路径 → 获取日志-接口请求 → 输出参数-all_file_path → 上传cos（蓝鲸ceph） → 输出参数-cos_url → 发送日志消息 → 结束
```

---

## 通用模式

### 常见标准子流程

**1. 日志清理序列**
```
查找过期日志 → 压缩归档 → 清理原文件 → 通知结果
```

**2. Core 文件处理序列**
```
Core文件采集 → 文件分发（到分析服务器） → 分析Core → 通知结果
```

---

## 核心组件

| 组件 | 说明 | 使用场景 | 使用次数 |
|------|------|---------|--------|
| `job_fast_execute_script` | 快速脚本执行 | 通过 JOB 平台快速执行 Shell/Python 脚本 | 229 |
| `job_execute_task` | JOB 作业执行 | 执行 JOB 平台预定义的作业模板 | 151 |
| `remote_plugin` | 蓝鲸标准插件调用 | 调用蓝鲸标准插件（DBM/AI/BKChat 等） | 96 |
| `job_fast_push_file` | 快速文件分发 | 通过 JOB 快速推送文件到目标机器 | 47 |
| `odm_upload_xml` | odm_upload_xml | odm_upload_xml | 43 |
| `bk_notify` | 蓝鲸通知 | 发送邮件/短信/微信通知 | 29 |
| `pause_node` | 人工确认/暂停 | 流程暂停等待人工确认后继续 | 26 |
| `wechat_work_send_message` | 企业微信消息 | 发送企业微信群/个人消息 | 10 |
| `odm_alter_bill` | odm_alter_bill | odm_alter_bill | 9 |
| `odm_bill_execute` | odm_bill_execute | odm_bill_execute | 9 |
| `job_fetch_task_log` | JOB 日志获取 | 获取 JOB 任务执行日志 | 7 |
| `bk_http_request` | HTTP 请求 | 发送 HTTP/HTTPS 请求调用外部 API | 5 |
| `bk_approve` | 审批节点 | 流程审批确认 | 5 |
| `bk_display` | 消息展示 | 在流程中展示信息供查看 | 4 |
| `all_biz_job_fast_push_file` | all_biz_job_fast_push_file | all_biz_job_fast_push_file | 4 |

## 核心插件

| 插件 | 说明 | 使用场景 | 使用次数 |
|------|------|---------|--------|
| `tglog-xml-python` | tglog-xml-python | tglog-xml-python | 31 |
| `tcompose-exec` | TCompose 执行 | 执行容器编排任务 | 11 |
| `bkchat-sops` | BKChat 集成 | 蓝鲸 ChatOps 消息交互 | 10 |
| `devops-pl-plugin` | 蓝盾流水线 | 触发蓝盾 CI/CD 流水线 | 8 |
| `bkchat-sops-send` | BKChat 消息发送 | 发送消息到企业微信群 | 6 |
| `bkdbm-sqlexecute` | DBM SQL 执行 | 通过 DBM 执行 SQL 变更 | 5 |
| `robot-reponse` | robot-reponse | robot-reponse | 4 |
| `bkdbm-confirm` | DBM 确认 | 数据库管理平台操作确认 | 3 |
| `bk-odm` | bk-odm | bk-odm | 3 |
| `ai-corefile-anz` | ai-corefile-anz | ai-corefile-anz | 2 |

---

## 关键参数

### 组件参数

| 参数 | 所属组件 | 说明 | 示例值 |
|------|---------|------|--------|
| `biz_cc_id` | 快速脚本执行 | biz_cc_id | - |
| `job_account` | 快速脚本执行 | job_account | root |
| `job_content` | 快速脚本执行 | job_content | - |
| `job_ip_list` | 快速脚本执行 | job_ip_list | ${ip_list} |
| `job_script_param` | 快速脚本执行 | job_script_param | ${name} |
| `job_task_id` | JOB 作业执行 | job_task_id | - |
| `button_refresh` | JOB 作业执行 | button_refresh | - |
| `job_global_var` | JOB 作业执行 | job_global_var | ${job_global_var} |
| `button_refresh_2` | JOB 作业执行 | button_refresh_2 | - |
| `odm_file` | 蓝鲸标准插件调用 | odm_file | - |
| `msg_type` | 蓝鲸标准插件调用 | msg_type | - |
| `code_content` | 蓝鲸标准插件调用 | code_content | - |
| `job_source_files` | 快速文件分发 | job_source_files | ${job_source_files} |
| `job_timeout` | 快速文件分发 | job_timeout | 3600 |
| `odm_game_id` | odm_upload_xml | odm_game_id | ${odm_game_id} |
| `odm_new_xml` | odm_upload_xml | odm_new_xml | ${odm_new_xml} |
| `bk_notify_content` | 蓝鲸通知 | bk_notify_content | ${bk_notify_content} |
| `bk_notify_title` | 蓝鲸通知 | bk_notify_title | ${bk_notify_title} |
| `bk_notify_type` | 蓝鲸通知 | bk_notify_type | - |
| `bk_receiver_info` | 蓝鲸通知 | bk_receiver_info | - |

### 流程变量

| 变量 | 名称 | 来源类型 | 出现次数 |
|------|------|---------|--------|
| `${odm_file}` | 上传xml文件 | component_inputs | 73 |
| `${task_end_time}` | 任务结束时间 | custom | 43 |
| `${task_start_time}` | 任务起始时间 | custom | 43 |
| `${log_outputs}` | JOB全局变量 | component_outputs | 40 |
| `${ip}` | ip | custom | 20 |
| `${odm_new_xml}` | 上传新xml文件 | component_inputs | 14 |
| `${iplist}` | iplist | custom | 11 |
| `${job_ip_list}` | Job-快速发布文件 | custom | 10 |
| `${odm_ip_list}` | GCS-ODM的Tlog变更 | custom | 9 |
| `${_gcs_bill_id}` | 单据号 | component_outputs | 9 |
| `${job_inst_id}` | JOB任务ID | component_outputs | 8 |
| `${job_task_log}` | 任务日志 | component_outputs | 7 |
| `${result_vars}` | 结果变量 | component_outputs | 7 |
| `${custom_date}` | custom_date | custom | 7 |
| `${end_time}` | 结束时间 | custom | 7 |

---

## 网关使用

| 网关类型 | 使用次数 | 说明 |
|---------|---------|------|
| ParallelGateway | 19 | 并行执行所有分支 |
| ExclusiveGateway | 30 | 条件选择单一分支 |
| ConvergeGateway | 33 | 等待所有并行分支完成 |
| ConditionalParallelGateway | 4 | 满足条件的分支并行执行 |

---

## 检查清单

| 检查项 | 说明 | 严重程度 |
|--------|------|--------|
| 🟡 日志轮转 | 是否有日志定期清理机制 | 中 |
| 🟡 Core 分析 | coredump 是否有自动 bt 分析 | 中 |
| 🟢 远程存储 | 日志是否归档到 COS/远程存储 | 低 |
| 🟡 空间监控 | 是否监控日志磁盘空间 | 中 |