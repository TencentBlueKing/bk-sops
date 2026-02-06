import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from gcloud.core.models import Business, Project
from gcloud.external_plugins.models import (
    CachePackageSource,
    FileSystemOriginalSource,
    GitRepoOriginalSource,
    S3OriginalSource,
    SyncTask,
)

from . import sync_config

logger = logging.getLogger("root")


class Command(BaseCommand):
    help = "批量更新表中租户字段"

    def add_arguments(self, parser):
        """添加命令行参数"""
        parser.add_argument("--dry_run", action="store_true", help="模拟运行模式，不实际执行更新")
        parser.add_argument("--special_business_id", type=str, help="特殊业务ID")
        parser.add_argument("--special_tenant_id", type=str, help="特殊租户ID")

    def handle(self, *args, **options):
        tenant_id = sync_config.TENANT_CONFIG["tenant_id"]
        special_business_id = options.get("special_business_id")
        special_tenant_id = options.get("special_tenant_id")
        dry_run = options.get("dry_run", False)

        self.stdout.write(f"开始执行租户ID更新操作，目标租户ID: {tenant_id}")

        if dry_run:
            self.stdout.write("=== 模拟运行模式 ===")

        # 定义需要更新的模型列表
        models_to_update = [
            Business,
            Project,
            SyncTask,
            GitRepoOriginalSource,
            S3OriginalSource,
            FileSystemOriginalSource,
            CachePackageSource,
        ]

        # 模拟运行模式
        if dry_run:
            self.stdout.write(f"模拟运行模式，将更新 {len(models_to_update)} 个模型")
            return

        # 循环处理每个模型
        with transaction.atomic():
            for model in models_to_update:
                try:
                    model.objects.all().update(tenant_id=tenant_id)
                    if model.__name__ == "Business" and special_business_id and special_tenant_id:
                        model.objects.filter(cc_id=special_business_id).update(tenant_id=special_tenant_id)
                    if model.__name__ == "Project" and special_business_id and special_tenant_id:
                        model.objects.filter(bk_biz_id=special_business_id).update(tenant_id=special_tenant_id)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"更新模型{model.__name__}租户信息失败: {e}"))
                    logger.error(f"更新模型{model.__name__}租户信息失败: {e}")

        self.stdout.write("更新租户信息完成")
