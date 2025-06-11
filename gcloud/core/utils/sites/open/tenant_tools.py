from threading import local

# 创建线程局部存储对象
_thread_locals = local()


def get_current_tenant_id():
    """获取当前线程的租户ID"""
    return getattr(_thread_locals, "tenant_id", "default")


def set_current_tenant_id(tenant_id):
    """设置当前线程的租户ID"""
    _thread_locals.tenant_id = tenant_id
