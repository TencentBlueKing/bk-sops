### 蓝鲸服务系列

#### 蓝鲸服务(BK)-定时
#### 蓝鲸服务(BK)-暂停
#### 蓝鲸服务(BK)-HTTP 请求
#### 蓝鲸服务(BK)-发送通知

### 配置平台系列

#### 配置平台(CMDB)-创建集群
#### 配置平台(CMDB)-更新集群属性
#### 配置平台(CMDB)-修改集群服务状态
#### 配置平台(CMDB)-清空集群中主机
#### 配置平台(CMDB)-删除集群
#### 配置平台(CMDB)-更新模块属性
#### 配置平台(CMDB)-转移主机模块
#### 配置平台(CMDB)-更新主机属性
#### 配置平台(CMDB)-转移主机至空闲机模块
#### 配置平台(CMDB)-转移主机至故障机模块
#### 配置平台(CMDB)-上交主机至资源池
#### 配置平台(CMDB)-故障机替换


### 作业平台系列

#### 作业平台(JOB)-执行作业
#### 作业平台(JOB)-快速分发文件
#### 作业平台(JOB)-快速执行脚本
#### 作业平台(JOB)-新建定时作业
#### 作业平台(JOB)-分发本地文件

请确保组件版本版本：

- install_ee >= v1.9.5
- job >= v2.5.18

> 若组件版本不符合要求，升级版本后，需要重新部署标准运维


确保`开发者中心 #### S-mart应用 #### 标准运维 #### 环境变量`中包含有以下变量：


- BKAPP_ENABLE_SHARED_FS：允许挂载 NFS，应为 `True`
- BKAPP_FILE_MANAGER_TYPE：文件管理类型，应为 `host_nfs`
- BKAPP_NFS_CONTAINER_ROOT：NFS 挂载路径，应为 `/data/app/code/USERRES`
- BKAPP_NFS_HOST_ROOT：NFS 宿主机路径，应为 `/data/bkee/paas_agent/apps/projects/bk_sops/code/bk_sops/USERRES`



### 节点管理系列

#### 节点管理(Nodeman)-安装
