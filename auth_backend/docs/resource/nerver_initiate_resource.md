# NeverInitiateResource

在我们的系统中，难免有一些全局的资源，这些资源永远不会被实例化，auth backend 提供了 `NeverInitiateResource` 来处理这种类型的资源。

## 使用 NeverInitiateResource

假设我们需要对系统中的运营数据进行查看和编辑的权限控制，那么 `NeverInitiateResource` 就能够派上用场：

```python
from auth_backend.resources.base import Action, NeverInitiateResource

operate_data_resource = NeverInitiateResource(
    rtype='operate_data',
    name=_(u"运营数据"),
    scope_type='system',
    scope_type_name=u"系统",
    scope_id='bk_sops',
    scope_name=_(u"标准运维"),
    actions=[
        Action(id='view', name=_(u"查看"), is_instance_related=False),
        Action(id='edit', name=_(u"编辑"), is_instance_related=False)
    ])
```