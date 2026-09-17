# 机器初始化

> 新机器上架后的标准化初始化。跨业务高度一致的基础运维流程，可直接复用。
>
> **1203** 条流程 | 平均节点数基于采样分析

---

## 关键检查点

1. 初始化后必须同步 CMDB 主机信息（当前采用率 0%）
2. 初始化完成后必须执行验证检查（当前采用率 0%）
3. 初始化期间屏蔽告警（当前采用率 0%）
4. 关键初始化步骤前有人工确认（当前采用率 1%）
---
## 代表性流程图

**流程 1**（70 个节点）:
```
开始 → [并行] → 定时 → [汇聚] → 初始化gseAgent → 设置防火墙 → [并行] → DNS 设置 → 初始化gseAgent → [汇聚] → 访问外网代理设置 → [并行] → 【子流程】磁盘合并 → 定时10秒 → 【子流程】磁盘初始化 → [汇聚] → 设置环境变量 → [并行] → SpaceSniffer安装 → Python-3.9安装 → powershell安装 → Everything安装 → [汇聚] → Beyond Compare安装 → NSIS安装（3.10版本） → 安装7z → 发送通知 → 发送通知 → 发送通知 → 发送通知 → [并行] → 发送通知 → 发送通知 → 发送通知 → 安装git（2.47.1） → 安装.gradle → [汇聚] → java-17环境部署（jdk） → TortoiseSVN安装 → Node.js安装 → Visual Studio Code安装（1.96） → 发送通知 → 发送通知 → [并行] → 发送通知 → 发送通知 → 发送通知 → 发送通知 → 安装vs2022-Professional-17.14.5（VS2022） → clang安装（18.1版本） → 结束
```

**流程 2**（40 个节点）:
```
开始 → 依赖工具分发 → 系统基础WMI服务判断及修复 → 系统及目标磁盘位置判断 → 执行定义 → [条件] → Tag文件拉取 → Tag文件拉取 → Tag设定处理 → Tag设定处理 → 是否满足安装条件预判 [C/D/E盘需保留10G空闲空间] → 是否满足安装条件预判 [C/D/E盘需保留10G空闲空间] → [条件] → [条件] → [汇聚] → 分析WinSxS → 分析WinSxS → [汇聚] → [条件] → 清理WinSxS[可能非常耗时，需等待此步完成] → 清理WinSxS[可能非常耗时，需等待此步完成] → [条件] → [条件] → [汇聚] → [汇聚] → [条件] → 设置虚拟内存页面 → [汇聚] → [并行] → [并行] → [汇聚] → 设置虚拟内存页面 → 重启操作系统 → 分发windows 10补丁 → 分发windows 2022补丁 → 分发windows 2016补丁 → 分发windows 2019补丁 → [汇聚] → 分发windows 10补丁 → 分发windows 2022补丁 → 分发windows 2019补丁 → [汇聚] → 分发windows 2016补丁 → 重启操作系统 → 定时[等待系统重启完毕] → [并行] → 定时[等待系统重启完毕] → 等待系统及gse_agent恢复，若失败请重试！ → 分发windows补丁更新及检查工具 → 消息展示 → 结束
```

**流程 3**（32 个节点）:
```
开始 → SA-初始化_xxx_init → SA-初始化_config_gcs_dns → SA-初始化_install_L5AGENT → 批量更新主机所属业务模块 → 按规则修改主机名 → 配置udns → 目录初始化 → 配置日志自动删除规则 → 设置coredump文件压缩任务 → 初始脚本目录同步 → 初始脚本目录解压 → [条件] → 环境搭建--小区main模块--xxxQ → 环境搭建--小区main模块--微信 → main-设置本机crontab → main-lcserver配置生成前处理 → main-lcserver配置生成 → main-lcserver配置下发 → main-lcserver gameXXX.args配置生成 → main-dataproxy.args配置生成前处理 → main-dataproxy.args配置生成 → main-dataproxy.args配置生成 → main-dataproxy创建database文件夹 → main-修改main的Script.cfg.php → main-rpcfw_gsc下目录处理 → [条件] → GCS-db库权限申请--微信 → GCS-db库权限申请--xxxQ → GCS-在线库权限申请 → GCS-在线库权限申请 → db连接状况check--微信 → db连接状况check--xxxQ → 在线库连接状况check → 在线库连接状况check → 结束
```

**流程 4**（30 个节点）:
```
开始 → 告警屏蔽12小时 → gamesvr下线 → 延时等待2小时 → 2008重装系统-保留分区 → 延时600秒后继续 → sa初始化 → tjj修改密码 → sajob配置DNS → 3自动化部署gamesvr-传输init包 → 3-01-2008注册表调整 → 2008重启生效 → 延时300秒后继续 → 3-02机器是否重启成功 → 3-03-dx和vc安装 → 3-1自动化部署gamesvr-打开必要的防火墙 → 4自动化部署gamesvr-xxx文件传输解压 → 5自动化部署gamesvr-	传ipkuorong文件 → 6自动化部署gamesvr-	从外网拷贝xxxini文件 → 7-8自动化部署gamesvr-	传输修改xxxini → 9自动化部署gamesvr-	部署xxxtar → 10自动化部署gamesvr-xxx助手安装文件 → 11自动化部署gamesvr-安装枫叶采集数据脚本 → 12自动化部署gamesvr-xxxlogs采集脚本分发安装 → 13自动化部署gamesvr-replayd部署 → 旧版反外挂分发和部署 → 启动gamesvr游戏相关所有服务 → 反外挂新版本worldid生成 → 安装gamesvr采集脚本并添加crontab → 安装windows插件-下发文件-脚本 → 解除告警屏蔽 → 结束
```

**流程 5**（29 个节点）:
```
开始 → 告警屏蔽12小时 → gamesvr下线 → 延时等待2小时 → 2016重装系统-保留分区 → 延时600秒后继续 → sa初始化 → tjj修改密码 → 1业务初始化参数 → 2服务器重启生效 → 延时300秒后继续 → sajob配置DNS → 2检查初始化参数 → 3自动化部署gamesvr-传输init包 → 3-1自动化部署gamesvr-打开必要的防火墙 → 4自动化部署gamesvr-xxx文件传输解压 → 5自动化部署gamesvr-	传ipkuorong文件 → 6自动化部署gamesvr-	从外网拷贝xxxini文件 → 7-8自动化部署gamesvr-	传输修改xxxini → 9自动化部署gamesvr-	部署xxxtar → 10自动化部署gamesvr-xxx助手安装文件 → 11自动化部署gamesvr-安装枫叶采集数据脚本 → 12自动化部署gamesvr-xxxlogs采集脚本分发安装 → 13自动化部署gamesvr-replayd部署 → 反外挂新版本worldid生成 → G3反外挂新worldid版本部署 → 启动gamesvr游戏相关所有服务 → 安装gamesvr采集脚本并添加crontab → 安装windows插件-下发文件-脚本 → 解除告警屏蔽 → 结束
```

**流程 6**（25 个节点）:
```
开始 → TNM2-告警屏蔽 → config_gcs_dns → 初始化 → install_L5AGENT → 创建文件夹 → 传输ds包和tgame_latest_md5.txt → 传输zone配置 → 传输dir配置 → 解压latest三个包 → 发送通知，检查IP列表 → localagent增加server上报 → 启动 apps/tagent → tgame_init_ds_version.sh xxx版本号 → 检查新扩容的额及其是否init成功 → CC-更新VIP/VPort → crontab → root授权vaskey文件 → user00启动vaskey → 暂停 → 暂停 → 暂停 → tgame_init_ds_version.sh xxx版本号 → 检查是否有/data/... → 暂停 → 四合一蓝鲸监控插件最新版本 → 结束
```

**流程 7**（25 个节点）:
```
开始 → [并行] → 【安装】【SA】【Linux】安装L5Agent → 【常用】【SA】【Linux】配置UDNS → 【常用】【SA】初始化 → [汇聚] → 【安装】手游secagent安装 → [并行] → 插件操作 → 插件操作 → [汇聚] → 人工确认 → 根据模板创建集群 → 批量更新主机所属业务模块 → 批量更新集群属性 → Job-执行作业 → DBM-DB权限申请 → 规则上线 → FTP分发服务端版本文件 → 版本部署 → 暂停 → 分发本地文件 → 机器配置初始化 → 执行作业 → 验证release参数 → 暂停 → 启动新服other → 启动game和battle → 执行gm参数 → 发送通知 → 结束
```

**流程 8**（23 个节点）:
```
开始 → [并行] → 【初始化】GseAgent → [汇聚] → 【初始化】收集设备信息 → 【初始化】是否已初始化 → [并行] → 【初始化】空闲检查 → [汇聚] → 【初始化】文件分发 → 【初始化】配置检查 → 【初始化】前置处理 → 结束 → 【初始化】系统类型 → [并行] → 【初始化】前置设置 → 【初始化】前置设置 → 【初始化】前置检查设置 → 【初始化】磁盘格式化 → 【初始化】主逻辑 → 【初始化】磁盘格式化 → 【初始化】主逻辑 → 【初始化】后置配置 → 【初始化】主逻辑 → [汇聚] → 【初始化】DBA配置 → [并行] → 【初始化】安装LDAP → 【初始化】安装插件 → 【安装】【IDC】bifrost/bksam【正式】 → 【初始化】安装NMON → 【初始化】安装网管Agent → [汇聚] → 结束
```

---

## 通用模式

### 常见标准子流程

**1. 标准初始化序列**
```
SA常规初始化 → 空闲检查 → 配置DNS → 转移主机模块 → 告警屏蔽 → 数据盘格式化 → 安装组件 → 网络配置 → 内核升级 → 人工确认
```

**2. 网络配置序列**
```
路由检测修正 → 禁掉外网 → DNS配置 → NTP时间同步 → 安全组配置
```

**3. 组件安装序列**
```
YUM源配置 → ipvsadm安装 → ceph安装 → conntrack安装 → iptables更新 → 内核模块装载
```

---

## 核心组件

| 组件 | 说明 | 使用场景 | 使用次数 |
|------|------|---------|--------|
| `job_fast_execute_script` | 快速脚本执行 | 通过 JOB 平台快速执行 Shell/Python 脚本 | 641 |
| `sa_create_task` | SA 任务创建 | 创建 SA 工单任务 | 354 |
| `job_execute_task` | JOB 作业执行 | 执行 JOB 平台预定义的作业模板 | 333 |
| `pause_node` | 人工确认/暂停 | 流程暂停等待人工确认后继续 | 114 |
| `nodeman_create_task` | 节点管理任务 | 通过节点管理平台执行任务 | 110 |
| `remote_plugin` | 蓝鲸标准插件调用 | 调用蓝鲸标准插件（DBM/AI/BKChat 等） | 97 |
| `nodeman_plugin_operate` | 节点管理插件 | 操作节点管理平台插件 | 97 |
| `job_fast_push_file` | 快速文件分发 | 通过 JOB 快速推送文件到目标机器 | 90 |
| `bk_notify` | 蓝鲸通知 | 发送邮件/短信/微信通知 | 43 |
| `cc_transfer_host_module` | CMDB 主机转移 | 在 CMDB 中转移主机到指定模块 | 28 |
| `bk_http_request` | HTTP 请求 | 发送 HTTP/HTTPS 请求调用外部 API | 26 |
| `sleep_timer` | 定时等待 | 流程等待指定时间后继续 | 26 |
| `job_push_local_files` | 本地文件推送 | 推送本地文件到远程机器 | 20 |
| `all_biz_job_fast_execute_script` | all_biz_job_fast_execute_script | all_biz_job_fast_execute_script | 20 |
| `tjj_update_password` | tjj_update_password | tjj_update_password | 18 |

## 核心插件

| 插件 | 说明 | 使用场景 | 使用次数 |
|------|------|---------|--------|
| `sa-task-plugin` | sa-task-plugin | sa-task-plugin | 24 |
| `bkdbm-sssqlexec` | bkdbm-sssqlexec | bkdbm-sssqlexec | 16 |
| `bkdbm-confirm` | DBM 确认 | 数据库管理平台操作确认 | 10 |
| `hostname-by-rule` | hostname-by-rule | hostname-by-rule | 7 |
| `bkchat-sops-send` | BKChat 消息发送 | 发送消息到企业微信群 | 5 |
| `db-auto-create` | DB 自动创建 | 自动创建数据库实例 | 4 |
| `bkdbm-ssauth` | bkdbm-ssauth | bkdbm-ssauth | 4 |
| `bkchat-sops` | BKChat 集成 | 蓝鲸 ChatOps 消息交互 | 4 |
| `modify-hostname` | modify-hostname | modify-hostname | 3 |
| `db-auto-upload` | DB 自动上传 | 自动上传数据库备份 | 3 |

---

## 关键参数

### 组件参数

| 参数 | 所属组件 | 说明 | 示例值 |
|------|---------|------|--------|
| `biz_cc_id` | 快速脚本执行 | biz_cc_id | ${biz_cc_id} |
| `job_account` | 快速脚本执行 | job_account | ${job_account} |
| `job_content` | 快速脚本执行 | job_content | - |
| `job_ip_list` | 快速脚本执行 | job_ip_list | ${job_ip_list} |
| `job_script_param` | 快速脚本执行 | job_script_param | - |
| `sa_ip_list` | SA 任务创建 | sa_ip_list | ${sa_ip_list} |
| `sa_task_type` | SA 任务创建 | sa_task_type | xxx_init |
| `job_task_id` | JOB 作业执行 | job_task_id | - |
| `job_global_var` | JOB 作业执行 | job_global_var | - |
| `button_refresh` | JOB 作业执行 | button_refresh | - |
| `ip_is_exist` | JOB 作业执行 | ip_is_exist | - |
| `description` | 人工确认/暂停 | description | 收集IP地址 |
| `bk_biz_id` | 节点管理任务 | bk_biz_id | ${bk_biz_id} |
| `nodeman_op_info` | 节点管理任务 | nodeman_op_info | - |
| `nodeman_ticket` | 节点管理任务 | nodeman_ticket | - |
| `nodeman_op_target` | 节点管理任务 | nodeman_op_target | - |
| `ignore_ticket_status` | 蓝鲸标准插件调用 | ignore_ticket_status | - |
| `nodeman_host_os_type` | 节点管理插件 | nodeman_host_os_type | linux |
| `nodeman_plugin_operate` | 节点管理插件 | nodeman_plugin_operate | - |
| `nodeman_host_info` | 节点管理插件 | nodeman_host_info | ${nodeman_host_info} |

### 流程变量

| 变量 | 名称 | 来源类型 | 出现次数 |
|------|------|---------|--------|
| `${job_ip_list}` | Job-快速执行脚本 | custom | 134 |
| `${biz_cc_id}` | 业务 | component_inputs | 104 |
| `${bk_biz_id}` | 业务 | component_inputs | 85 |
| `${job_account}` | 执行账号 | component_inputs | 84 |
| `${notready}` | 异常列表 | custom | 74 |
| `${task_end_time}` | 任务结束时间 | custom | 68 |
| `${task_start_time}` | 任务起始时间 | custom | 68 |
| `${download_port}` | 下载服务器端口 | custom | 59 |
| `${download_svr}` | 下载服务器地址 | custom | 59 |
| `${sys_os_type}` | 系统类型 | custom | 59 |
| `${url}` | 下载URL | custom | 59 |
| `${sa_ip_list}` | SA初始化(常规) | custom | 37 |
| `${gtags_ip}` | SA初始化(常规) | custom | 33 |
| `${ip_list}` | 主机密码修改 | custom | 28 |
| `${host_id}` | 主机id | custom | 27 |

---

## 网关使用

| 网关类型 | 使用次数 | 说明 |
|---------|---------|------|
| ParallelGateway | 53 | 并行执行所有分支 |
| ExclusiveGateway | 56 | 条件选择单一分支 |
| ConvergeGateway | 203 | 等待所有并行分支完成 |
| ConditionalParallelGateway | 129 | 满足条件的分支并行执行 |

---

## 检查清单

| 检查项 | 说明 | 严重程度 |
|--------|------|--------|
| 🔴 UDNS 配置 | 是否包含 UDNS 配置步骤 | 高 |
| 🔴 Agent 安装 | 是否安装必要的 Agent（L5/北极星/bifrost/bksam） | 高 |
| 🟡 LDAP 配置 | 是否配置 LDAP 认证 | 中 |
| 🟢 主机名设置 | 是否设置标准主机名 | 低 |
| 🟡 空闲检查 | 是否有空闲状态检查 | 中 |