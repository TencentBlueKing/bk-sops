# K8S容器

> 基于 K8S/BCS 的容器化运维。包括 Helm 部署、Pod 管理、镜像管理、BCS 集群操作等。
>
> **734** 条流程 | 平均节点数基于采样分析

---

## 关键检查点

1. 容器部署后必须执行 Pod 健康检查（当前采用率 0%）
2. 容器变更期间屏蔽告警（当前采用率 0%）
3. 容器关键操作前有人工确认（当前采用率 10%）
4. 容器操作完成后发送通知（当前采用率 11%）
---
## 代表性流程图

**流程 1**（53 个节点）:
```
开始 → 任务开始时间 → 待切换服停机 → [并行] → TLOG切换-tlogdb重命名提单 → Docker替换校验DB-新DR → Docker替换校验DB-原DR → [汇聚] → DB校验文件比对 → 暂停检查--通知dba调整域名 → 暂停 → 【xxx游戏】源world机器文件打包 → 【xxx游戏】目标world机器解压 → 【xxx游戏】目标world机器解压 → 暂停手动同步forbiduinInfo.txt文件 → 暂停 → webplat上删除要替换的大区 → 暂停 → tcm配置去掉替换服 → tcm配置去掉被替换服 → zone修改主机名 → zone_bak修改主机名 → 其它模块修改主机名 → 新主机名同步到自定义属性 → CCSetID修改替换-set属性 → 暂停 → webplat上重新添加替换的大区 → 暂停 → tcm配置加上被替换服 → 暂停检查 → 暂停 → 切换服配置刷新 → 修正切换服pay_proxy配置 → 暂停 → 全局进程重启刷新 → 切换服核验数据-dba域名切换ok → 暂停 → TLOG切换-tlogdb重命名执行 → odm上删除旧大区tlog → 暂停 → TLOG切换-新tlog机器ODM上架 → 同步安全后台iplist → 同步安全后台iplist → 清掉zerotime文件 → 暂停检查 → 暂停 → 切换服启动 → 刷新内部tdir → 通知切换服测试，变更邮件 → 暂停 → 结束
```

**流程 2**（48 个节点）:
```
开始 → 正式服bcs部署？ → [并行] → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → [汇聚] → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → 结束 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → 结束
```

**流程 3**（47 个节点）:
```
开始 → 发送通知 → 【发布】小服禁用 → 定时300 → [并行] → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → 【发布】小服禁用 → [汇聚] → 【发布】小服禁用 → 【发布】小服禁用 → 结束
```

**流程 4**（46 个节点）:
```
开始 → 是否禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 服务禁用-仅云上上上 → 结束
```

**流程 5**（43 个节点）:
```
开始 → 正式服bcs部署？ → HpaCustomMetricServer更新 → 暂停 → [并行] → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → [汇聚] → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → HpaCustomMetricServer更新 → 结束
```

**流程 6**（33 个节点）:
```
开始 → 正式服bcs部署？ → TACGameServer111-HPA部署 → TACRouterServer-gray-acg-wx部署 → TACGameServer222-HPA部署 → TACGameServer222-HPA部署 → TACGameServer222-HPA部署 → TACGameServer222-HPA部署 → WarmRoundPredictServer-gray部署 → TssSdkServer-gray部署 → BeforeLoginServer-gray部署 → TACRankServer-gray部署 → TLogProxySvr-gray部署 → TalkDCServer-gray部署 → TACConfigSvr-gray部署 → AuthenServer-gray部署 → DBServer-gray部署 → GameDirServer-gray部署 → MatchDirServer-gray部署 → RoomDirServer-gray部署 → TACGameStateSvr-gray部署 → WardenServer-gray部署 → ShareRoomServer-gray部署 → TACUserProfileServer-gray部署 → GuildServer-gray部署 → IdipHttpServer-gray部署 → TACMatchRoomSvr-gray部署 → LockstepRoomServer101-gray部署 → HttpProxyServer-gray部署 → TssSdkServer-gray部署 → HttpProxyServer-gray部署 → GameCreditServer-gray部署 → NameRecommendServer-gray部署 → LockstepRoomServer12-gray部署 → 结束
```

**流程 7**（30 个节点）:
```
开始 → 任务开始时间 → 新主机名同步到自定义属性 → DB初始化变更提单 → DB初始化变更执行 → tcm配置修改,新增大区 → 同步安全后台iplist → 同步安全后台iplist → （暂停中） → 暂停 → 新区配置刷新 → 新服启动前清理文件 → 新服全局进程重启刷新 → 确认新服是否启动 → 暂停 → 新区启动 → xxx_tdircfg替换服upline → 刷新内部tdir → xxx_tdircfg替换服offline → 暂停，添加xxx权限 → 暂停 → 通知替换环境功能测试，邮件通知周边变更 → 暂停 → 准备停服清理数据 → 暂停 → 新区再次停服 → 删除world启动标志文件 → 新服db清理 → GCS-执行GCS变更单据 → 通知DBA进行DB清理并准备数据同步 → 暂停 → 结束
```

**流程 8**（27 个节点）:
```
开始 → [并行] → Set16暂停 → Set20暂停 → Set22暂停 → Set14暂停 → Set24暂停 → Set23暂停 → Set25暂停 → Set21暂停 → Set18暂停 → Set19暂停 → Set15暂停 → Set17暂停 → Set13暂停 → set16 Step1 → set20 Step1 → set22 Step1 → set14 Step1 → set24 Step1 → set23 Step1 → set25 Step1 → set21 Step1 → set18 Step1 → set19 Step1 → set15 Step1 → set17 Step1 → set13 Step1 → [汇聚] → 新版本部署完成 → 结束
```

---

## 通用模式

### 常见标准子流程

**1. 容器部署标准序列**
```
镜像构建/推送 → 告警屏蔽 → 校验镜像(MD5) → 滚动更新Deployment → 等待Pod就绪 → 健康检查 → 取消告警屏蔽 → 通知
```

**2. 节点管理序列**
```
添加污点(taint) → 驱逐Pod → 节点维护操作 → 删除污点 → 验证Pod调度
```

**3. BCS Ingress 管理**
```
修改BCS Ingress配置 → BCS Ingress检查 → 验证连通性 → 通知
```

---

## 核心组件

| 组件 | 说明 | 使用场景 | 使用次数 |
|------|------|---------|--------|
| `job_fast_execute_script` | 快速脚本执行 | 通过 JOB 平台快速执行 Shell/Python 脚本 | 355 |
| `job_execute_task` | JOB 作业执行 | 执行 JOB 平台预定义的作业模板 | 256 |
| `remote_plugin` | 蓝鲸标准插件调用 | 调用蓝鲸标准插件（DBM/AI/BKChat 等） | 152 |
| `pause_node` | 人工确认/暂停 | 流程暂停等待人工确认后继续 | 83 |
| `all_biz_job_fast_execute_script` | all_biz_job_fast_execute_script | all_biz_job_fast_execute_script | 80 |
| `job_fast_push_file` | 快速文件分发 | 通过 JOB 快速推送文件到目标机器 | 43 |
| `bk_notify` | 蓝鲸通知 | 发送邮件/短信/微信通知 | 43 |
| `tcm_execute_task` | TCM 配置管理 | 执行 TCM 配置检查/安装/启用/禁用 | 24 |
| `sleep_timer` | 定时等待 | 流程等待指定时间后继续 | 16 |
| `wechat_work_send_message` | 企业微信消息 | 发送企业微信群/个人消息 | 11 |
| `all_biz_job_fast_push_file` | all_biz_job_fast_push_file | all_biz_job_fast_push_file | 9 |
| `sa_create_task` | SA 任务创建 | 创建 SA 工单任务 | 9 |
| `all_biz_execute_job_plan` | all_biz_execute_job_plan | all_biz_execute_job_plan | 7 |
| `nodeman_create_task` | 节点管理任务 | 通过节点管理平台执行任务 | 6 |
| `tnm2_alarm_shield` | TNM2 告警屏蔽 | 屏蔽 TNM2 监控告警 | 5 |

## 核心插件

| 插件 | 说明 | 使用场景 | 使用次数 |
|------|------|---------|--------|
| `bcs-remote-cmd` | bcs-remote-cmd | bcs-remote-cmd | 42 |
| `fx-bcs-plugin` | BCS 插件 | BCS 容器平台操作 | 32 |
| `helm-plugin1` | Helm 部署 | Helm Chart 部署/更新 | 16 |
| `bkchat-sops` | BKChat 集成 | 蓝鲸 ChatOps 消息交互 | 12 |
| `devops-pl-plugin` | 蓝盾流水线 | 触发蓝盾 CI/CD 流水线 | 9 |
| `bcsnode-plugin` | bcsnode-plugin | bcsnode-plugin | 6 |
| `bkchat-sops-send` | BKChat 消息发送 | 发送消息到企业微信群 | 5 |
| `bksops-itsm` | ITSM 对接 | 与 ITSM 工单系统对接 | 4 |
| `tcompose-exec` | TCompose 执行 | 执行容器编排任务 | 3 |
| `gn-helm` | gn-helm | gn-helm | 3 |

---

## 关键参数

### 组件参数

| 参数 | 所属组件 | 说明 | 示例值 |
|------|---------|------|--------|
| `biz_cc_id` | 快速脚本执行 | biz_cc_id | - |
| `job_account` | 快速脚本执行 | job_account | ${job_account} |
| `job_content` | 快速脚本执行 | job_content | - |
| `job_ip_list` | 快速脚本执行 | job_ip_list | ${ip_list} |
| `job_script_source` | 快速脚本执行 | job_script_source | manual |
| `job_task_id` | JOB 作业执行 | job_task_id | - |
| `job_global_var` | JOB 作业执行 | job_global_var | - |
| `button_refresh` | JOB 作业执行 | button_refresh | - |
| `ip_is_exist` | JOB 作业执行 | ip_is_exist | - |
| `cluster_id` | 蓝鲸标准插件调用 | cluster_id | - |
| `namespace` | 蓝鲸标准插件调用 | namespace | - |
| `container_name` | 蓝鲸标准插件调用 | container_name | - |
| `description` | 人工确认/暂停 | description |  |
| `all_biz_cc_id` | all_biz_job_fast_execute_script | all_biz_cc_id | xxx |
| `job_script_param` | all_biz_job_fast_execute_script | job_script_param | "${Env}" "${rainbow_cluster}" "${full_version}" |
| `job_script_timeout` | all_biz_job_fast_execute_script | job_script_timeout | 600 |
| `job_script_type` | all_biz_job_fast_execute_script | job_script_type | 1 |
| `job_source_files` | 快速文件分发 | job_source_files | - |
| `job_timeout` | 快速文件分发 | job_timeout | - |
| `break_line` | 快速文件分发 | break_line | - |

### 流程变量

| 变量 | 名称 | 来源类型 | 出现次数 |
|------|------|---------|--------|
| `${log_outputs}` | JOB全局变量 | component_outputs | 49 |
| `${cluster_id}` | cluster_id | custom | 28 |
| `${job_ip_list}` | Job-快速执行脚本 | custom | 26 |
| `${Charts_Version}` | Charts_Version | custom | 20 |
| `${node_ip_list}` | node_ip_list | custom | 19 |
| `${ReplicaCount}` | ReplicaCount | custom | 18 |
| `${extraInfo}` | 其他额外服务（默认为空） | custom | 18 |
| `${namespace}` | namespace | custom | 18 |
| `${yunwei_host}` | 运维机 | custom | 17 |
| `${Release_Name_xiao}` | JOB全局变量 | component_outputs | 14 |
| `${Release_Name}` | Release_Name | custom | 14 |
| `${job_account}` | 目标账户 | component_inputs | 13 |
| `${Release_Time}` | Release_Time | custom | 13 |
| `${SetId}` | SetId | custom | 13 |
| `${Tag}` | Tag | custom | 13 |

---

## 网关使用

| 网关类型 | 使用次数 | 说明 |
|---------|---------|------|
| ParallelGateway | 57 | 并行执行所有分支 |
| ExclusiveGateway | 36 | 条件选择单一分支 |
| ConvergeGateway | 96 | 等待所有并行分支完成 |
| ConditionalParallelGateway | 28 | 满足条件的分支并行执行 |

---

## 检查清单

| 检查项 | 说明 | 严重程度 |
|--------|------|--------|
| 🔴 滚动更新 | 部署是否使用滚动更新策略 | 高 |
| 🔴 就绪探针 | 部署后是否有就绪/存活探针验证 | 高 |
| 🟡 资源限制 | 是否配置资源 requests/limits | 中 |
| 🟢 镜像管理 | 是否有镜像版本管理和清理 | 低 |
| 🟡 命名空间隔离 | 是否正确使用 namespace 隔离 | 中 |