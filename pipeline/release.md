# 3.1.5

- bugfix
  - 修复节点日志无法区分多个节点版本状态的问题
# 3.1.4

- feature
  - 添加对 bamboo-engine 的 prometheus metrics 支持

# 3.1.3

- feature
  - get_process_info_with_root_pipeline 接口支持

# 3.1.2

- bugfix
  - 修复 service wrapper 在 schedule 返回 None 时导致节点卡住的问题

# 3.1.1

- bugfix:
  - 修复 pypi module 模式下 create_plugins_app 无法工作的问题

# 3.1.0

- features:
  - 增加 bamboo-engine runtime 实现
  - s3远程插件加载支持配置源目录
  - 插件测试框架添加对插件input/output format的检查 & 同步修改service_activity result type类型
- optimization
  - engine admin 页面性能优化
  - worker 检测增加 rabbitmq 连接错误容错机制
- bugfix:
  - 修复并行网关子进程解析了 splice 类型变量后 _value 没有同步到父进程的问题
  - 修复分支网关表达式字符串未转义导致判断出错问题
  - 修复某些场景下网关合法性校验死循环的问题

# 3.0.0rc2

- bugfix:
  - 修复高并发情况下 sleep 可能会覆写 schedule 产生的数据的问题
# 3.0.0rc1

- features:
  - 支持 Django2，支持 Celery 4
# 2.4.4

- feature:
  - redis sentinel 模式支持配置 redis sentinel 独立密码
  - mako 模板渲染上下文支持配置屏蔽关键字及导入模块
  - 添加 engine context 模块,支持直接获取当前上下文中正在执行的节点信息
  - 支持对 mako 模板进行安全检查
- optimization:
  - 结束节点写流程输出失败时不抛出错误,兼容输出字段可能未输出的情况
  - 优化 pipeline set_{status} 系列接口
  - 优化 component model 和 variable model 的加载逻辑
  - 优化有向图环检测算法
  - 为 pipeline.log LogEntry 的 logged_at 字段添加索引
- bugfix: 
  - 修复子流程参数传递过程中内外层存在同名 key 时导致参数传递失败的问题
  - 修复 lazy 变量 get_value 异常时没有捕获的 bug
  - 修复 pipeline.log.handlers 没有捕获可能会出现的 AppRegistryNotReady 异常
  - IOField 支持序列化节点数更多的流程
  - 修复解析 mako 变量值时没有捕获所有可能异常的问题
  - 修复分支网关提前解析了引用输出的变量后导致后续节点获取不到值的问题
# 2.4.3

- feature:
  - 增加引擎内部消息流转检测功能，记录发送失败的消息，开发者能够对其进行重放
  - databackend 添加自动过期功能
- bugfix:
  - 修复 pipeline worker 检查未使用最新 mq 链接的问题

# 2.4.2

- optimization:
  - pipeline worker 检查添加重连机制
- bugfix:
  - 旧版本存留任务 pickle 数据兼容 _runtime_attrs 不存在的情况

# 2.4.1

- fetures:
  - force_fail 支持传入 ex_data 参数
  - 变量引擎渲染内置函数时返回原字符串
  - 标准插件支持自动加载模块子路径下的所有插件
- optimization:
  - 在 schedule 时更新节点对应的 Data 对象
  - 部分 DB 字段增加索引，解决数据增长后带来的慢查询问题
- bugfix:
  - 修复读取 python manage cmd 可能出现的 IndexError

# 2.4.0

- fetures:
  - 插件统计信息支持记录插件在流程中的版本号
  - 添加僵死任务检测功能
  - 在节点 RuntimeAttrs 中添加 `root_pipeline_id`
- optimization:
  - 插件扫描功能支持忽略特定命令
- bugfix:
  - 修复对子流程中的节点进行强制失败时可能会失败的问题
  - 修复并发多次回调数据混乱问题

# 2.3.0rc1

- features:
  - 节点重入时 `_loop` 的开始值可以配置
  - 增加用户自定义配置隔离队列功能
  - 添加引擎状态(workers, queeus)获取接口
  - 调度节点支持多次回调 
- bugfix:
  - 修复子流程中有环时无法执行任务的问题

# 2.2.0rc1

- features:
  - 添加插件执行命令 `manage.py run_component`
  - 输出变量支持配置多个 source_act
  - redis replication 模式支持配置多 sentinels
  - 支持配置备选 data_backend, 提升流程执行容错性
  - PipelineInstance 新增 is_revoked 属性
- improvements:
  - 优化并行网关的执行效率
  - 优化无法从 settings 中获取 redis 配置时的日志提示
  - 插件模块导入错误时添加错误日志
- bugfix:
  - 修复 MySQLDatabackend 更新数据时产生死锁问题
  - 修复带打回流程 tree 导致 parser 解析错误问题
  - 修复 py3 下部分编码问题
  - 修复多次对不存在的流程调用 revoke_piepline 接口返回结果不一致的问题
  - 修复 snapshot 为空时 in_subprocess 调用报错的问题
  - 修复汇聚网关是否被共享判断逻辑有漏洞的问题
  - 修复节点重入时记录的 history 中 started_time 不正确的问题
  - 修复读取 python2 pickle dump 的数据可能会导致 DecodeError 的问题

# 2.1.0rc1

- features:
    - 添加插件版本管理功能

# 2.0.0rc2

- bugfix:
    - 插件单元测试执行出错时，测试命令不会返回 0

# 2.0.0rc1

- features:
    - py3 支持

# 1.0.0

- features:
    - 流程启动支持传入优先级

# 0.9.8

- features:
    - builder 中 ServiceActivity 元素添加可忽略错误等配置项
    - pipeline log 模块日志级别支持配置
    - task_service 添加节点执行日志获取接口
    - 添加能够自定义执行逻辑的结束节点

# 0.9.7

- features:
    - builder 增加新的全局数据的传递方式
    - 添加条件并行网关
- bugfix:
    - 修复子流程中结束节点执行错误时无法优雅退出进程的 bug
    
# 0.9.6

- features:
    - 节点支持重新执行，以支持循环和打回
    - 流程结构支持更加复杂的环状结构
- bugs fix:
    - 修复同时发起同一个根流程下子进程的唤醒后部分子进程无法往下执行的问题
    - 修复子进程完成后在调整子流程栈中的状态时未处理暂停状态的问题
    - 修复批量重试时部分子进程因为根流程处于 BLOCKED 状态而无法继续执行的问题

# 0.9.5

- minors:
    - 单元测试完善
    
# 0.9.4

- minors:
    - 定时流程在激活时不允许修改流程的常量

# 0.9.3

- features:
    - 流程模板在保存时设置是否含有子流程的信息

# 0.9.2

- improvements:
    - 将 models 模块下与 web 层相关的代码移动到 pipeline_web 中

# 0.9.1

- features:
    - 模板接口兼容 web 及 sdk 模式下的数据

# 0.9.0

- features:
    - 当引擎冻结时不再启动周期任务，并将当前启动记入失败历史
- bugs fix:
    - 修复节点超时强制失败操作执行失败时仍然发送节点执行失败的信号的 bug

    