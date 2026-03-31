import os
import subprocess
from datetime import datetime

import pymysql
from django.core.management.base import BaseCommand

# 导入数据库配置文件
try:
    from . import sync_config
except ImportError:
    # 如果sync_config不存在，使用默认配置
    sync_config = None


class Command(BaseCommand):
    help = "数据库导出导入工具：通过配置文件管理数据库连接信息"

    def add_arguments(self, parser):
        parser.add_argument("--export", action="store_true", help="执行导出操作（使用源环境配置）")
        parser.add_argument("--import", action="store_true", help="执行导入操作（使用目标环境配置）")
        parser.add_argument("--file", type=str, help="导出或导入的文件路径")
        parser.add_argument("--dry-run", action="store_true", help="只显示将要执行的操作，不实际执行")

    def handle(self, *args, **options):
        # 检查配置文件是否存在
        if sync_config is None:
            self.stdout.write(self.style.ERROR("数据库配置文件 sync_config.py 不存在，请先创建配置文件"))
            return

        # 验证必需参数
        if options["export"]:
            if not sync_config.SOURCE_DB_CONFIG.get("database"):
                self.stdout.write(self.style.ERROR("源环境数据库配置中未指定数据库名称"))
                return

        # 设置默认文件路径（仅在未指定文件时）
        if options["export"] or options["import"]:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if options["export"] and not options.get("file"):
                db_name = sync_config.SOURCE_DB_CONFIG["database"]
                options["file"] = f"{db_name}_backup_{timestamp}.sql"
            elif options["import"] and not options.get("file"):
                # 导入操作时，文件路径是必需的
                self.stdout.write(self.style.ERROR("导入操作必须指定文件路径（--file参数）"))
                return

        # 验证数据库连接并执行操作
        if options["export"]:
            # 导出操作始终使用源环境配置
            if not self.validate_connection(sync_config.SOURCE_DB_CONFIG):
                return
            self.export_database(sync_config.SOURCE_DB_CONFIG, options)

        if options["import"]:
            # 导入操作始终使用目标环境配置
            if not self.validate_connection(sync_config.TARGET_DB_CONFIG):
                return
            self.import_database(sync_config.TARGET_DB_CONFIG, options)

    def export_database(self, sync_config, options):
        """执行数据库导出操作"""
        if options["dry_run"]:
            self.stdout.write("[运行] 将执行导出操作")
            return

        self.stdout.write(f"导出数据库: {sync_config['database']}")
        port = int(sync_config["port"]) if sync_config["port"] else 3306
        # 构建mysqldump命令
        cmd = [
            "mysqldump",
            f"-h{sync_config['host']}",
            f"-P{port}",
            f"-u{sync_config['user']}",
        ]

        if sync_config["password"]:
            cmd.append(f"-p{sync_config['password']}")

        cmd.append(sync_config["database"])

        # 添加其他选项
        cmd.extend(
            [
                "--single-transaction",
                "--quick",
                "--lock-tables=false",
                "--set-gtid-purged=OFF",
                "--skip-add-locks",
                "--skip-comments",
                "--skip-disable-keys",
                "--skip-set-charset",
            ]
        )

        try:
            with open(options["file"], "w", encoding="utf-8") as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, universal_newlines=True)

            if result.returncode == 0:
                file_size = os.path.getsize(options["file"])
                self.stdout.write(self.style.SUCCESS(f"导出成功！文件: {options['file']} ({file_size} bytes)"))
            else:
                self.stdout.write(self.style.ERROR(f"导出失败: {result.stderr}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"导出过程中发生错误: {str(e)}"))

    def import_database(self, sync_config, options):
        """执行数据库导入操作"""
        if not os.path.exists(options["file"]):
            self.stdout.write(self.style.ERROR(f"导入文件不存在: {options['file']}"))
            return

        self.stdout.write(f"导入数据库: {sync_config['database']}")
        if options["dry_run"]:
            self.stdout.write("[运行] 将执行导入操作")
            return

        port = int(sync_config["port"]) if sync_config["port"] else 3306
        # 构建mysql命令
        cmd = [
            "mysql",
            f"-h{sync_config['host']}",
            f"-P{port}",
            f"-u{sync_config['user']}",
        ]

        if sync_config["password"]:
            cmd.append(f"-p{sync_config['password']}")

        cmd.append(sync_config["database"])
        cmd.extend(
            [
                "--default-character-set=utf8",
            ]
        )

        try:
            with open(options["file"], "r", encoding="utf-8") as f:
                result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, universal_newlines=True)

            if result.returncode == 0:
                self.stdout.write(self.style.SUCCESS("导入成功！"))
            else:
                self.stdout.write(self.style.ERROR(f"导入失败: {result.stderr}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"导入过程中发生错误: {str(e)}"))

    def validate_connection(self, sync_config):
        """验证数据库连接"""
        try:
            port = int(sync_config["port"]) if sync_config["port"] else 3306
            conn = pymysql.connect(
                host=sync_config["host"],
                port=port,
                user=sync_config["user"],
                password=sync_config["password"],
                database=sync_config["database"],
                charset="utf8mb4",
            )
            conn.close()
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"数据库连接失败: {str(e)}"))
            return False
