# Tastypie Authorization

如果你在项目中使用了 Tastypie 来暴露资源操作的接口，那么你可以借助 auth backend 中 tastypie 的 Authorization 插件来为已有的接口接入鉴权功能，只需几行配置代码。

## 使用示例

假设你的项目中存在一个名为 `Project` 的模型和对应的资源模型：

```python
class Project(models.Model):
    name = models.CharField(_(u"项目名"), max_length=256)
    time_zone = models.CharField(_(u"项目时区"), max_length=100, blank=True)
    creator = models.CharField(_(u"创建者"), max_length=256)
    desc = models.CharField(_(u"项目描述"), max_length=512, blank=True)
    create_at = models.DateTimeField(_(u"创建时间"), auto_now_add=True)
    from_cmdb = models.BooleanField(_(u"是否是从 CMDB 业务同步过来的项目"), default=False)
    bk_biz_id = models.IntegerField(_(u"业务同步项目对应的 CMDB 业务 ID"), default=-1)
    is_disable = models.BooleanField(_(u"是否已停用"), default=False)

project_resource = DjangoModelResource(
    rtype='project',
    name=u"项目",
    scope_type='system',
    scope_type_name=u"系统",
    scope_id='bk_sops',
    scope_name=u"标准运维",
    actions=[
        Action(id='create', name=u"新建", is_instance_related=False),
        Action(id='view', name=u"查看", is_instance_related=True),
        Action(id='edit', name=u"编辑", is_instance_related=True),
    ],
    operations=[
        {
            'operate_id': 'create',
            'actions_id': ['create']
        },
        {
            'operate_id': 'view',
            'actions_id': ['view']
        },
        {
            'operate_id': 'edit',
            'actions_id': ['view', 'edit']
        }
    ],
    resource_cls=Project,
    id_field='id',
    inspect=FixedCreatorFieldInspect(creator_type='user',
                                     creator_id_f='creator',
                                     resource_id_f='id',
                                     resource_name_f='name',
                                     parent_f=None,
                                     scope_id_f=None))
```

那么你只需要在该模型对应的 tastypie 资源中添加对应的权限配置即可：

```python
from tastypie.resources import ModelResource

from auth_backend.plugins.tastypie.authorization import BkSaaSLooseAuthorization

from somewhere import project_resource

class ProjectResource(ModelResource):

    ...

    class Meta():
        auth_resource = project_resource
        authorization = BkSaaSLooseAuthorization(auth_resource=auth_resource,
                                                 read_action_id='view',
                                                 update_action_id='edit')

```

## Authorization 类型 

auth backend 提供了四种类型的 Authorization：

- `BkSaaSReadOnlyAuthorization`：严格只读类型校验，只允许资源的读请求；**在返回资源列表时不会返回用户无权限的实例**。
- `BkSaaSAuthorization`：严格类型校验，**在返回资源列表时不会返回用户无权限的实例**。
- `BkSaaSLooseReadOnlyAuthorization`：宽松只读类型校验，只允许资源的读请求，**在返回资源列表时会返回用户无权限的实例**。
- `BkSaaSLooseAuthorization`：宽松类型校验，**在返回资源列表时会返回用户无权限的实例**。

## Authorization 参数

Authorization 在创建时有以下参数：

- `auth_resource`：校验对应的资源模型。
- `create_action_id`（可选）：实例创建操作在资源模型中对应的 action id，默认为 `create`。
- `read_action_id`（可选）：读实例操作在资源模型中对应的 action id，默认为 `read`。
- `update_action_id`（可选）：更新实例操作在资源模型中对应的 action id，默认为 `update`。
- `delete_action_id`（可选）：删除实例操作在资源模型中对应的 action id，默认为 `delete`。
- `create_delegation`（可选）：创建实例操作鉴权代理对象，详情请看下方的 *鉴权代理* 小节。
- `scope_inspect`（可选）：[作用域探测器](inspect.md)，需要从 tastypie 的 bundle 中探测出当前用户操作所在的作用域信息。

## 鉴权代理

有些场景下，对某个资源的操作可能需要代理给另外一个资源来进行鉴权，例如：我们要执行任务（task）的创建操作，但是我们需要将这个操作的权限判断叫给其父资源项目（project）来完成，因为新建任务这个操作属于项目（project）资源而非任务（task）资源。

借助鉴权代理就能够解决这个问题：

```python

from tastypie.resources import ModelResource

from auth_backend.plugins.delegation import RelateAuthDelegation
from auth_backend.plugins.tastypie.authorization import BkSaaSLooseAuthorization

from somewhere import project_resource, task_resource

class TaskResource(ModelResource):
    ...

    class Meta():
        create_delegation = RelateAuthDelegation(delegate_resource=project_resource,
                                                 action_ids=['create_task'],
                                                 delegate_instance_f='project')
        auth_resource = task_resource
        authorization = BkSaaSLooseAuthorization(auth_resource=auth_resource,
                                                 read_action_id='view',
                                                 update_action_id='edit',
                                                 create_delegation=create_delegation)
```

上述的代码中就将任务（task）的新建权限判断代理到了项目（project）来进行。

### RelateAuthDelegation

如果你的代理对象能够通过当前的资源实例获取到，那么 `RelateAuthDelegation` 能够帮你完成这项工作。`RelateAuthDelegation` 接收以下参数：

- `delegate_resource`：代理资源模型。
- `action_ids`：代理操作 ID 列表。
- `delegate_instance_f`（可选）：被代理资源实例中存储代理资源实例的字段，若该字段为空则进行与不绑定资源实例的操作鉴权。

### 自定义代理

如果你所处理的场景十分的特殊，现有的代理对象无法满足你的需求，那么你可以自定义代理对象，所有的代理对象都需要继承 `auth_backend.plugins.delegation.AuthDelegation`：

```python
class AuthDelegation(object):
    def __init__(self, delegate_resource, action_ids):
        self.delegate_resource = delegate_resource
        self.action_ids = action_ids

    @abstractmethod
    def delegate_instance(self, client_instance):
        raise NotImplementedError()
```

`delegate_instance` 方法负责返回 `client_instance` 实例所对应的代理实例。