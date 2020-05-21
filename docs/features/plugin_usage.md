## JOB-分发本地文件

请确保组件版本版本：

- install_ee >= v1.9.5
- job >= v2.5.18

> 若组件版本不符合要求，升级版本后，需要重新部署标准运维

确保`开发者中心 - S-mart应用 - 标准运维 - 环境变量`中包含有以下变量：

- BKAPP_ENABLE_SHARED_FS：允许挂载 NFS，应为 `True`
- BKAPP_FILE_MANAGER_TYPE：文件管理类型，应为 `host_nfs`
- BKAPP_NFS_CONTAINER_ROOT：NFS 挂载路径，应为 `/data/app/code/USERRES`
- BKAPP_NFS_HOST_ROOT：NFS 宿主机路径，应为 `/data/bkee/paas_agent/apps/projects/bk_sops/code/bk_sops/USERRES`
