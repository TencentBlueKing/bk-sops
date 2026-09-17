# CDN文件分发

> CDN 文件发布与预热、版本包分发、COS 对象存储上传下载等。涉及xxx云 CDN、COS 等基础设施。
>
> **766** 条流程 | 平均节点数基于采样分析

---

## 关键检查点

1. 文件分发后必须做 MD5/完整性校验（当前采用率 5%）
2. CDN 分发开始时发送通知（当前采用率 7%）
3. CDN 分发完成后发送通知（当前采用率 33%）
4. 大规模分发前必须有人工确认（当前采用率 7%）
---
## 代表性流程图

**流程 1**（33 个节点）:
```
开始 → 正式服大区告警屏蔽 → Idipauth-更新大区状态 → 安卓&ios版本分发 → 标记版本文件部署状态 → 暂停 → 暂停 → REL&CHG-关服数据上报 → 大区软停服 → 通知测试已对外停服 → 暂停 → 暂停10分钟 → 安卓IOS停所有进程 → 安卓版本解压 → IOS版本解压 → 通知运维db变更 → 暂停 → 安卓起resource进程 → 安卓起qq进程 → 安卓起wx进程 → ios起resource进程 → ios起qq进程 → ios起wx进程 → ios起游客进程 → 通知测试已对内开服 → 暂停 → 暂停下一步操作 → 暂停 → 安卓IOS对外开服 → Idipauth-更新大区状态 → 通知测试已对外开服 → 暂停 → 告警屏蔽解除 → REL&CHG-开服数据上报 → 结束
```

**流程 2**（30 个节点）:
```
开始 → 正式服大区告警屏蔽 → 安卓ios版本分发 → 标记版本文件部署状态 → 暂停 → 暂停 → 大区软停服 → 通知测试已对外停服 → 暂停 → 暂停10分钟 → 安卓IOS停所有进程 → 安卓版本解压 → IOS版本解压 → 删除csv文件 → 通知运维db变更 → 暂停 → 安卓起resource进程 → 安卓起qq进程 → 安卓起wx进程 → ios起resource进程 → ios起qq进程 → ios起wx进程 → ios起游客进程 → 通知测试已对内开服 → 暂停 → 暂停下一步操作 → 暂停 → 安卓IOS对外开服 → 通知测试已对外开服 → 暂停 → 告警屏蔽解除 → 结束
```

**流程 3**（29 个节点）:
```
开始 → 证据生成 → 用户信息搜集 → 是否需要审批 → [条件] → 规则类型 → 强制暂停 → [条件] → 审批确认 → 执行封禁 → 是否合规（暂停） → [条件] → [汇聚] → [条件] → 审批拒绝结单 → 结束 → 用户信息二次确认 → 用户信息二次确认 → 客户整改 → 客户整改（24h） → [汇聚] → 客户整改（24h） → 用户信息二次确认 → 用户信息二次确认 → 执行封禁 → 执行封禁 → 是否合规（操作） → 是否合规（操作） → 是否合规（操作） → 执行封禁 → 执行封禁 → [条件] → [条件] → [条件] → 用户信息二次确认 → [汇聚] → 用户信息二次确认 → [汇聚] → 用户信息二次确认 → [汇聚] → 执行封禁 → 执行封禁 → 执行封禁 → 结束
```

**流程 4**（27 个节点）:
```
开始 → 正式服大区告警屏蔽 → Idipauth-更新大区状态 → 安卓ios版本分发 → 标记版本文件部署状态 → 暂停 → RELCHG-关服数据上报 → 大区软停服 → 暂停，通知测试已对外停服 → 暂停10分钟 → 安卓IOS停所有进程 → 安卓版本解压 → IOS版本解压 → 暂停，通知运维db变更 → 安卓起resource进程 → 安卓起qq进程 → 安卓起wx进程 → ios起resource进程 → ios起qq进程 → ios起wx进程 → ios起游客进程 → 通知测试已对内开服 → 暂停下一步操作 → 安卓IOS对外开服 → Idipauth-更新大区状态 → 通知测试已对外开服 → 告警屏蔽解除 → RELCHG-开服数据上报 → 结束
```

**流程 5**（26 个节点）:
```
开始 → 定时执行 → 云石-分发安卓CDN包 → 云石-分发IOSCDN包 → JOB-上传安卓CDN包 → JOB-上传IOSCDN包 → 云石-分发安卓版本包 → 云石-分发IOS版本包 → 云石-分发yaml版本文件 → 暂停-检查CDN能否下载 → JOB-安卓IOS版本合并 → JOB-生成主机元数据 → JOB-设置版本号 → JOB-设置是否重新登录 → JOB-生成filecache → 暂停-暂停观察配置文件 → JOB-同步filecache目录 → restart game-31 → reload global-51 → [条件] → reload node-41 → restart node-41 → reload node-42 → restart node-42 → [汇聚] → 重启timer - 54 → reload dir-61 → stop battle → start battle → 结束
```

**流程 6**（25 个节点）:
```
开始 → 证据生成 → 用户信息搜集 → 规则类型 → [条件] → 执行封禁 → 是否合规（暂停） → [汇聚] → [条件] → 结束 → 用户信息二次确认 → 用户信息二次确认 → 客户整改 → 客户整改（24h） → [汇聚] → 客户整改（24h） → 用户信息二次确认 → 用户信息二次确认 → 执行封禁 → 执行封禁 → 是否合规（操作） → 是否合规（操作） → 是否合规（操作） → 执行封禁 → 执行封禁 → [条件] → [条件] → [条件] → 用户信息二次确认 → [汇聚] → 用户信息二次确认 → [汇聚] → 用户信息二次确认 → [汇聚] → 执行封禁 → 执行封禁 → 执行封禁 → 结束
```

**流程 7**（23 个节点）:
```
开始 → 安卓ios版本分发 → 标记版本文件部署状态 → 暂停 → 大区软停服 → 通知测试已对外停服 → 暂停10分钟 → 安卓IOS停所有进程 → 安卓版本解压 → IOS版本解压 → 删除csv文件 → 通知运维db变更 → 暂停 → 安卓起resource进程 → 安卓起qq进程 → 安卓起wx进程 → ios起resource进程 → ios起qq进程 → ios起wx进程 → 通知测试已对内开服 → 暂停下一步操作 → 暂停 → 安卓IOS对外开服 → 通知测试已对外开服 → 结束
```

**流程 8**（22 个节点）:
```
开始 → [并行] → Job-备份K8S配置 → 静态资源传输到CDN源站-[new] → Robot通知 - 开始发布 → [汇聚] → Job-执行作业 - CDN源站更新[new] → [并行] → Job-qq_stage服-停服 → Job-wx_stage服-停服 → Job-非state服-停服 → [汇聚] → Job-执行作业 - 更新client版本号 → [并行] → Job-执行作业 - 更新servergame服务镜像tag → Job-执行作业 - 更新optool服务镜像tag → Job-执行作业 - 更新trademarket服务镜像tag → Job-执行作业 - 更新private assets服务镜像tag → Job-执行作业 - 更新hygeia服务镜像tag → Job-执行作业 - 更新relay服务镜像tag → Job-执行作业 - 更新perrier服务镜像tag → [汇聚] → 检查各个服务镜像tag → 暂停 → [并行] → Job-非state服-起服 → Job-wx_stage服-起服 → Job-qq_stage服-起服 → [汇聚] → Job-测试服-服务检测 → Robot通知 - 结束发布 → 结束
```

---

## 通用模式

### 常见标准子流程

**1. CDN 资源分发标准序列**
```
告警屏蔽 → 文件分发（推送到CDN节点） → MD5校验 → CDN预热/刷新 → 通知
```

**2. 多节点并行分发**
```
[并行] → CDN节点A分发 | CDN节点B分发 | CDN节点C分发 → [汇聚] → 全量校验
```

**3. 资源+程序分发序列**
```
备份旧版本 → 分发资源文件 → 分发程序文件 → 通知 → 停止进程 → 更新版本 → 启动进程
```

---

## 核心组件

| 组件 | 说明 | 使用场景 | 使用次数 |
|------|------|---------|--------|
| `job_fast_execute_script` | 快速脚本执行 | 通过 JOB 平台快速执行 Shell/Python 脚本 | 304 |
| `job_execute_task` | JOB 作业执行 | 执行 JOB 平台预定义的作业模板 | 234 |
| `pause_node` | 人工确认/暂停 | 流程暂停等待人工确认后继续 | 111 |
| `bk_http_request` | HTTP 请求 | 发送 HTTP/HTTPS 请求调用外部 API | 104 |
| `remote_plugin` | 蓝鲸标准插件调用 | 调用蓝鲸标准插件（DBM/AI/BKChat 等） | 83 |
| `tcm_execute_task` | TCM 配置管理 | 执行 TCM 配置检查/安装/启用/禁用 | 70 |
| `bk_notify` | 蓝鲸通知 | 发送邮件/短信/微信通知 | 60 |
| `job_fast_push_file` | 快速文件分发 | 通过 JOB 快速推送文件到目标机器 | 50 |
| `server_file_dispatch` | 服务端文件分发 | 分发服务端版本包到目标机器 | 45 |
| `job_push_local_files` | 本地文件推送 | 推送本地文件到远程机器 | 39 |
| `client_distribute_files` | client_distribute_files | client_distribute_files | 31 |
| `sleep_timer` | 定时等待 | 流程等待指定时间后继续 | 25 |
| `gsekit_job_exec` | GseKit 进程管理 | 通过 GseKit 执行进程启停操作 | 21 |
| `wechat_work_send_message` | 企业微信消息 | 发送企业微信群/个人消息 | 13 |
| `sa_create_task` | SA 任务创建 | 创建 SA 工单任务 | 10 |

## 核心插件

| 插件 | 说明 | 使用场景 | 使用次数 |
|------|------|---------|--------|
| `bkchat-sops` | BKChat 集成 | 蓝鲸 ChatOps 消息交互 | 22 |
| `tcompose-exec` | TCompose 执行 | 执行容器编排任务 | 8 |
| `bkchat-sops-send` | BKChat 消息发送 | 发送消息到企业微信群 | 8 |
| `prefetch-cdn` | prefetch-cdn | prefetch-cdn | 6 |
| `bot-approval` | 机器人审批 | 通过企业微信机器人发起审批 | 6 |
| `power-plugin-rpc` | Power RPC | 远程过程调用插件 | 5 |
| `ymexport` | ymexport | ymexport | 4 |
| `ticket-to-itsm` | ITSM 创建工单 | 创建 ITSM 工单 | 4 |
| `bksops-itsm` | ITSM 对接 | 与 ITSM 工单系统对接 | 3 |
| `cdn-refresh` | CDN 刷新 | 刷新 CDN 缓存 | 2 |

---

## 关键参数

### 组件参数

| 参数 | 所属组件 | 说明 | 示例值                                                  |
|------|---------|------|------------------------------------------------------|
| `biz_cc_id` | 快速脚本执行 | biz_cc_id | -                                                    |
| `job_account` | 快速脚本执行 | job_account | root                                                 |
| `job_content` | 快速脚本执行 | job_content | -                                                    |
| `job_ip_list` | 快速脚本执行 | job_ip_list | ${ip_list}                                           |
| `job_script_param` | 快速脚本执行 | job_script_param | ${wechat_group_id} ${bk_agent_id} '${user_prompt}'... |
| `job_task_id` | JOB 作业执行 | job_task_id | -                                                    |
| `job_global_var` | JOB 作业执行 | job_global_var | -                                                    |
| `button_refresh` | JOB 作业执行 | button_refresh | -                                                    |
| `ip_is_exist` | JOB 作业执行 | ip_is_exist | -                                                    |
| `description` | 人工确认/暂停 | description | 配置修改，DB变更                                            |
| `bk_http_request_body` | HTTP 请求 | bk_http_request_body | ${signdict['req_str']}                               |
| `bk_http_request_method` | HTTP 请求 | bk_http_request_method | POST                                                 |
| `bk_http_request_url` | HTTP 请求 | bk_http_request_url | cdn_bind_obsid                                       |
| `bk_http_request_header` | HTTP 请求 | bk_http_request_header | -                                                    |
| `bk_http_success_exp` | HTTP 请求 | bk_http_success_exp | resp.code==0                                         |
| `msg_type` | 蓝鲸标准插件调用 | msg_type | markdown                                             |
| `bk_receiver_group` | 蓝鲸标准插件调用 | bk_receiver_group | -                                                    |
| `message_content` | 蓝鲸标准插件调用 | message_content | ... |
| `tcm_app_id` | TCM 配置管理 | tcm_app_id | ${tcm_app_id}                                        |
| `tcm_executor` | TCM 配置管理 | tcm_executor | -                                                    |

### 流程变量

| 变量 | 名称 | 来源类型 | 出现次数 |
|------|------|---------|--------|
| `${task_start_time}` | 任务起始时间 | custom | 74 |
| `${task_end_time}` | 任务结束时间 | custom | 71 |
| `${job_ip_list}` | Job-快速执行脚本 | custom | 33 |
| `${job_local_files}` | local_file_uploadjson | component_inputs | 28 |
| `${log_outputs}` | JOB全局变量 | component_outputs | 27 |
| `${job_target_ip_list}` | 本地文件上传 | custom | 19 |
| `${SetName_LIST}` | 发布范围 | custom | 19 |
| `${_v3_scene_set}` | 场景set | custom | 18 |
| `${_v3_set_group}` | 发布动态分组 | custom | 18 |
| `${_server_version_files}` | FTP分发版本文件 | custom | 17 |
| `${SetChnName_LIST}` | SET中文名 | custom | 16 |
| `${WORLD_ID_LIST}` | 缩容模块 | custom | 16 |
| `${md5}` | 更新md5 | custom | 12 |
| `${filename}` | 文件名称 | custom | 12 |
| `${eventId}` | 工单ID | custom | 11 |

---

## 网关使用

| 网关类型 | 使用次数 | 说明 |
|---------|---------|------|
| ParallelGateway | 32 | 并行执行所有分支 |
| ExclusiveGateway | 62 | 条件选择单一分支 |
| ConvergeGateway | 69 | 等待所有并行分支完成 |
| ConditionalParallelGateway | 3 | 满足条件的分支并行执行 |

---

## 检查清单

| 检查项 | 说明 | 严重程度 |
|--------|------|--------|
| 🔴 预热验证 | CDN 预热后是否有分发完成验证 | 高 |
| 🟡 文件校验 | 分发后是否有 MD5/SHA 校验 | 中 |
| 🟢 多区域并行 | 多区域分发是否使用并行网关 | 低 |
| 🟡 回源检查 | 是否检查 CDN 回源状态 | 中 |
| 🟡 存储桶权限 | COS 上传是否有权限校验 | 中 |