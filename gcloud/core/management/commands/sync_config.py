import os

# 数据库配置文件
# 用于存储源环境和目标环境的数据库连接信息

# 源环境数据库配置
SOURCE_DB_CONFIG = {
    "host": os.getenv("SOURCE_DB_HOST"),
    "port": os.getenv("SOURCE_DB_PORT", 3306),
    "user": os.getenv("SOURCE_DB_USER"),
    "password": os.getenv("SOURCE_DB_PASSWORD"),
    "database": os.getenv("SOURCE_DB_DATABASE"),
}

# 目标环境数据库配置
TARGET_DB_CONFIG = {
    "host": os.getenv("BKAPP_MYSQL_HOST"),
    "port": os.getenv("BKAPP_MYSQL_PORT", 3306),
    "user": os.getenv("BKAPP_MYSQL_USER"),
    "password": os.getenv("BKAPP_MYSQL_PASSWORD"),
    "database": os.getenv("BKAPP_MYSQL_NAME"),
}

# 租户ID配置
TENANT_CONFIG = {
    "tenant_id": "tencent",
}

# 配置说明：
# 1. 请根据实际环境修改上述配置信息
# 2. 源环境配置用于导出操作，目标环境配置用于导入操作
# 3. 租户ID配置用于同步租户数据操作
