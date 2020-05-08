# auth backend

auth backend 是为 Python 应用提供的基于资源模型与操作的鉴权后端框架，其主要功能为：

- 提供资源的定义
- 提供与第三方系统无关的鉴权后端接口及实现
- 管理系统中的资源（感知，收集，管理变更）
- 提供便利插件，快速接入第三方框架的鉴权流程

## quick start

### 1. 将 auth_backend, bkiam 添加到项目根目录下

```text
.
├── __init__.py
├── auth_backend
├── bkiam
├── ...
```

### 2. 将 auth_backend 添加到 INSTALLED_APPS 中

```python
INSTALLED_APPS += (
    ...
    'auth_backend',
    ...
)
```

### 3. 添加基本配置

```python
BK_IAM_SYSTEM_ID = os.getenv('BKAPP_BK_IAM_SYSTEM_ID', APP_CODE)  # 系统注册到权限中心的系统名
BK_IAM_SYSTEM_NAME = os.getenv('BKAPP_BK_IAM_SYSTEM_NAME', u"测试系统")  # 系统注册到权限中心的系统名
BK_IAM_SYSTEM_DESC = ''  # 系统注册到权限中心的系统描述
BK_IAM_QUERY_INTERFACE = '' # 权限中心获取资源接口，目前填空即可
BK_IAM_RELATED_SCOPE_TYPES = 'system' # 系统关联的作用域类型，多个作用域用 ; 分隔
BK_IAM_SYSTEM_MANAGERS = 'admin' # 系统管理员，多个管理员用 ; 分隔
BK_IAM_SYSTEM_CREATOR = 'admin' # 系统创建者
BK_IAM_INNER_HOST = os.getenv('BK_IAM_INNER_HOST', '') # 权限中心的 HOST
BK_IAM_APP_CODE = os.getenv('BKAPP_BK_IAM_APP_CODE', 'bk_iam_app') # 权限中心的 APP CODE
AUTH_BACKEND_CLS = os.getenv('BKAPP_AUTH_BACKEND_CLS', 'auth_backend.backends.bkiam.BkIAMBackend') # 使用的鉴权后端类，默认使用权限中心作为鉴权后端
```

## 使用文档

- resource
  - [定义系统中的资源](docs/resource/define_your_resource.md)
  - [资源实例探测器](docs/resource/resource_instance_inspect.md)
- common resource types
  - [DjangoModelResource](docs/resource/django_model_resource.md)
  - [NeverInitiateResource](docs/resource/nerver_initiate_resource.md)
- common plugins
  - [Http](docs/plugins/http.md)
  - [Decorators](docs/plugins/decorators.md)
  - [Shortcuts](docs/plugins/shortcuts.md)
  - [Middlewares](docs/plugins/middlewares.md)
- tastypie plugins
  - [Authorization](docs/plugins/tastypie/authorization.md)
  - [Resource](docs/plugins/tastypie/resource.md)
  - [Shortcuts](docs/plugins/tastypie/shortcuts.md)
  - [ScopeInspect](docs/plugins/tastypie/inspect.md)
- backend
- management
  - [资源变更（Resource Migrations)](docs/management/resource_migrations.md)
  - [权限模板](docs/management/perms_templates.md)
- settings
  - [基本配置](docs/settings/basic_settings.md)
  - [资源变更](docs/settings/migration_settings.md)
  - [权限模板](docs/settings/templates_settings.md)