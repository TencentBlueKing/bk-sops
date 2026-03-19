# Django QuerySet SQL 查看指南

## 🎯 快速方法汇总

### 方法1: 使用 `.query` 属性（最简单）⭐⭐⭐

```python
# 在Django shell或代码中
from gcloud.taskflow3.models import TaskFlowInstance

qs = TaskFlowInstance.objects.filter(engine_ver=2).order_by('id')[:10]
print(str(qs.query))
```

**输出示例**:
```sql
SELECT * FROM `taskflow3_taskflowinstance` WHERE `engine_ver` = 2 ORDER BY `id` ASC LIMIT 10
```

**使用场景**:
- ✅ 查看QuerySet生成的SQL（不实际执行）
- ✅ 调试查询逻辑
- ✅ 优化查询性能

**注意事项**:
- ❌ 不显示参数化后的实际值
- ❌ 看不到实际执行的SQL（如果有中间层处理）
- ❌ 执行后的QuerySet不能再用`.query`

---

### 方法2: 使用 `connection.queries`（查看实际执行的SQL）⭐⭐

```python
from django.db import connection, reset_queries

# 1. 重置查询历史
reset_queries()

# 2. 执行你的查询
qs = TaskFlowInstance.objects.filter(id__in=[1, 2, 3])
list(qs)  # 强制执行

# 3. 查看所有执行的SQL
for query in connection.queries:
    print(query['sql'])
    print(f"耗时: {query['time']}秒\n")
```

**前提条件**:
```python
# settings.py中需要
DEBUG = True  # 生产环境不要开启！
```

**使用场景**:
- ✅ 查看实际执行的SQL（包含参数值）
- ✅ 统计SQL数量（N+1问题检测）
- ✅ 查看执行时间
- ✅ 调试性能问题

---

### 方法3: 在项目中直接使用（推荐）⭐⭐⭐

#### 步骤1: 进入Django shell

```bash
cd /root/Projects/bk-sops
source ~/.envs/bk-sops/bin/activate
export $(cat .env | xargs)
python manage.py shell
```

#### 步骤2: 执行查询并查看SQL

```python
# 在shell中
from gcloud.taskflow3.models import TaskFlowInstance
from django.utils import timezone
from datetime import timedelta

# 创建查询
qs = TaskFlowInstance.objects.filter(
    engine_ver=2,
    pipeline_instance__create_time__lt=timezone.now() - timedelta(days=30)
).select_related('pipeline_instance')[:10]

# 查看SQL
sql = str(qs.query)
# 格式化显示
print(sql.replace(' FROM ', '\nFROM ').replace(' WHERE ', '\nWHERE ').replace(' INNER JOIN ', '\nINNER JOIN '))
```

#### 步骤3: 使用提供的脚本

```bash
# 在shell中执行
exec(open('show_sql.py').read())
```

---

### 方法4: 使用 Django logging（生产环境推荐）⭐⭐

在 `settings.py` 或 `local_settings.py` 中添加：

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/tmp/django_sql.log',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',  # 记录所有SQL
            'propagate': False,
        },
    },
}
```

**使用场景**:
- ✅ 生产环境调试（临时开启）
- ✅ 持久化SQL日志
- ✅ 不影响代码逻辑

**查看日志**:
```bash
tail -f /tmp/django_sql.log
```

---

### 方法5: 使用 `.explain()`（查看执行计划）⭐

```python
# Django 2.1+
qs = TaskFlowInstance.objects.filter(engine_ver=2)
print(qs.explain())

# 或带参数
print(qs.explain(verbose=True, analyze=True))
```

**输出示例**:
```
-> Index Lookup on taskflow3_taskflowinstance using idx_engine_ver
   (cost=0.35 rows=10)
```

**使用场景**:
- ✅ 分析查询性能
- ✅ 检查是否使用索引
- ✅ 优化慢查询

---

## 📚 实际应用示例

### 示例1: 检查清理任务的SQL

```python
# 在Django shell中
from gcloud.contrib.cleaner.tasks import filter_clean_task_instances
from django.db import connection, reset_queries

# 重置查询记录
reset_queries()

# 执行函数
result = filter_clean_task_instances()

# 查看执行的SQL
print(f"执行了 {len(connection.queries)} 条SQL")
for i, q in enumerate(connection.queries, 1):
    print(f"\nSQL #{i}:")
    print(q['sql'])
    print(f"耗时: {q['time']}秒")
```

### 示例2: 对比优化前后的SQL

```python
from gcloud.taskflow3.models import TaskFlowInstance
from django.db import connection, reset_queries

# 优化前：N+1查询问题
reset_queries()
tasks = TaskFlowInstance.objects.filter(engine_ver=2)[:10]
for task in tasks:
    _ = task.pipeline_instance.create_time  # 每次都查询
print(f"执行了 {len(connection.queries)} 条SQL")  # 可能是11条（1+10）

# 优化后：使用select_related
reset_queries()
tasks = TaskFlowInstance.objects.filter(engine_ver=2).select_related('pipeline_instance')[:10]
for task in tasks:
    _ = task.pipeline_instance.create_time  # 不会额外查询
print(f"执行了 {len(connection.queries)} 条SQL")  # 只有1条
```

### 示例3: 检查是否使用索引

```python
qs = TaskFlowInstance.objects.filter(engine_ver=2)

# 查看执行计划
print(qs.explain())

# 如果看到 "Full Table Scan"，说明没有使用索引
# 如果看到 "Index Lookup"，说明使用了索引
```

---

## 🔧 常用技巧

### 1. 格式化SQL输出

```python
def format_sql(sql):
    """格式化SQL使其更易读"""
    sql = sql.replace(' FROM ', '\nFROM ')
    sql = sql.replace(' WHERE ', '\nWHERE ')
    sql = sql.replace(' INNER JOIN ', '\nINNER JOIN ')
    sql = sql.replace(' LEFT JOIN ', '\nLEFT JOIN ')
    sql = sql.replace(' ORDER BY ', '\nORDER BY ')
    sql = sql.replace(' LIMIT ', '\nLIMIT ')
    sql = sql.replace(' AND ', '\n  AND ')
    sql = sql.replace(' OR ', '\n  OR ')
    return sql

# 使用
qs = TaskFlowInstance.objects.filter(engine_ver=2)
print(format_sql(str(qs.query)))
```

### 2. 统计查询次数（检测N+1问题）

```python
from django.db import connection
from functools import wraps

def count_queries(func):
    """装饰器：统计函数执行的SQL数量"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        from django.db import reset_queries
        reset_queries()
        result = func(*args, **kwargs)
        print(f"[{func.__name__}] 执行了 {len(connection.queries)} 条SQL")
        return result
    return wrapper

# 使用
@count_queries
def my_function():
    tasks = TaskFlowInstance.objects.filter(engine_ver=2)[:10]
    for task in tasks:
        print(task.id)
```

### 3. 查找慢查询

```python
from django.db import connection

# 执行一些操作
# ...

# 找出慢查询（>0.1秒）
slow_queries = [q for q in connection.queries if float(q['time']) > 0.1]
for q in slow_queries:
    print(f"慢查询 ({q['time']}秒):")
    print(q['sql'])
    print()
```

---

## ⚠️ 注意事项

### 1. DEBUG模式的影响

```python
# ❌ 生产环境不要这样做
DEBUG = True  # 会记录所有SQL，占用大量内存

# ✅ 生产环境临时调试
if os.getenv('TEMP_DEBUG') == '1':
    DEBUG = True
```

### 2. QuerySet的惰性求值

```python
# 这不会执行SQL
qs = TaskFlowInstance.objects.filter(engine_ver=2)
print(str(qs.query))  # ✅ 可以查看SQL

# 这会执行SQL
list(qs)  # 执行
qs.count()  # 执行
for item in qs:  # 执行
    pass

# 执行后不能再用.query
list(qs)
print(str(qs.query))  # ❌ 可能出错或显示缓存的查询
```

### 3. connection.queries的内存占用

```python
# 长时间运行的任务
for i in range(10000):
    TaskFlowInstance.objects.filter(id=i).first()
    # connection.queries会越来越大！

# 解决方案：定期重置
from django.db import reset_queries
for i in range(10000):
    TaskFlowInstance.objects.filter(id=i).first()
    if i % 100 == 0:
        reset_queries()  # 每100次重置一次
```

---

## 📝 针对清理任务的SQL调试

### 查看filter_clean_task_instances的SQL

```python
# 在Django shell中
from django.conf import settings
from django.utils import timezone
from gcloud.taskflow3.models import TaskFlowInstance
from django.db.models import Q

validity_day = settings.V2_TASK_VALIDITY_DAY
expire_time = timezone.now() - timezone.timedelta(days=validity_day)

base_q = Q(
    pipeline_instance__create_time__lt=expire_time,
    engine_ver=2,
    pipeline_instance__is_expired=False,
)

qs = TaskFlowInstance.objects.filter(base_q).order_by("id")[:20]

# 查看SQL
sql = str(qs.query)
print(sql.replace(' FROM ', '\nFROM ').replace(' WHERE ', '\nWHERE '))
```

### 查看删除操作的SQL

```python
from pipeline.eri.models import State

# 删除操作会先SELECT再DELETE
qs = State.objects.filter(node_id__in=['node1', 'node2'])

print("将执行的SELECT:")
print(str(qs.query))

print("\n然后执行DELETE:")
print("DELETE FROM pipeline_eri_state WHERE id IN (...)")

# 实际删除（⚠️ 慎用）
# qs.delete()
```

---

## 🚀 快速开始

最简单的方法：

```bash
# 1. 进入Django shell
cd /root/Projects/bk-sops
source ~/.envs/bk-sops/bin/activate
export $(cat .env | xargs)
python manage.py shell

# 2. 在shell中执行
from gcloud.taskflow3.models import TaskFlowInstance
qs = TaskFlowInstance.objects.filter(engine_ver=2)[:5]
print(str(qs.query))
```

就这么简单！🎉

---

**相关文件**:
- `show_sql.py` - 简单的SQL查看脚本
- `debug_sql_helper.py` - 高级调试工具
- `check_cleaner_sql.py` - 清理任务SQL检查工具






