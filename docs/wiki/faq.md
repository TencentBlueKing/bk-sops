# FAQ

- 标准运维插件支持用户接入企业内IT系统吗？
> 支持，接入方式请参考《标准插件开发》文档。

- 标准运维点击开始执行任务后报错：taskflow[id=1] get status error: node(nodee37e20…c7fb131) does not exist, may have not by 
executed，并且在任务列表中查看任务状态是“未知”，可能是什么原因？
> 标准运维执行引擎依赖于蓝鲸的 RabbitMQ 服务和 App 启动的 celery 进程，请登录服务器确认服务已启动并正常运行，
可以查看 App 的 celery.log 日志文件帮助定位问题原因。

- 标准运维能执行任务，但是插件节点报错：Trackback…TypeError:int() argument must be a string or a number,not ‘NoneType’，可能是什么原因？
> 标准运维任务流程的执行状态和插件输入、输出等信息缓存依赖 Redis 服务，所以首次部署请务必按照蓝鲸官网的"标准运维部署文档"操作，
配置 Redis 环境变量后重新部署。社区版5.1已经支持默认使用蓝鲸社区版自带的 Redis 服务，但是你依然可以通过修改配置来使用更高性能的独立 Redis 服务。
