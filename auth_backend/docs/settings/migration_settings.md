# 资源变更相关配置

## AUTH_BACKEND_RESOURCE_MIGRATION_CLASS

资源模型变更执行时所使用的类，若该配置为空，则不会向权限中心注册变更。

示例：

```python
AUTH_BACKEND_RESOURCE_MIGRATION_CLASS = 'auth_backend.resources.migrations.migration.BKIAMResourceMigration'
```