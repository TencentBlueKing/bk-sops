# 数据库配置文件
# 用于存储源环境和目标环境的数据库连接信息

# 源环境数据库配置
SOURCE_DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "your_source_password",
    "database": "source_database_name",
}

# 目标环境数据库配置
TARGET_DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "your_target_password",
    "database": "target_database_name",
}

# 租户ID配置
TENANT_CONFIG = {
    "tenant_id": "tencent",
}

# 配置说明：
# 1. 请根据实际环境修改上述配置信息
# 2. 源环境配置用于导出操作，目标环境配置用于导入操作
# 3. 租户ID配置用于同步租户数据操作
