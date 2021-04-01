<!-- TOC -->

- [组件单元测试](#%E7%BB%84%E4%BB%B6%E5%8D%95%E5%85%83%E6%B5%8B%E8%AF%95)
    - [组件测试类](#%E7%BB%84%E4%BB%B6%E6%B5%8B%E8%AF%95%E7%B1%BB)
    - [组件测试用例](#%E7%BB%84%E4%BB%B6%E6%B5%8B%E8%AF%95%E7%94%A8%E4%BE%8B)
        - [执行断言](#%E6%89%A7%E8%A1%8C%E6%96%AD%E8%A8%80)
        - [调度断言](#%E8%B0%83%E5%BA%A6%E6%96%AD%E8%A8%80)
        - [调用断言](#%E8%B0%83%E7%94%A8%E6%96%AD%E8%A8%80)
        - [如何patch ESB接口调用](#%E5%A6%82%E4%BD%95patch-esb%E6%8E%A5%E5%8F%A3%E8%B0%83%E7%94%A8)
- [示例](#%E7%A4%BA%E4%BE%8B)

<!-- /TOC -->

## 组件单元测试

在我们完成自定义组件的开发后，我们需要测试组件是否能够按照我们预期的那样运行。最简单的方式就是构造一个包含该节点的流程然后把流程跑起来观察其行为和输出是否符合预期。但是这种测试方式十分耗时而且是一次性的，下次若是修改了节点后需要再进行一遍相同的操作。

为了解决这个问题，框架内部提供了组件测试单元测试框架，框架会模拟组件在流程中执行的场景，并根据开发者编写的测试用例来执行组件并检测组件的行为是否符合预期。借助组件单元测试框架能够节省我们测试组件的时间，并且保证组件实现在发生变化后能够快速确认改动是否影响了组件的功能。

### 组件测试类

要使用框架提供的单元测试框架十分容易，只需要在定义测试类的时候将框架提供的测试混入类混入到当前类中即可：

```python

from django.test import TestCase
from pipeline.component_framework.test import ComponentTestMixin

class AComponentTestCase(TestCase, ComponentTestMixin):

    @property
    def component_cls(self):
        # return the component class which should be tested
        return TheScheduleComponent

    @property
    def cases(self):
        # return your component test cases here
        return []

```

将测试类混入到当前类中后，还需要定义两个属性：

- `component_cls`：该方法返回需要被测试的组件的类。
- `cases`：该方法返回该组件的所有测试用例。

### 组件测试用例

对于一个组件可能我们会有若干个测试用例，分别测试不同情况下组件的行为是否符合我们的预期。下面的代码就定义了一个组件测试用例的实例：

```python
from mock import patch, MagicMock, call
from pipeline.component_framework.test import (ComponentTestMixin,
                                               ComponentTestCase,
                                               CallAssertion,
                                               ExecuteAssertion,
                                               ScheduleAssertion)

ComponentTestCase(name='case 1',
                  inputs={'e_call_1': True},
                  parent_data={},
                  execute_assertion=ExecuteAssertion(success=True,
                                                     outputs={}),
                  schedule_assertion=[
                      ScheduleAssertion(success=True,
                                        outputs={'count': 1},
                                        callback_data=None),
                      ScheduleAssertion(success=True,
                                        outputs={'count': 2},
                                        callback_data=None),
                      ScheduleAssertion(success=True,
                                        schedule_finished=True,
                                        outputs={'count': 2},
                                        callback_data=None)],
                  patchers=[
                      patch('pipeline_test_use.components.collections.experience.need_patch_1',
                            MagicMock()),
                      patch('pipeline_test_use.components.collections.experience.need_patch_2',
                            MagicMock())],
                  execute_call_assertion=[
                      CallAssertion(func='pipeline_test_use.components.collections.experience.need_patch_1',
                                    calls=[call()]),
                      CallAssertion(func='pipeline_test_use.components.collections.experience.need_patch_2',
                                    calls=[])],
                  schedule_call_assertion=[
                      CallAssertion(func='pipeline_test_use.components.collections.experience.need_patch_1',
                                    calls=[]),
                      CallAssertion(func='pipeline_test_use.components.collections.experience.need_patch_2',
                                    calls=[])])
```

下面让我们来看一下测试用例的构成：

- `name`：用例名，框架在用例运行失败时会使用当前用例名在日志信息中提示开发者，定义有意义的用例名能够方便我们快速了解该用例测试的功能以及在用例执行失败时快速定位。
- `inputs`：组件执行输入数据，其中定义的数据在测试用例执行前会被设置到被测组件所绑定服务的 `execute(data, parent_data)` 及 `schedule(self, data, parent_data, callback_data=None)` 方法中 `data` 对象的 `inputs` 中。
- `parent_data`：组件执行上下文数据，其中定义的数据在测试用例执行前会被设置到被测组件所绑定服务的 `execute(data, parent_data)` 及 `schedule(self, data, parent_data, callback_data=None)` 方法中 `parent_data` 对象的 `inputs` 中。
- `execute_assertion`：执行断言，用于检测本次测试中组件绑定服务的 `execute` 方法的行为是否符合预期。
- `schedule_assertion`：调度断言，用于检测本次测试中组件绑定服务的 `schedule` 方法的行为是否符合预期；对于非调度或断言型的组件，该字段留空即可。
- `patchers`：其中定义的 `patcher` 会在当前测试用例执行前调用，用于 patch 组件在执行时调用的其他模块的方法或属性，以实现测试隔离。
- `execute_call_assertion`：执行调用断言，用于检测本次测试中组件绑定服务的 `execute` 方法是否以预期的方式调用了其他方法。
- `schedule_call_assertion`：调度调用断言，用于检测本次测试中组件绑定服务的 `schedule` 方法是否以预期的方式调用了其他方法。

#### 执行断言

执行断言能够帮助我们检测本次测试中组件服务的 `exeucte` 方法是否执行成功了，输出的数据是否符合预期：

```python
ExecuteAssertion(success=True, outputs={})
```

下面看一下执行断言的构成：

- `success`：断言本次测试中组件服务的 `execute` 方法是否执行成功。
- `outputs`：断言本次测试中组件服务的 `execute` 方法执行完成后当前节点的数据对象中 `outputs` 字段（即 `execute(data, parent_data)` 中 `data` 的 `outputs` 字段）的数据。

#### 调度断言

调度断言能够帮助我们检测本次测试中组件服务的 `schedule` 方法是否执行成功了，调度是否完成了，输出的数据是否符合预期；这里需要注意的是：**对于调度型的服务，测试框架会根据我们传入的调度断言的数量来进行相应次数的 `scheudle` 方法调用**：

```python
ScheduleAssertion(success=True, schedule_finished=True, outputs={'count': 2}, callback_data=None)
```

下面看一下调度断言的构成：

- `success`：断言本次测试中组件服务的 `schedule` 方法是否执行成功。
- `schedule_finished`：断言本次测试中组件服务是否已经完成调度。
- `outputs`：断言本次测试中组件服务的 `schedule` 方法执行完成后当前节点的数据对象中 `outputs` 字段（即 `schedule(data, parent_data, callback_data=None)` 中 `data` 的 `outputs` 字段）的数据。
- `callback_data`：对于回调型的组件，通过该参数传入回调数据（即 `schedule(data, parent_data, callback_data=None)` 中的 `callback_data`）。

#### 调用断言

调用断言用于检测组件服务的 `execute` 或 `schedule` 方法是否按照预期调用了某些方法；这里需要注意的是：**进行调用断言的函数必须是被 `MagicMock` patch 过的函数**：

```python
CallAssertion(func='pipeline_test_use.components.collections.experience.need_patch_1',
              calls=[call(),
                     call(kwarg_1='', kwargs_2='')],
              any_order=False),
```

下面看一下调用断言的构成：

- `func`：进行调用断言的函数的全限定名。
- `calls`：对函数的调用断言，若要进行“没有被调用”的断言，传递空数组即可。
- `any_order`：是否对 `calls` 中的调用断言没有顺序要求。

#### 如何patch ESB接口调用
大部分插件都会调用ESB接口，在单元测试中，我们可以将这个调用过程进行patch，使被测插件在执行时，接口调用并不实际发生，而是通过MagicMock返回我们给定的响应。比如对于作业平台job.fast_execute_script，
我们可以编写这样的Mock类：
```python
class MockClient(object):
    def __init__(self, fast_execute_script_return=None):
        self.job = MagicMock()
        self.job.fast_execute_script = MagicMock(return_value=fast_execute_script_return)
```
实例化该类时，提供接口响应用例数据：
```python
success_result = {
    'result': True,
    'code': 0,
    'message': 'success',
    'data': {
        'job_instance_name': 'API Quick execution script1521100521303',
        'job_instance_id': 10000
    },
}
mock_client = MockClient(fast_execute_script_return=success_result)
```

而在测试用例中，patch获取client的get_client_by_user函数为mock_client:
```python
from pipeline.component_framework.test import Patcher

GET_CLIENT_BY_USER = 'pipeline_plugins.components.collections.sites.open.job.get_client_by_user'


ComponentTestCase(
    ...
    patchers=[
        Patcher(target=GET_CLIENT_BY_USER, return_value=mock_client)
    ]
    ...
    )
```
## 示例

让我们针对下面代码中定义的组件来编写一个测试类：

```python

from pipeline.core.flow.activity import Service, StaticIntervalGenerator
from pipeline.component_framework.component import Componen

class TheScheduleService(Service):
    __need_schedule__ = True
    interval = StaticIntervalGenerator(1)

    def execute(self, data, parent_data):
        
        # make execute failed if receive fail signal
        if data.inputs.get('fail', False):
            return False

        # write all inputs to outputs
        for k, v in data.inputs.items():
            data.outputs[k] = v

        # write all parent_data.inputs to outputs
        data.outputs.parent_data = {}
        for k, v in parent_data.inputs.items():
            data.outputs.parent_data[k] = v

        return True

    def schedule(self, data, parent_data, callback_data=None):

        # make schedule failed if receive fail signal
        if data.inputs.get('schedule_fail', False):
            return False

        # decide schedule state according to count
        count = data.get_one_of_outputs('count')
        if count is None:
            data.outputs.count = 1
        else:
            if count == 2:
                self.finish_schedule()
            else:
                data.outputs.count += 1

        return True


class TheScheduleComponent(Component):
    name = u'the schedule component'
    code = 'the_schedule_component'
    bound_service = TheScheduleService
```

上述代码中定义的组件是一个调度型组件，该组件的 `execute` 和 `schedule` 方法都会根据输入的某个参数来决定是否能够执行成功。并且在 `execute` 方法中会把传入的 `data` 和 `parent_data` 中的所有输入数据写到输出中。而在 `schedule` 方法中，会根据当前 `schedule` 执行的次数来决定是否完成调度。

根据这个组件的实现，我们能够构造出三个测试用例：

- 组件执行成功的测试用例
- `execute` 执行失败的测试用例
- `schedule` 执行失败的测试用例

> 由于被测代码比较简单，在实际情况中，建议根据黑盒和白盒测试中用例构造方式的指导来构造较为完备的测试用例，以保证能够覆盖到组件执行时所有可能出现的场景。

下面就是我们的测试代码：

```python
from django.test import TestCase

from pipeline.component_framework.test import (ComponentTestMixin,
                                               ComponentTestCase,
                                               ExecuteAssertion,
                                               ScheduleAssertion)

from pipeline_test_use.components.collections.experience import TheScheduleComponent


class TheScheduleComponentTest(TestCase, ComponentTestMixin):

    def component_cls(self):
        return TheScheduleComponent

    def cases(self):
        return [
            ComponentTestCase(name='success case',
                              inputs={'k1': 'v1',
                                      'k2': 'v2'},
                              parent_data={'k': 'v'},
                              execute_assertion=ExecuteAssertion(success=True,
                                                                 outputs={'k1': 'v1',
                                                                          'k2': 'v2',
                                                                          'parent_data': {'k': 'v'}}),
                              schedule_assertion=[ScheduleAssertion(success=True,
                                                                    outputs={'k1': 'v1',
                                                                             'k2': 'v2',
                                                                             'count': 1,
                                                                             'parent_data': {'k': 'v'}},
                                                                    callback_data=None),
                                                  ScheduleAssertion(success=True,
                                                                    outputs={'k1': 'v1',
                                                                             'k2': 'v2',
                                                                             'count': 2,
                                                                             'parent_data': {'k': 'v'}},
                                                                    callback_data=None),
                                                  ScheduleAssertion(success=True,
                                                                    schedule_finished=True,
                                                                    outputs={'k1': 'v1',
                                                                             'k2': 'v2',
                                                                             'count': 2,
                                                                             'parent_data': {'k': 'v'}},
                                                                    callback_data=None)]),
            ComponentTestCase(name='execute fail case',
                              inputs={'k1': 'v1',
                                      'k2': 'v2',
                                      'fail': True},
                              parent_data={'k': 'v'},
                              execute_assertion=ExecuteAssertion(success=False,
                                                                 outputs=None),
                              schedule_assertion=None),
            ComponentTestCase(name='schedule fail case',
                              inputs={'k1': 'v1',
                                      'k2': 'v2',
                                      'schedule_fail': True},
                              parent_data={'k': 'v'},
                              execute_assertion=ExecuteAssertion(success=True,
                                                                 outputs={'k1': 'v1',
                                                                          'k2': 'v2',
                                                                          'schedule_fail': True,
                                                                          'parent_data': {'k': 'v'}}),
                              schedule_assertion=ScheduleAssertion(success=False,
                                                                   outputs=None,
                                                                   callback_data=None
                                                                   ))]
```

可以看到我们定义了三个测试用例：

- `success case`：在这个用例中，我们测试了组件成功执行的情况。在执行断言中：我们根据组件的行为对输出数据进行了断言；在调度断言中，我们定义了三个断言对象，并根据组件的行为分别对不同调度中的输出数据及调度完成情况进行断言。
- `execute fail case`：在这个用例中，我们测试了组件服务 `execute` 方法执行失败的情况，由于 `execute` 方法执行失败后不会再进入调度状态，所以我们没有设置调度断言。
- `schedule fail case`：在这个用例中，我们测试了组件服务 `schedule` 方法执行失败的情况。
