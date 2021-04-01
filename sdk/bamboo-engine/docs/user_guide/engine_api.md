
<!-- TOC -->

- [Engine API](#engine-api)
    - [run_pipeline](#run_pipeline)
        - [example](#example)
    - [pause_pipeline](#pause_pipeline)
        - [example](#example)
    - [revoke_pipeline](#revoke_pipeline)
        - [example](#example)
    - [resume_pipeline](#resume_pipeline)
        - [example](#example)
    - [pause_node_appoint](#pause_node_appoint)
        - [example](#example)
    - [resume_node_appoint](#resume_node_appoint)
        - [example](#example)
    - [retry_node](#retry_node)
        - [example](#example)
    - [skip_node](#skip_node)
        - [example](#example)
    - [skip_exclusive_gateway](#skip_exclusive_gateway)
        - [example](#example)
    - [forced_fail_activity](#forced_fail_activity)
        - [example](#example)
    - [callback](#callback)
        - [example](#example)
    - [get_pipeline_states](#get_pipeline_states)
        - [example](#example)
    - [get_children_states](#get_children_states)
        - [example](#example)
    - [get_execution_data_inputs](#get_execution_data_inputs)
        - [example](#example)
    - [get_execution_data_outputs](#get_execution_data_outputs)
        - [example](#example)
    - [get_execution_data](#get_execution_data)
        - [example](#example)
    - [get_node_histories](#get_node_histories)
        - [example](#example)
    - [get_node_short_histories](#get_node_short_histories)
        - [example](#example)

<!-- /TOC -->

## Engine API

所有与 bamboo_engine 的交互都应该通过 bamboo_engine.api 来进行，所有的 Engine API 的返回对象均为 `bamboo_engine.api.EngineAPIResult`：

```python
class EngineAPIResult:
    def __init__(
        self,
        result: bool,
        message: str,
        exc: Optional[Exception] = None,
        data: Optional[Any] = None,
    ):
        """
        :param result: 是否执行成功
        :type result: bool
        :param message: 附加消息，result 为 False 时关注
        :type message: str
        :param exc: 异常对象
        :type exc: Exception
        :param data: 数据
        :type data: Any
        """
        self.result = result
        self.message = message
        self.exc = exc
        self.data = data
```

### run_pipeline

```python
def run_pipeline(
    runtime: EngineRuntimeInterface, pipeline: dict, **options
) -> EngineAPIResult:
    """
    执行 pipeline

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param pipeline: pipeline 描述对象
    :type pipeline: dict
    :return: 执行结果
    :rtype: EngineAPIResult
```

#### example

```python
start = EmptyStartEvent()
act = ServiceActivity(component_code="example_component")
end = EmptyEndEvent()

start.extend(act).extend(end)

pipeline = builder.build_tree(start)

runtime = BambooDjangoRuntime()
api.run_pipeline(runtime=runtime, pipeline=pipeline).result
# True
```

### pause_pipeline

```python
def pause_pipeline(
    runtime: EngineRuntimeInterface, pipeline_id: str
) -> EngineAPIResult:
    """
    暂停 pipeline 的执行

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param pipeline_id: piipeline id
    :type pipeline_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
```
#### example

```python
runtime = BambooDjangoRuntime()
api.run_pipeline(runtime=runtime, pipeline_id="pipeline id").result
# True
```

### revoke_pipeline

```python
def revoke_pipeline(
    runtime: EngineRuntimeInterface, pipeline_id: str
) -> EngineAPIResult:
    """
    撤销 pipeline，使其无法继续执行

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param pipeline_id: pipeline id
    :type pipeline_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
```

#### example

```python
runtime = BambooDjangoRuntime()
api.revoke_pipeline(runtime=runtime, pipeline_id="pipeline id").result
# True
```

### resume_pipeline

```python
def resume_pipeline(
    runtime: EngineRuntimeInterface, pipeline_id: str
) -> EngineAPIResult:
    """
    继续被 pause_pipeline 接口暂停的 pipeline 的执行

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param pipeline_id: pipeline id
    :type pipeline_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
```

#### example

```python
runtime = BambooDjangoRuntime()
api.resume_pipeline(runtime=runtime, pipeline_id="pipeline id").result
# True
```


### pause_node_appoint

```python
def pause_node_appoint(
    runtime: EngineRuntimeInterface, node_id: str
) -> EngineAPIResult:
    """
    预约暂停某个节点的执行

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 节点 id
    :type node_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
```

#### example

```python
runtime = BambooDjangoRuntime()
api.pause_node_appoint(runtime=runtime, node_id="node_id").result
# True
```

### resume_node_appoint

```python
def resume_node_appoint(
    runtime: EngineRuntimeInterface, node_id: str
) -> EngineAPIResult:
    """
    继续由于某个节点而暂停的 pipeline 的执行

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 节点 id
    :type node_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
```

#### example

```python
runtime = BambooDjangoRuntime()
api.resume_node_appoint(runtime=runtime, node_id="node_id").result
# True
```

### retry_node

```python
def retry_node(
    runtime: EngineRuntimeInterface, node_id: str, data: Optional[dict] = None
) -> EngineAPIResult:
    """
    重试某个执行失败的节点

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 失败的节点 id
    :type node_id: str
    :param data: 重试时使用的节点执行输入
    :type data: dict
    :return: 执行结果
    :rtype: EngineAPIResult
    """
```

#### example

```python
runtime = BambooDjangoRuntime()
api.retry_node(runtime=runtime, node_id="node_id", data={"key": "value"}).result
# True
```

### skip_node

```python
def skip_node(runtime: EngineRuntimeInterface, node_id: str) -> EngineAPIResult:
    """
    跳过某个执行失败的节点（仅限 event，activity）

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 失败的节点 id
    :type node_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
```

#### example

```python
runtime = BambooDjangoRuntime()
api.skip_node(runtime=runtime, node_id="node_id").result
# True
```

### skip_exclusive_gateway

```python
def skip_exclusive_gateway(
    runtime: EngineRuntimeInterface, node_id: str, flow_id: str
) -> EngineAPIResult:
    """
    跳过某个执行失败的分支网关

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 失败的分支网关 id
    :type node_id: str
    :param flow_id: 需要往下执行的 flow id
    :type flow_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
```

#### example

```python
runtime = BambooDjangoRuntime()
api.skip_exclusive_gateway(runtime=runtime, node_id="node_id", flow_id="flow_id").result
# True
```

### forced_fail_activity

```python
def forced_fail_activity(
    runtime: EngineRuntimeInterface, node_id: str, ex_data: str
) -> EngineAPIResult:
    """
    强制失败某个 activity 节点

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 节点 ID
    :type node_id: str
    :param message: 异常信息
    :type message: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
```

#### example

```python
runtime = BambooDjangoRuntime()
api.forced_fail_activity(runtime=runtime, node_id="node_id", ex_data="forced fail by me").result
# True
```

### callback

```python
def callback(
    runtime: EngineRuntimeInterface, node_id: str, version: str, data: dict
) -> EngineAPIResult:
    """
    回调某个节点

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param version: 节点执行版本
    :param version: str
    :param data: 节点 ID
    :type data: dict
    :return: 执行结果
    :rtype: EngineAPIResult
    """
```

#### example

```python
runtime = BambooDjangoRuntime()
api.callback(runtime=runtime, node_id="node_id", version="version", data={"key": "value"}).result
# True
```

### get_pipeline_states

```python
def get_pipeline_states(
    runtime: EngineRuntimeInterface, root_id: str, flat_children=True
) -> EngineAPIResult:
    """
    返回某个任务的状态树

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param root_id: 根节点 ID
    :type root_id: str
    :param flat_children: 是否将所有子节点展开
    :type flat_children: bool
    :return: 执行结果
    :rtype: EngineAPIResult
    """
```

#### example

```python
runtime = BambooDjangoRuntime()
api.get_pipeline_states(runtime=runtime, root_id="pipeline_id").data

{'pc31c89e6b85a4e2c8c5db477978c1a57': {'id': 'pc31c89e6b85a4e2c8c5db477978c1a57', # 节点 ID
  'state': 'FINISHED', # 节点状态
  'root_id:': 'pc31c89e6b85a4e2c8c5db477978c1a57', # 根流程 ID
  'parent_id': 'pc31c89e6b85a4e2c8c5db477978c1a57', # 父流程 ID
  'version': 'vaf47e56f2f31401e979c3c47b2a0c285', # 状态版本
  'loop': 1, # 重入次数
  'retry': 0, # 重试次数
  'skip': False, # 是否被跳过
  'created_time': datetime.datetime(2021, 3, 10, 3, 45, 54, 688664, tzinfo=<UTC>), # 状态数据创建时间
  'started_time': datetime.datetime(2021, 3, 10, 3, 45, 54, 688423, tzinfo=<UTC>), # 节点开始执行时间
  'archived_time': datetime.datetime(2021, 3, 10, 3, 45, 54, 775165, tzinfo=<UTC>), # 执行完成（成功或失败）时间
  'children': {'e42035b3f98374062921a191115fc602e': {'id': 'e42035b3f98374062921a191115fc602e',
    'state': 'FINISHED',
    'root_id:': 'pc31c89e6b85a4e2c8c5db477978c1a57',
    'parent_id': 'pc31c89e6b85a4e2c8c5db477978c1a57',
    'version': 've2d0fa10d7d842a1bcac25984620232a',
    'loop': 1,
    'retry': 0,
    'skip': False,
    'children': {},
    'created_time': datetime.datetime(2021, 3, 10, 3, 45, 54, 744490, tzinfo=<UTC>),
    'started_time': datetime.datetime(2021, 3, 10, 3, 45, 54, 744308, tzinfo=<UTC>),
    'archived_time': datetime.datetime(2021, 3, 10, 3, 45, 54, 746690, tzinfo=<UTC>)},
   'e327f83de42df4ebfab375c271bf63d29': {'id': 'e327f83de42df4ebfab375c271bf63d29',
    'state': 'FINISHED',
    'root_id:': 'pc31c89e6b85a4e2c8c5db477978c1a57',
    'parent_id': 'pc31c89e6b85a4e2c8c5db477978c1a57',
    'version': 'v893cdc14150d4df5b20f2db32ba142b3',
    'loop': 1,
    'retry': 0,
    'skip': False,
    'children': {},
    'created_time': datetime.datetime(2021, 3, 10, 3, 45, 54, 753321, tzinfo=<UTC>),
    'started_time': datetime.datetime(2021, 3, 10, 3, 45, 54, 753122, tzinfo=<UTC>),
    'archived_time': datetime.datetime(2021, 3, 10, 3, 45, 54, 758697, tzinfo=<UTC>)},
   'e6c7d7a3721ca4b19a5a7f3b34d8387bf': {'id': 'e6c7d7a3721ca4b19a5a7f3b34d8387bf',
    'state': 'FINISHED',
    'root_id:': 'pc31c89e6b85a4e2c8c5db477978c1a57',
    'parent_id': 'pc31c89e6b85a4e2c8c5db477978c1a57',
    'version': 'v0c661ee6994d4eb4bdbfe5260f9a9f22',
    'loop': 1,
    'retry': 0,
    'skip': False,
    'children': {},
    'created_time': datetime.datetime(2021, 3, 10, 3, 45, 54, 767563, tzinfo=<UTC>),
    'started_time': datetime.datetime(2021, 3, 10, 3, 45, 54, 767384, tzinfo=<UTC>),
    'archived_time': datetime.datetime(2021, 3, 10, 3, 45, 54, 773341, tzinfo=<UTC>)}}}}
```

### get_children_states

```python
def get_children_states(
    runtime: EngineRuntimeInterface, node_id: str
) -> EngineAPIResult:
    """
    返回某个节点及其所有子节点的状态

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 父流程 ID
    :type node_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
```

#### example

```python
runtime = BambooDjangoRuntime()
api.get_children_states(runtime=runtime, node_id="pipeline_id").data


{'p07926dd8e81a4f0d9cd484d4856afd42': {'id': 'p07926dd8e81a4f0d9cd484d4856afd42',  # 节点 ID
  'state': 'FINISHED', # 节点状态
  'root_id:': 'p07926dd8e81a4f0d9cd484d4856afd42', # 根流程 ID
  'parent_id': 'p07926dd8e81a4f0d9cd484d4856afd42', # 父流程 ID
  'version': 'v512822ec7fbc4c3180bddb4a6e3f72ad', # 状态版本
  'loop': 1, # 重入次数
  'retry': 0, # 重试次数
  'skip': False, # 是否被跳过
  'created_time': datetime.datetime(2021, 3, 10, 11, 5, 22, 725395, tzinfo=<UTC>), # 状态数据创建时间
  'started_time': datetime.datetime(2021, 3, 10, 11, 5, 22, 725130, tzinfo=<UTC>), # 节点开始执行时间
  'archived_time': datetime.datetime(2021, 3, 10, 11, 5, 22, 842400, tzinfo=<UTC>), # 执行完成（成功或失败）时间
  'children': {'e571501dfbf204e679347c4a74a4ad2ae': {'id': 'e571501dfbf204e679347c4a74a4ad2ae',
    'state': 'FINISHED',
    'root_id:': 'p07926dd8e81a4f0d9cd484d4856afd42',
    'parent_id': 'p07926dd8e81a4f0d9cd484d4856afd42',
    'version': 'vf72134b379224b5e95bd1b1c887b2b1e',
    'loop': 1,
    'retry': 0,
    'skip': False,
    'created_time': datetime.datetime(2021, 3, 10, 11, 5, 22, 806533, tzinfo=<UTC>),
    'started_time': datetime.datetime(2021, 3, 10, 11, 5, 22, 806038, tzinfo=<UTC>),
    'archived_time': datetime.datetime(2021, 3, 10, 11, 5, 22, 809831, tzinfo=<UTC>)},
   'ea3e45c2685e148e9849e4a34e992a562': {'id': 'ea3e45c2685e148e9849e4a34e992a562',
    'state': 'FINISHED',
    'root_id:': 'p07926dd8e81a4f0d9cd484d4856afd42',
    'parent_id': 'p07926dd8e81a4f0d9cd484d4856afd42',
    'version': 'vbca6dd994806449bbfdfb372457189bc',
    'loop': 1,
    'retry': 0,
    'skip': False,
    'created_time': datetime.datetime(2021, 3, 10, 11, 5, 22, 817497, tzinfo=<UTC>),
    'started_time': datetime.datetime(2021, 3, 10, 11, 5, 22, 817295, tzinfo=<UTC>),
    'archived_time': datetime.datetime(2021, 3, 10, 11, 5, 22, 823874, tzinfo=<UTC>)},
   'efdb8de56dec5419baa0c68ae9af6a671': {'id': 'efdb8de56dec5419baa0c68ae9af6a671',
    'state': 'FINISHED',
    'root_id:': 'p07926dd8e81a4f0d9cd484d4856afd42',
    'parent_id': 'p07926dd8e81a4f0d9cd484d4856afd42',
    'version': 'v957e052ef10d4d14b3fc039893ec70ae',
    'loop': 1,
    'retry': 0,
    'skip': False,
    'created_time': datetime.datetime(2021, 3, 10, 11, 5, 22, 834135, tzinfo=<UTC>),
    'started_time': datetime.datetime(2021, 3, 10, 11, 5, 22, 833957, tzinfo=<UTC>),
    'archived_time': datetime.datetime(2021, 3, 10, 11, 5, 22, 840337, tzinfo=<UTC>)}}}}
```

### get_execution_data_inputs

```python
def get_execution_data_inputs(
    runtime: EngineRuntimeInterface, node_id: str
) -> EngineAPIResult:
    """
    获取某个节点执行数据的输入数据

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 节点 ID
    :type node_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
```

#### example

```python
runtime = BambooDjangoRuntime()
api.get_execution_data_inputs(runtime=runtime, node_id="node_id").data

{'_loop': 1}
```

### get_execution_data_outputs

```python
def get_execution_data_outputs(
    runtime: EngineRuntimeInterface, node_id: str
) -> EngineAPIResult:
    """
    获取某个节点的执行数据输出

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 节点 ID
    :type node_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
```

#### example

```python
runtime = BambooDjangoRuntime()
api.get_execution_data_outputs(runtime=runtime, node_id="node_id").data

{}
```

### get_execution_data

```python
def get_execution_data(
    runtime: EngineRuntimeInterface, node_id: str
) -> EngineAPIResult:
    """
    获取某个节点的执行数据

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 节点 ID
    :type node_id: str
    :return: 执行结果
    :rtype: EngineAPIResult
    """
```

#### example

```python
runtime = BambooDjangoRuntime()
api.get_execution_data(runtime=runtime, node_id="node_id").data

{'inputs': {'_loop': 1}, 'outputs': {}}
```

### get_node_histories

> 注意，只有进行过重试、跳过、重入的节点才会记录执行历史

```python
def get_node_histories(
    runtime: EngineRuntimeInterface, node_id: str, loop: int = -1
) -> EngineAPIResult:
    """
    获取某个节点的历史记录概览

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 节点 ID
    :type node_id: str
    :param loop: 重入次数, -1 表示不过滤重入次数
    :type loop: int, optional
    :return: 执行结果
    :rtype: EngineAPIResult
    """
```

#### example

```python
runtime = BambooDjangoRuntime()
api.get_node_histories(runtime=runtime, node_id="node_id").data


[
    {
        "id": 1, # 历史 ID
        "node_id": "e34ef61258b134ffaae42efee2ab9ff1b", # 节点 ID
        "started_time": datetime.datetime(2021, 3, 10, 11, 10, 9, 350028, tzinfo=<UTC>), # 节点开始执行时间
        "archived_time": datetime.datetime(2021, 3, 10, 11, 10, 9, 352609, tzinfo=<UTC>), # 执行完成（成功或失败）时间
        "loop": 1, # 重入次数
        "skip": False, # 是否被跳过
        "version": "vg4ef61258b134ffaae42efee2ab9ff1b", # 状态版本
        "inputs": {}, # 输入执行数据
        "outputs": {}, # 输出执行数据
    }
]
```

### get_node_short_histories

> 注意，只有进行过重试、跳过、重入的节点才会记录执行历史

```python
def get_node_short_histories(
    runtime: EngineRuntimeInterface, node_id: str, loop: int = -1
) -> EngineAPIResult:
    """
    获取某个节点的简要历史记录

    :param runtime: 引擎运行时实例
    :type runtime: EngineRuntimeInterface
    :param node_id: 节点 ID
    :type node_id: str
    :param loop: 重入次数, -1 表示不过滤重入次数
    :type loop: int, optional
    :return: 执行结果
    :rtype: EngineAPIResult
    """
```

#### example

```python
runtime = BambooDjangoRuntime()
api.get_node_histories(runtime=runtime, node_id="node_id").data


[
    {
        "id": 1, # 历史 ID
        "node_id": "e34ef61258b134ffaae42efee2ab9ff1b", # 节点 ID
        "started_time": datetime.datetime(2021, 3, 10, 11, 10, 9, 350028, tzinfo=<UTC>), # 节点开始执行时间
        "archived_time": datetime.datetime(2021, 3, 10, 11, 10, 9, 352609, tzinfo=<UTC>), # 执行完成（成功或失败）时间
        "loop": 1, # 重入次数
        "skip": False, # 是否被跳过
        "version": "vg4ef61258b134ffaae42efee2ab9ff1b", # 状态版本
    }
]
```