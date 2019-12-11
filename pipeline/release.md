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

    