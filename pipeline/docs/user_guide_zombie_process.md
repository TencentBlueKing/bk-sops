
<!-- TOC -->

- [卡死任务检测](#卡死任务检测)
- [配置方式](#配置方式)
- [Doctors](#doctors)
  - [RunningNodeZombieDoctor](#runningnodezombiedoctor)

<!-- /TOC -->
## 卡死任务检测

由于引擎中负责执行任务的 celery worker 可能会因为不可抗力被杀死（非正常退出进程）或是其他未知原因，导致引擎中正在执行的部分任务进入卡死无法推进的状态，从上层来看其表现可能为：

- 正在执行的节点一直在执行
- 当前节点执行完成后没有继续往下推进

为了应对这种情况，引擎提供了检测卡死任务并尝试处理的机制。pipeline 采用链式处理的模式来处理引擎中可能卡死的任务，目前提供的可用的 Doctor 有：

- `pipeline.engine.health.zombie.doctors.RunningNodeZombieDoctor`：检测长时间当前节点处于 `RUNNING` 状态的进程，一旦该状态持续超过一定时间，则尝试将该节点置为失败状态。

## 配置方式

只需要在 app settings 中加入如下配置，并且启动 celery beat 和监听了 pipeline_additional_task_priority 队列的 celery worker 即可开启该功能：

```python
ENGINE_ZOMBIE_PROCESS_DOCTORS = [
]
```

下面是一个配置示例，该示例配置了一个 `RunningNodeZombieDoctor`，并且将 `RUNNING` 状态的最大滞留时间设置为 600 秒：

```python
ENGINE_ZOMBIE_PROCESS_DOCTORS = [
    {
        'class': 'pipeline.engine.health.zombie.doctors.RunningNodeZombieDoctor',
        'config': {
            'max_stuck_time': 600,
            'detect_wait_callback_proc': False
        }
    }
]
```

> 注意，由于采用的是链式处理的模式，进程会按照 doctor 配置的顺序进行扫描，配置的 doctor 中有任意一个确认并处理的进程，则后续的 doctor 不会继续处理

## Doctors

### RunningNodeZombieDoctor

检测长时间当前节点处于 `RUNNING` 状态的进程，一旦该状态持续超过一定时间，则尝试将该节点置为失败状态。可配置参数有：

- `max_stuck_time`： `RUNNING` 状态的最大滞留时间，单位为`秒`
- `detect_wait_callback_proc`: 布尔值，是否检测等待回调的进程