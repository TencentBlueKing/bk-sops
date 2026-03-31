# SOPS 迁移工具文档

## 🎯 核心目标

确保周期任务和计划任务在迁移过程中保持**业务连续性**和**数据一致性**。

---

## ✅ 前置条件

### 文件准备
- 将文件拷贝到源环境和目标环境 `/app/gcloud/core/management/commands` 目录
- 在 `/app` 目录下执行脚本，可在任意 pod 中执行

### 🛠️ 环境准备

#### 网络配置
- 🌐 **网络连通性**：确保源环境与目标环境之间网络互通，支持数据库连接
- 🔑 **数据库权限**：目标环境需具备连接源环境数据库的权限

#### 服务状态管理（目标环境执行）
- ⏸️ **服务暂停**：执行迁移前关闭 celery beat 服务，防止后台任务产生新数据，可在开发者中心-部署管理-生产环境-default模块下关闭 beat 服务
- ▶️ **服务恢复**：全量迁移完成后并且已经全部关闭了流程周期任务和计划任务后可以重新启动 celery beat 服务

> **⚠️ 关键注意事项**
> 
> **数据一致性保障**：数据导入完成后，必须设置新环境表的自增偏移量，避免源环境增量数据与目标环境新数据产生ID冲突。

---

## 🔄 迁移流程

### 阶段一：数据库备份与恢复（耗时较长）

#### 1.1 配置数据库连接信息
首先编辑 `sync_config.py` 文件，配置源环境和目标环境的数据库连接信息：

```
# 源环境数据库 SOURCE_DB_CONFIG 配置
# 目标环境数据库 TARGET_DB_CONFIG 配置
```

#### 1.2 源环境数据库导出（源环境执行）
```bash
# 使用源环境配置导出数据库
python manage.py backup_restore --export

# 指定导出文件路径
python manage.py backup_restore --export --file /path/to/backup.sql
```

#### 1.3 目标环境数据库导入（目标环境执行）
```bash
# 使用目标环境配置导入数据库
python manage.py backup_restore --import --file <备份文件路径>
```

#### 1.4 设置偏移量（目标环境执行）
```bash
mysql -u root -p target_database_name < path/to/alter_auto_id.sql
```

**说明**：在目标环境执行 `alter_auto_id.sql` 脚本为模型设置偏移量

#### 1.5 模型迁移（目标环境执行）
```bash
python manage.py migrate account
python manage.py migrate core
python manage.py migrate external_plugins
python manage.py migrate template
```

**使用说明**：执行模型迁移，为模型补充 `tenant_id` 字段

#### 1.6 记录增量表的最大ID
```bash
python manage.py sync_model_max_ids
```

此脚本会统计部份表的最大ID到 EnvironmentVariables 表中，用于后续的增量数据同步

---

### 阶段二：停止目标环境任务（目标环境执行）

#### 2.1 关闭目标环境的周期任务和计划任务
```bash
python manage.py suspend_all_tasks
```

**执行时机**：迁移后立即执行  
**影响范围**：所有正在运行的周期任务和计划任务将被暂停

#### 2.2 检测任务是否全部关闭
```bash
# 检测所有业务的任务是否全部关闭
python manage.py check_task_status --check-type all_closed
```

**功能说明**：
- `--check-type all_closed`：检测周期任务和计划任务是否全部关闭
- `--check-type all_success`：检测周期任务和计划任务是否全部启动
- `--business-ids`：指定业务ID范围，多个用逗号分隔

---

### 阶段三：同步目标环境租户数据（目标环境执行）

#### 3.1 普通业务
```bash
# 使用配置文件中的租户ID同步数据
python manage.py sync_tenant_data
```
**功能说明**
此命令会修改所有业务的租户ID


#### 验证普通业务租户ID一致性
```bash
# 验证所有业务的租户ID字段一致性
python manage.py verify_tenant_sync
```

#### 3.2 特殊业务
```bash
python manage.py sync_tenant_data \
  --special_business_id <特殊业务ID> \
  --special_tenant_id <特殊租户ID>
```

#### 验证特殊业务租户ID一致性
```bash
# 验证包含特殊业务的租户ID字段一致性
python manage.py verify_tenant_sync \
  --special_business_id <特殊业务ID> \
  --special_tenant_id <特殊租户ID>
```

**功能说明**：
- 脚本只会修改特殊业务，特殊业务支持多个，用逗号分隔

**注意**：
- 此脚本必须在执行完租户字段迁移后执行
- 租户ID从配置文件 `sync_config.py` 中的 `TENANT_CONFIG` 读取

---

### 阶段四：刷新轻应用地址（目标环境执行）
```bash
python manage.py update_appmaker_link_domain --new-domain example.com
```

**比脚本会**：
1. 修改轻应用注册地址的域名
2. 重新拉取轻应用logo的地址

**参数说明**：
- `--new-domain`：目标环境的新域名

---

### 阶段五：任务迁移

#### 5.1 导出旧环境任务（源环境执行）
```bash
python manage.py task_backup_restore --export --business-ids 1,2,3 --file <目标路径>
```

**此脚本会**：
1. 关闭开启指定业务下的周期任务和未执行的计划任务
2. 将关闭的任务导出到文件中
3. 导出模式必须要指定具体的业务ID，不支持全业务操作

**参数说明**：
- `--business-ids`：操作的具体业务ID
- `--file`：要导出的文件路径，会在改路径下生成文件

**检测源环境指定业务下任务是否全部关闭**：
```bash
python manage.py check_task_status --check-type all_closed --business-ids 1,2,3
```

#### 5.2 导入新环境任务（目标环境执行）
```bash
python manage.py task_backup_restore --import --file <文件路径>
```

**此脚本需要**：
1. 需要先将在源环境导出的文件拷贝到目标环境
2. 在目标环境将文件导入开启任务

**参数说明**：
- `--file`：要读取的文件所在路径

**检测目标环境中指定业务下任务启动状态**：
```bash
python manage.py check_task_status --check-type all_success --business-ids 1,2,3
```

---

### 阶段六：增量数据同步（目标环境执行）

#### 6.1 增量同步配置准备

在执行增量同步前，需要确保已正确配置数据库连接信息，并已记录基础数据同步的最大ID。

**前置条件检查**：
- ✅ 已完成阶段一的全量数据迁移
- ✅ 已执行 `sync_model_max_ids` 记录各表最大ID
- ✅ 数据库连接配置正确

#### 6.2 执行增量数据同步

```bash
# 基本增量同步（默认批量大小100）
python manage.py sync_incremental_data

# 指定批量大小
python manage.py sync_incremental_data --batch-size 200
```

**注意**：
- 该命令同步的周期任务和计划任务会修改为关闭状态

**参数说明**：
- `--batch-size`：每次同步的记录数，默认100，可根据网络和数据库性能调整

#### 6.3 增量同步工作原理

**同步流程**：
1**按分类同步**：按模型分类依次同步
2**增量查询**：基于记录的max_id查询新增数据
3**批量处理**：按指定批量大小分批同步数据
4**状态更新**：每个分类完成后立即更新增量表记录的的ID
