标准运维能够使用以下几种部署模式的 redis 服务，对应模式需要的配置如下：

## 单实例模式

单实例模式，需要配置以下环境变量

- BKAPP_REDIS_MODE：`single`
- BKAPP_REDIS_HOST：redis 服务 host
- BKAPP_REDIS_PORT：redis 服务端口
- BKAPP_REDIS_PASSWORD（非必须）：redis 访问密码
- BKAPP_REDIS_DB（非必须）：redis db

## 集群模式

需要配置以下环境变量

- BKAPP_REDIS_MODE：`cluster`
- BKAPP_REDIS_HOST：redis 集群中任意一台节点的 host
- BKAPP_REDIS_PORT：redis 集群中任意一台节点的端口
- BKAPP_REDIS_PASSWORD（非必须）：redis 访问密码

## Sentinel 模式

需要配置以下环境变量

- BKAPP_REDIS_MODE：replication
- BKAPP_REDIS_HOST：sentinel host，支持配置多 sentinel，host 间以 `,` 分隔
- BKAPP_REDIS_PORT：sentinel port，支持配置多 sentinel，port 间以 `,` 分隔，port 数量与 sentinel 数量必须保持一致
- BKAPP_REDIS_PASSWORD（非必须）：redis 访问密码
- BKAPP_REDIS_SERVICE_NAME（非必须）：redis 集群 master service name
