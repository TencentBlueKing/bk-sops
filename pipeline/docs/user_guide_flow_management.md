## 流程管理

在前面的章节中，我们学习了如何编排流程以及如何通过流程构造器来快速构造流程描述结构。但是在实际应用中，我们的流程结构一般不会经常发生变化，如果每次执行一个流程都要重新执行一遍流程构造逻辑未免过于麻烦。

好在 pipeline 提供了流程管理模型，通过使用**流程模板**和**流程实例**，能够让我们将流程管理的成本降到最低。

### 流程模板

![分支网关示例](https://raw.githubusercontent.com/homholueng/md_pic/master/pipeline_doc/exclusive_gateway.png)

假设我们要将上述流程存储起来，并在用户发起执行操作时根据用户传入的参数来执行该流程，如果我们不使用流程模板的话，我们就需要在每次用户发起执行动作时执行以下代码：

```python
from pipeline import builder
from pipeline.parser import PipelineParser
from pipeline.service import task_service
from pipeline.builder import (EmptyStartEvent, 
                              ServiceActivity, 
                              EmptyEndEvent, 
                              ExclusiveGateway, 
                              Var, 
                              Data,
                              NodeOutput)

start = EmptyStartEvent()
act_1 = ServiceActivity(component_code='pipe_example_component', name='act_1')
eg = ExclusiveGateway(
    conditions={
        0: '${act_1_output} < 0',
        1: '${act_1_output} >= 0'
    },
    name='act_2 or act_3'
)
act_2 = ServiceActivity(component_code='pipe_example_component', name='act_2')
act_3 = ServiceActivity(component_code='pipe_example_component', name='act_3')
end = EmptyEndEvent()

start.extend(act_1).extend(eg).connect(act_2, act_3).to(eg).converge(end)

act_1.component.inputs.input_a = Var(type=Var.SPLICE, value='${input_a}')

pipeline_data = Data()
pipeline_data.inputs['${input_a}'] = Var(type=Var.PLAIN, value=0)
pipeline_data.inputs['${act_1_output}'] = NodeOutput(type=Var.SPLICE, source_act=act_1.id, source_key='input_a')

tree = builder.build_tree(start, data=pipeline_data)
parser = PipelineParser(pipeline_tree=tree)
pipeline = parser.parse()


task_service.run_pipeline(pipeline)
```

也就是说，我们需要每次都要进行一个流程编排的操作，但是我们的流程结构时不变的，这一步操作就显得有些多余了。但是借助**流程模板**的话，我们就不需要每次都进行流程构造的操作，我们要做的是把一个流程的结构数据保存下来，并在每次执行前根据这个结构化的数据生成流程对象：

```python
from pipeline import builder
from pipeline.parser import PipelineParser
from pipeline.builder import (EmptyStartEvent, 
                              ServiceActivity, 
                              EmptyEndEvent, 
                              ExclusiveGateway, 
                              Var, 
                              Data,
                              DataInput,
                              NodeOutput)
from pipeline.models import PipelineTemplate

start = EmptyStartEvent()
act_1 = ServiceActivity(component_code='pipe_example_component', name='act_1')
eg = ExclusiveGateway(
    conditions={
        0: '${act_1_output} < 0',
        1: '${act_1_output} >= 0'
    },
    name='act_2 or act_3'
)
act_2 = ServiceActivity(component_code='pipe_example_component', name='act_2')
act_3 = ServiceActivity(component_code='pipe_example_component', name='act_3')
end = EmptyEndEvent()

start.extend(act_1).extend(eg).connect(act_2, act_3).to(eg).converge(end)

act_1.component.inputs.input_a = Var(type=Var.SPLICE, value='${input_a}')

pipeline_data = Data()
pipeline_data.inputs['${input_a}'] = DataInput(type=Var.PLAIN, value=0)
pipeline_data.inputs['${act_1_output}'] = NodeOutput(type=Var.SPLICE, source_act=act_1.id, source_key='input_a')

tree = builder.build_tree(start, data=pipeline_data)

template = PipelineTemplate.objects.create_model(structure_data=tree)
template.template_id  # adab2df7cca73e898f2f6c688aa37e24
same_template = PipelineTemplate.objects.get(template_id=template.template_id)
template.template_id == same_template.template_id  # True
```

至此，我们就完成了一个流程模板的创建，并且该模板已经被持久到数据库中。

### 流程实例

当我们拥有了流程模板后，我们就能够通过流程模板来创建流程实例。模板和实例的关系就像是面向对象设计中类和对象的关系，模板描述了一个流程的基本信息，而实例则是根据模板中所描述的信息创建出来的一个“快照”，实例在创建时会根据模板中存储的流程结构数据生成一份新的结构数据并保存下来。

```bash
>>> from pipeline.service import task_service
>>> from pipeline.models import PipelineTemplate
>>> template = PipelineTemplate.objects.get(template_id='adab2df7cca73e898f2f6c688aa37e24')
>>> instance = template.gen_instance(inputs={'${input_a}': -1})
>>> instance.start(executor='me')
>>> task_service.get_state(instance.instance_id)
{'children': {u'583b521fc677309fba0216d0c04928c4': {'finish_time': '2019-04-17 07:49:00',
   'id': u'583b521fc677309fba0216d0c04928c4',
   'loop': 1L,
   'name': u'act_2 or act_3',
   'retry': 0L,
   'skip': False,
   'start_time': '2019-04-17 07:49:00',
   'state': 'FINISHED'},
  u'765d2b31fd273571af7bea8f5fdbd5f2': {'finish_time': '2019-04-17 07:49:00',
   'id': u'765d2b31fd273571af7bea8f5fdbd5f2',
   'loop': 1L,
   'name': u'act_3',
   'retry': 0L,
   'skip': False,
   'start_time': '2019-04-17 07:49:00',
   'state': 'FINISHED'},
  u'a055740f3a4b3e46b06bb70ff40592fb': {'finish_time': '2019-04-17 07:49:00',
   'id': u'a055740f3a4b3e46b06bb70ff40592fb',
   'loop': 1L,
   'name': u"<class 'pipeline.core.flow.event.EmptyEndEvent'>",
   'retry': 0L,
   'skip': False,
   'start_time': '2019-04-17 07:49:00',
   'state': 'FINISHED'},
  u'ad178c995d0d373e8ca13fbc2fdb048f': {'finish_time': '2019-04-17 07:49:00',
   'id': u'ad178c995d0d373e8ca13fbc2fdb048f',
   'loop': 1L,
   'name': u"<class 'pipeline.core.flow.event.EmptyStartEvent'>",
   'retry': 0L,
   'skip': False,
   'start_time': '2019-04-17 07:49:00',
   'state': 'FINISHED'},
  u'b7ffc956b27f3e3f90ba5d4803648550': {'finish_time': '2019-04-17 07:49:00',
   'id': u'b7ffc956b27f3e3f90ba5d4803648550',
   'loop': 1L,
   'name': u'act_1',
   'retry': 0L,
   'skip': False,
   'start_time': '2019-04-17 07:49:00',
   'state': 'FINISHED'}},
 'finish_time': '2019-04-17 07:49:00',
 'id': u'1f898831a9483708851c5802aff526fa',
 'loop': 1L,
 'name': u"<class 'pipeline.core.pipeline.Pipeline'>",
 'retry': 0L,
 'skip': False,
 'start_time': '2019-04-17 07:49:00',
 'state': 'FINISHED'}
```

可以看到，我们通过 `instance = template.gen_instance(inputs={'${input_a}': -1})` 来根据模板创建除了流程实例，并修改了流程实例的全局变量；随后，我们调用 `instance` 的 `start()` 方法来启动该流程。

这样一来，一旦我们创建了模板，每次执行流程只需要通过该模板生成一个新的实例并启动即可，同时，流程实例也能够降低我们管理已执行的流程的成本。

### 使用流程模板来管理子流程

使用流程模板来管理流程还有一个好处，即我们能够通过流程模板的 ID 来构造子流程，下面的例子就很好的展示了如何使用已有的流程模板来构造子流程：

```python
from pipeline import builder
from pipeline.parser import PipelineParser
from pipeline.service import task_service
from pipeline.builder import (EmptyStartEvent, 
                              ServiceActivity, 
                              EmptyEndEvent, 
                              ExclusiveGateway, 
                              SubProcess,
                              Var, 
                              Data,
                              Params,
                              NodeOutput)
from pipeline.models import PipelineTemplate

start = EmptyStartEvent()
params = Params({
            '${input_a}': Var(type=Var.SPLICE, value='${constant_1}')
        })
subproc = SubProcess(template_id='adab2df7cca73e898f2f6c688aa37e24', params=params)
end = EmptyEndEvent()

start.extend(subproc).extend(end)

pipeline_data = Data()
pipeline_data.inputs['${constant_1}'] = Var(type=Var.PLAIN, value=-1)

tree = builder.build_tree(start, data=pipeline_data)

template = PipelineTemplate.objects.create_model(structure_data=tree)
instance = template.gen_instance()
instance.start(executor='me')
```

我们可以把注意力重点放在下面这两行代码上，首先我们创建了一个 `Params` 对象，`Params` 对象允许我们在子流程中引用父流程数据上下文中的变量，下面的代码中我们就创建了一个从子流程中的 `${input_a}` 变量到父流程中 `${constant_1}` 变量的引用。

然后，我们建立了一个子流程节点，这个子流程节点直接引用了模板 ID 为 `adab2df7cca73e898f2f6c688aa37e24` 的模板，这里我们直接省去了子流程结构的声明，因为子流程的结构已经存储在流程模板中了。

```python
params = Params({
            '${input_a}': Var(type=Var.SPLICE, value='${constant_1}')
        })
subproc = SubProcess(template_id='adab2df7cca73e898f2f6c688aa37e24', params=params)
```

最后我们将构造出来的流程结构保存到了一个新的模板中。其实我们可以把构造出来的流程结构打印出来看看：

```python
{'activities': {'aa3148edbe0e3ac4ac85d60aebbeed4d': {'id': 'aa3148edbe0e3ac4ac85d60aebbeed4d',
   'incoming': ['7bdd64f816f337c4985e55a10d0da10f'],
   'name': None,
   'outgoing': '28e3c65105ae3d868479cc2c99c398fd',
   'params': {'${input_a}': {'type': 'splice', 'value': '${constant_1}'}},
   'template_id': 'adab2df7cca73e898f2f6c688aa37e24',
   'type': 'SubProcess'}},
   ...}
```

不难发现，在子流程节点中我们只存储了模板 ID，而流程实例会在执行前去查询该节点所引用的模板的流程结构，并把这些结构添加到当前流程的结构中，就像我们之前手动构造的子流程节点一样。

