import os
import subprocess
from datetime import datetime

import pymysql
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "数据库导出导入工具：支持通过参数连接数据库并执行导出导入操作"

    def add_arguments(self, parser):
        parser.add_argument("--host", type=str, help="数据库主机地址")
        parser.add_argument("--port", type=int, help="数据库端口")
        parser.add_argument("--user", type=str, help="数据库用户名")
        parser.add_argument("--password", type=str, help="数据库密码")
        parser.add_argument("--database", type=str, help="数据库名称，导出操作时必需")
        parser.add_argument("--export", action="store_true", help="执行导出操作")
        parser.add_argument("--import", action="store_true", help="执行导入操作")
        parser.add_argument("--file", type=str, help="导出或导入的文件路径")
        parser.add_argument("--dry-run", action="store_true", help="只显示将要执行的操作，不实际执行")

    def handle(self, *args, **options):
        # 验证必需参数
        if options["export"] and not options["database"]:
            self.stdout.write(self.style.ERROR("导出操作必须指定数据库名称（--database参数），因为mysqldump需要知道要导出哪个具体的数据库"))
            return

        # 设置默认文件路径（仅在未指定文件时）
        if options["export"] or options["import"]:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if options["export"] and not options.get("file"):
                options["file"] = f"{options['database']}_backup_{timestamp}.sql"
            elif options["import"] and not options.get("file"):
                # 导入操作时，文件路径是必需的
                self.stdout.write(self.style.ERROR("导入操作必须指定文件路径（--file参数）"))
                return

        # 验证数据库连接
        if options["export"]:
            if not self.validate_connection(options):
                return
            self.export_database(options)

        if options["import"]:
            local_db_settings = settings.DATABASES["default"]
            local_options = {
                "host": local_db_settings["HOST"],
                "port": int(local_db_settings["PORT"]) if local_db_settings["PORT"] else 3306,
                "user": local_db_settings["USER"],
                "password": local_db_settings["PASSWORD"],
                "database": local_db_settings["NAME"],
                "file": options.get("file", ""),
                "dry_run": options.get("dry_run", False),
            }
            if not self.validate_connection(local_options):
                return
            self.import_database(local_options)

    def export_database(self, options):
        """执行数据库导出操作"""
        self.stdout.write(f"开始导出数据库: {options['database']}")

        if options["dry_run"]:
            self.stdout.write("[运行] 将执行导出操作")
            return

        port = int(options["port"]) if options["port"] else 3306
        # 构建mysqldump命令
        cmd = [
            "mysqldump",
            f"-h{options['host']}",
            f"-P{port}",
            f"-u{options['user']}",
        ]

        if options["password"]:
            cmd.append(f"-p{options['password']}")

        cmd.append(options["database"])

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

    def import_database(self, options):
        """执行数据库导入操作"""
        self.stdout.write(f"开始导入数据库: {options['database']}")

        if not os.path.exists(options["file"]):
            self.stdout.write(self.style.ERROR(f"导入文件不存在: {options['file']}"))
            return

        if options["dry_run"]:
            self.stdout.write("[运行] 将执行导入操作")
            return

        port = int(options["port"]) if options["port"] else 3306
        # 构建mysql命令
        cmd = [
            "mysql",
            f"-h{options['host']}",
            f"-P{port}",
            f"-u{options['user']}",
        ]

        if options["password"]:
            cmd.append(f"-p{options['password']}")

        cmd.append(options["database"])
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

    def validate_connection(self, options):
        """验证数据库连接"""
        try:
            port = int(options["port"]) if options["port"] else 3306
            conn = pymysql.connect(
                host=options["host"],
                port=port,
                user=options["user"],
                password=options["password"],
                database=options["database"],
                charset="utf8mb4",
            )
            conn.close()
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"数据库连接失败: {str(e)}"))
            return False
