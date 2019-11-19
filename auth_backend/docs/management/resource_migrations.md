# 资源变更（Resource Migrations)

auth backend 提供了系统中权限模型变更的检测机制，与 Django Model Migration 机制一样，在检测到变更后，auth backend 会自动生成当前系统中权限模型的快照，并在应用部署时向权限中心提交本次变更，保持权限中心的权限模型与系统中定义模型的一致性。如果是第一次进行执行变更，auth backend 还会向权限中心注册系统信息。

## 检测系统中权限模型的变更

执行 `python manage.py perms_makemigrations` 命令，框架会扫描当前系统中的资源模型，并生成对应的快照和变更数据。

## 执行权限模型的变更

执行 `python manage.py migrate` 命令，则会将当前变更注册到权限中心。如果是第一次生成权限模型快照，框架会自动向权限中心进行系统注册的初始化操作。

## 相关配置

### AUTH_BACKEND_RESOURCE_MIGRATION_CLASS

资源模型变更执行时所使用的类，若该配置为空，则不会向权限中心注册变更，请将以下配置添加到生产环境和预发布环境中：

```python
AUTH_BACKEND_RESOURCE_MIGRATION_CLASS = 'auth_backend.resources.migrations.migration.BKIAMResourceMigration'
```


> **由于 resource migration 复用了 Django Migration 的变更执行功能，并且将变更文件存储在 `auth_backend/migrations` 目录下，若您需要为 auth_backend 添加 Django Model，请在子 APP 的方式进行 Model 的声明，防止 Django 生成的 Model Migration 文件污染 `auth_backend/migrations` 目录。**