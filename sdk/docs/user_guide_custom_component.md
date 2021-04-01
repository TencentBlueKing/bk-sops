<!-- TOC -->

- [自定义组件](#自定义组件)
  - [开发一个自定义组件](#开发一个自定义组件)
    - [1. 使用 APP 统一管理你的组件](#1-使用-app-统一管理你的组件)
    - [2. 编写 Service](#2-编写-service)
    - [3. 编写 Component](#3-编写-component)
    - [4. 执行一下刚刚编写的组件](#4-执行一下刚刚编写的组件)
  - [组件的行为](#组件的行为)
    - [单次执行](#单次执行)
    - [周期性轮询](#周期性轮询)
    - [等待回调](#等待回调)
  - [组件的注册](#组件的注册)
  - [Component](#component)
    - [类属性](#类属性)
      - [name](#name)
      - [code](#code)
      - [bound_service](#bound_service)
      - [form](#form)
      - [version](#version)
      - [embedded_form](#embedded_form)
  - [Service](#service)
    - [类属性](#类属性-1)
      - [interval](#interval)
      - [`__need_schedule__`](#need_schedule)
    - [实例 API](#实例-api)
      - [execute](#execute)
      - [outputs_format](#outputs_format)
      - [inputs_format](#inputs_format)
      - [logger](#logger)
  - [Interval](#interval-1)
    - [StaticIntervalGenerator](#staticintervalgenerator)
    - [SquareIntervalGenerator](#squareintervalgenerator)
    - [LinearIntervalGenerator](#linearintervalgenerator)
    - [DefaultIntervalGenerator](#defaultintervalgenerator)
    - [自定义 interval](#自定义-interval)

<!-- /TOC -->

## 自定义组件

pipeline 开放了自定义组件的能力，开发者们能够开发针对某些特定业务场景的组件，将其添加到引擎的组件库中，并在 ServiceActivity 中调用他们。如之前的示例所示：

```python
act = ServiceActivity(component_code='example_component')
```

### 开发一个自定义组件

#### 1. 使用 APP 统一管理你的组件

组件开发的最佳实践是创建一个独立的 APP，并在这个 APP 中单独管理自定义的组件和组件需要使用到的一些公共逻辑。pipeline 提供了快捷命令，能够让我们快速的创建一个用于存放自定义组件的 APP，在 Django 工程根目录下执行以下命令：

```bash
$ python manage.py create_atoms_app custom_plugins
```

该命令会在 Django 工程根目录下生成拥有以下目录结构的 APP：

```text
custom_plugins
├── __init__.py
├── components
│   ├── __init__.py
│   └── collections
│       ├── __init__.py
│       └── plugins.py
├── migrations
│   └── __init__.py
└── static
    └── custom_plugins
        └── plugins.js
```

别忘了把新创建的 APP 添加到 Django 配置的 `INSTALLED_APPS` 中：

```python
INSTALLED_APPS = (
    ...
    'custom_plugins',
    ...
)
```

#### 2. 编写 Service

组件服务 `Service` 是组件的核心，`Service` 定义了组件被调用时执行的逻辑，下面让我们实现一个计算传入的参数 `n` 的阶乘，并把结果写到输出中的 `Service`，在 `custom_plugins/components/collections/plugins.py` 中输入以下代码：

```python
import math
from pipeline.core.flow.activity import Service


class FactorialCalculateService(Service):

    def execute(self, data, parent_data):
        n = data.get_one_of_inputs('n')
        if not isinstance(n, int):
            data.outputs.ex_data = 'n must be a integer!'
            return False

        data.outputs.factorial_of_n = math.factorial(n)
        return True

    def inputs_format(self):
        return [
            Service.InputItem(name='integer n', key='n', type='int', required=True)
        ]

    def outputs_format(self):
        return [
            Service.OutputItem(name='factorial of n', key='factorial_of_n', type='int')
        ]

```

首先我们继承了 `Service` 基类，并实现了 `execute()` 和 `outputs_format()` 这两个方法，他们的作用如下：

- `execute`：组件被调用时执行的逻辑。接收 `data` 和 `parent_data` 两个参数，`data` 是当前节点的数据对象，这个数据对象存储了用户传递给当前节点的参数的值以及当前节点输出的值。`parent_data` 则是该节点所属流程对象的数据对象，通常会将一些全局使用的常量存储在该对象中，如当前流程的执行者、流程的开始时间等。
- `outputs_format`：组件执行成功时输出的字段，每个字段都包含字段名、字段键及字段类型的说明。这个方法必须返回一个 `OutputItem` 的数组，返回的这些信息能够用于确认某个组件在执行成功时输出的数据，便于在流程上下文或后续节点中进行引用。
- `inputs_format`：组件所需的输入字段，每个字段都包含字段名、字段键、字段类型及是否必填的说明。这个方法必须返回一个 `InputItem` 的数组，返回的这些信息能够用于确认某个组件需要获取什么样的输入数据。

下面我们来看一下 `execute()` 方法内部执行的逻辑，首先我们尝试从当前节点数据对象的输出中获取输入参数 `n`，如果获取到的参数不是一个 `int` 实例，那么我们会将异常信息写入到当前节点输出的 `ex_data` 字段中，**这个字段是引擎内部的保留字段，节点执行失败时产生的异常信息都应该写入到该字段中**。随后我们返回 `False` 代表组件本次执行失败，随后节点会进入失败状态：

```
n = data.get_one_of_inputs('n')
if not isinstance(n, int):
    data.outputs.ex_data = 'n must be a integer!'
    return False
```

若获取到的 `n` 是一个正常的 `int`，我们就调用 `math.factorial()` 函数来计算 `n` 的阶乘，计算完成后，我们会将结果写入到输出的 `factorial_of_n` 字段中，以供流程中的其他节点使用：

```
data.outputs.factorial_of_n = math.factorial(n)
return True
```

#### 3. 编写 Component

完成 `Service` 的编写后，我们需要将其与一个 `Component` 绑定起来，才能够注册到组件库中：

```python
from pipeline.component_framework.component import Component

class FactorialCalculateComponent(Component):
    name = 'FactorialCalculateComponent'
    code = 'fac_cal_comp'
    bound_service = FactorialCalculateService

```

我们定义了一个继承自基类 `Component` 的类 `FactorialCalculateComponent`，他拥有以下属性：

- `name`：组件名。
- `code`：组件代码，这个代码必须是全局唯一的。
- `bound_service`：与该组件绑定的 `Service`。

这样一来，我们就完成了一个自定义组件的开发。

#### 4. 执行一下刚刚编写的组件

完成组件的编写后，让我们在流程中执行以下刚刚编写好的组件验证以下：

```python
from pipeline import builder
from pipeline.builder import Var
from pipeline.builder import EmptyStartEvent, ServiceActivity, EmptyEndEvent
from pipeline.parser import PipelineParser
from pipeline.service import task_service

# 使用 builder 构造出流程描述结构
start = EmptyStartEvent()
act = ServiceActivity(component_code='fac_cal_comp')
act.component.inputs.n = Var(type=Var.PLAIN, value=4)
end = EmptyEndEvent()

start.extend(act).extend(end)

tree = builder.build_tree(start)

# 根据流程描述结构创建流程对象
parser = PipelineParser(pipeline_tree=tree)
pipeline = parser.parse()

# 执行流程对象
task_service.run_pipeline(pipeline)
```

可以看到，我们能够通过 `component_code` 来引用刚刚编写的组件，然后我们将该组件的输入 `n` 的值设置为 `4`：

```python
act = ServiceActivity(component_code='fac_cal_comp')
act.component.inputs.n = Var(type=Var.PLAIN, value=4)
```

流程运行完后，获取节点的执行结果，可以看到，该节点输出了 `factorial_of_n`，并且值为 24(4 * 3 * 2 *1)，这正是我们需要的效果：

```bash
>>> task_service.get_outputs(act.id)
{'ex_data': None,
 'outputs': {'_loop': 0, '_result': True, 'factorial_of_n': 24}}
```

### 组件的行为

我们在上一节中定义的 `FactorialCalculateService` 在完成 `execute()` 的执行后即认为该组件已经执行完成。但是在某些场景下，这样的行为并不能满足我们的需求，例如调用第三方系统的接口启动一个任务，并周期性的轮询该任务的状态，随后根据任务状态确认执行结果；或是调用第三方系统启动任务后等待第三方系统回调并根据回调数据确认执行结果。

为了满足上述的场景，pipeline 中的组件执行时的行为有以下三种：

- 单次执行：默认的执行方式，完成 `execute()` 的执行后即认为该组件已经执行完毕。
- 周期性轮询：完成 `execute()` 的执行后，还会周期性的执行 `schedule()` 方法，直至满足一定的条件为止。
- 等待回调：完成 `execute()` 的执行后，会等待外部回调，接收到回调后会执行一次 `schedule()` 方法。

总结起来，组件的执行方式可以用一条公式概括： `execute + n * schedule`。


#### 单次执行

这是组件默认的执行方式，在这种模式下，一旦 `execute()` 方法执行完成后，该组件即视为执行完成。执行结果会根据 `execute()` 的返回值来判断：

- `False`：执行失败，节点会进入 FAILED 状态。
- `True` 或 `None`：执行成功，节点会进入 FINISHED 状态。

#### 周期性轮询

如果我们需要周期性的轮询第三方平台的接口，那么可以使用周期性轮询的执行方式，下面的代码定义了一个周期性轮询的组件服务：

```python
from pipeline.core.flow.activity import Service, StaticIntervalGenerator

class ScheduleService(Service):
    __need_schedule__ = True
    interval = StaticIntervalGenerator(2)


    def _get_poll_url(self):
        pass

    def _poll_status(self, poll_url):
        pass

    def execute(self, data, parent_data):
        poll_url = self._get_poll_url()
        data.outputs.poll_url = poll_url
        return True

    def schedule(self, data, parent_data, callback_data=None):

        poll_url = data.get_one_of_outputs('poll_url')
        status = self._poll_status(poll_url)

        if status == 0:
            self.finish_schedule()
        elif status < 0:
            data.outputs.ex_data = 'task failed with code: %s' % status
            return False

        return True


```

让我们来拆分一下这个组件服务的定义，一个周期性轮询组件服务必须包含两个类属性：
 
 - `__need_schedule__`： 表示当前组件服务是否需要调度，周期性轮询的方式下必须将该字段设置为 `True`
 - `interval`：轮询间隔生成器，周期性轮询方式下该字段必须为 `AbstractIntervalGenerator` 的子类。


我们在 `execute()` 中调用第三方系统获取了用于轮询的 `poll_url`，并将其写入到输出中（**如果在 `execute()` 方法中返回了 `False`，那么当前节点会进入 FAILED 状态，不会进入之后的轮询阶段**）：

```python
    def execute(self, data, parent_data):
        poll_url = self._get_poll_url()
        data.outputs.poll_url = poll_url
        return True
```

下面看看 `schedule()` 方法的定义，该方法接收三个参数：

- `data`： 当前节点的数据对象，这个数据对象存储了用户传递给当前节点的参数的值以及当前节点输出的值。
- `parent_data`： 该节点所属流程对象的数据对象。
- `callback_data`：回调数据，在等待回调模式下由第三方系统传入的数据。

我们在 `schedule()` 方法中，使用在 `execute()` 中设置到输出中的 `poll_url` 来轮询第三方系统的状态，并根据其返回值来决定该次轮询的结果：

- `True`：当次轮询成功，若轮询已完成则节点会进入 FINISHED 状态，否则仍然处于 RUNNING 状态，等待进入下次轮询。
- `False`：当次轮询失败，节点会进入 FAILED 状态。

当轮询完成后，即可调用 `finish_schedule()` 方法：

```python
    def schedule(self, data, parent_data, callback_data=None):

        poll_url = data.get_one_of_outputs('poll_url')
        status = self._poll_status(poll_url)

        if status == 0:
            self.finish_schedule()
        elif status < 0:
            data.outputs.ex_data = 'task failed with code: %s' % status
            return False

        return True
```

下面让我们了解一下轮询间隔生成器，间隔生成器必须拥有 `next()` 方法，该方法返回一个整数，代表每次轮询时间的时间间隔，单位为秒。一般我们会继承 `AbstractIntervalGenerator` 来定义新的生成器。下面的代码定义了一个间隔线性增长的生成器，轮询时间间隔会根据轮询次数的增长而增长：

```python
from pipeline.core.flow.activity import AbstractIntervalGenerator

class LinearIntervalGenerator(AbstractIntervalGenerator):
    def next(self):
        super(DefaultIntervalGenerator, self).next()
        return self.count

```

`AbstractIntervalGenerator` 中的 `count` 属性表示本次轮询的轮次，**在实现自定义的 `next()` 方法时一定要调用父类的 `next()` 方法**。

#### 等待回调

如果第三方系统提供了回调机制，那我们就可以将组件服务设置为等待回调的模式：

```python
from pipeline.core.flow.activity import Service

class WaitCallbackService(Service):
    __need_schedule__ = True

    def _external_api_call(self):
        pass

    def execute(self, data, parent_data):
        self._external_api_call()
        return True

    def schedule(self, data, parent_data, callback_data=None):

        status = self.callback_data['status']

        if status < 0:
            data.outputs.ex_data = 'task failed with code: %s' % status
            return False

        return True
```

让我们来拆分一下这个组件服务的定义，一个等待回调型组件服务必须包含这个类属性：

- `__need_schedule__`： 表示当前组件服务是否需要调度，等待回调的方式下必须将该字段设置为 `True`

等待回调型的组件服务于周期轮询型的差异在于 `interval` 这个类属性，周期轮训型的服务该属性的值为间隔生成器，而回调型的服务该属性的值为 `None`。

我们在 `execute()` 方法中只做了一次 api 调用，然后就进入了等待回调的状态（**如果在 `execute()` 方法中返回了 `False`，那么当前节点会进入 FAILED 状态，不会进入之后的等待回调阶段**）：

```python
    def execute(self, data, parent_data):
        self._external_api_call()
        return True
```

在 `schedule()` 方法中，我们检测第三方系统回调时传入的数据，来判断本次执行是否成功：

```python
    def schedule(self, data, parent_data, callback_data=None):

        status = self.callback_data['status']

        if status < 0:
            data.outputs.ex_data = 'task failed with code: %s' % status
            return False

        return True
```

### 组件的注册

pipeline 通过插件自动发现机制，在启动 SaaS 服务时扫描每个已经注册到 Django 中的 APP （INSTALLED_APPS）下特定的目录（包括子目录），自动发现并注册合法的插件，这些待扫描的目录能够通过 Django settings 下的 `COMPONENT_PATH` 进行配置：

```python
COMPONENT_PATH = [
    'custom.components.path',
]
```

pipeline 默认会扫描已注册 APP 的 `components.collections` 目录，尝试从该目录下（包括子目录）所有的 Python 模块中发现并注册合法的标准插件。

pipeline 插件自动发现机制的实现代码可以参考 `pipeline.component_framework.apps` 和 `pipeline.utils.register` 模块。


现在回过头来看看我们之前创建的 APP，其目录结构与 pipeline 默认扫描的路径一致，所以我们在 `custom_plugins.components.collections.atom` 模块中定义的组件就会自动的被注册到组件库中：

```text
custom_plugins
├── __init__.py
├── components
│   ├── __init__.py
│   └── collections
│       ├── __init__.py
│       └── plugins.py
├── migrations
│   └── __init__.py
└── static
    └── custom_plugins
        └── plugins.js
```

### Component

#### 类属性

##### name

##### code

##### bound_service

##### form

##### version

##### embedded_form

### Service

#### 类属性

##### interval

##### `__need_schedule__`

#### 实例 API

##### execute

##### outputs_format

##### inputs_format

##### logger

### Interval

#### StaticIntervalGenerator

#### SquareIntervalGenerator

#### LinearIntervalGenerator

#### DefaultIntervalGenerator

#### 自定义 interval