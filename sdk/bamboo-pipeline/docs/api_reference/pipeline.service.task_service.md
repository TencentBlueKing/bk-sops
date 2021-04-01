## pipeline.service.task_service

任务服务操作接口

### run_pipeline(pipeline)

执行流程对象

#### 参数

- pipeline(Pipeline)：流程对象
- check_workers(bool)：是否检测 worker 的状态，默认为 `True`
- priority(int)：流程优先级，范围为 `[0, 255]`，默认为 `100`
- queue(string)：执行队列名

#### 返回值

ActionResult：
- result(bool)：是否成功
- message(str)：接口返回信息
- extra(obj)：额外信息

### pause_pipeline(pipeline_id)

暂停一个正在执行的流程

#### 参数

- pipeline_id(str)：流程 ID

#### 返回值

ActionResult：
- result(bool)：是否成功
- message(str)：接口返回信息
- extra(obj)：额外信息

### revoke_pipeline(pipeline_id)

撤销一个正在执行的流程

#### 参数

- pipeline_id(str)：流程 ID

#### 返回值

ActionResult：
- result(bool)：是否成功
- message(str)：接口返回信息
- extra(obj)：额外信息

### resume_pipeline(pipeline_id)

继续一个已经被暂停的流程

#### 参数

- pipeline_id(str)：流程 ID

#### 返回值

ActionResult：
- result(bool)：是否成功
- message(str)：接口返回信息
- extra(obj)：额外信息

### pause_activity(act_id)

预约暂停尚未被执行的 Activity 节点

#### 参数

- act_id(str)：Activity 节点 ID

#### 返回值

ActionResult：
- result(bool)：是否成功
- message(str)：接口返回信息
- extra(obj)：额外信息

### resume_activity(act_id)

继续一个被暂停的 Activity 节点

#### 参数

- act_id(str)：Activity 节点 ID

#### 返回值

ActionResult：
- result(bool)：是否成功
- message(str)：接口返回信息
- extra(obj)：额外信息

### retry_activity(act_id, inputs=None)

重试一个执行失败的 Activity 节点，若 `inputs` 不为空则使用传入的参数重试该节点。 

#### 参数

- act_id(str)：Activity 节点 ID
- inputs(dict)：重试参数

#### 返回值

ActionResult：
- result(bool)：是否成功
- message(str)：接口返回信息
- extra(obj)：额外信息

### skip_activity(act_id)

跳过一个执行失败的 Activity 节点

#### 参数

- act_id(str)：Activity 节点 ID

#### 返回值

ActionResult：
- result(bool)：是否成功
- message(str)：接口返回信息
- extra(obj)：额外信息

### skip_exclusive_gateway(gateway_id, flow_id)

跳过一个执行失败的分支网关

#### 参数

- gateway_id(str)：分支网关 ID
- flow_id(str)：流程继续推进执行的顺序流 ID

#### 返回值

ActionResult：
- result(bool)：是否成功
- message(str)：接口返回信息
- extra(obj)：额外信息

### forced_fail(act_id)

强制失败一个正在执行的 Activity 节点

#### 参数

- act_id(str)：Activity 节点 ID

#### 返回值

ActionResult：
- result(bool)：是否成功
- message(str)：接口返回信息
- extra(obj)：额外信息

### get_state(node_id)

获取某个节点的状态信息

#### 参数

- node_id(str)：节点 ID

#### 返回值

dict：
- children(dict)：子节点状态信息
- finish_time(str)：节点完成时间
- id(str)：节点 ID
- loop(int)：循环次数
- name(str)：节点名称
- retry(int)：重试次数
- skip(book)：是否跳过
- start_time(str)：开始时间
- state(str)：节点状态

### get_inputs(act_id)

获取一个 Activity 节点的输入数据

#### 参数

- act_id(str)：Activity 节点 ID

#### 返回值

dict：输入数据

### get_outputs(act_id)

获取一个 Activity 节点的输出数据

#### 参数

- act_id(str)：Activity 节点 ID

#### 返回值

dict：
- ex_data(str)：异常信息
- outputs(dict)：输出数据

### get_activity_histories(act_id)

获取一个 Activity 节点的执行历史

#### 参数

- act_id(str)：Activity 节点 ID

#### 返回值

list(dict)：
- started_time(str)：开始时间
- finished_time(str)：完成时间
- elapsed_time(int)：执行耗时
- inputs(dict)：输入数据
- outputs(dict)：输出数据
- ex_data(str)：异常信息
- loop(int)：循环次数
- skip(bool)：是否跳过

### callback(act_id, data=None)

回调一个正在等待回调的 Activity 节点

#### 参数

- act_id(str)：Activity 节点 ID
- data(dict)：回调数据

#### 返回值

ActionResult：
- result(bool)：是否成功
- message(str)：接口返回信息
- extra(obj)：额外信息
