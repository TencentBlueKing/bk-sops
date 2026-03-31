import logging

from blueapps.account.models import User
from django.core.management.base import BaseCommand

from gcloud.common_template.models import CommonTemplate
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
    help = "检测租户ID字段一致性"

    def add_arguments(self, parser):
        """添加命令行参数"""
        parser.add_argument("--special_business_id", type=str, help="特殊业务ID")
        parser.add_argument("--special_tenant_id", type=str, help="特殊租户ID")

    def handle(self, *args, **options):
        target_tenant_id = sync_config.TENANT_CONFIG["tenant_id"]
        special_business_id = options.get("special_business_id")
        special_tenant_id = options.get("special_tenant_id")

        self.stdout.write("=== 开始检测租户ID字段一致性 ===")
        self.stdout.write(f"目标租户ID: {target_tenant_id}")

        if special_business_id and special_tenant_id:
            special_business_id = special_business_id.split(",")
            self.stdout.write(f"特殊业务ID: {special_business_id}, 特殊租户ID: {special_tenant_id}")

        # 检测业务模型
        models_to_check = [
            User,
            Business,
            Project,
            CommonTemplate,
            SyncTask,
            GitRepoOriginalSource,
            S3OriginalSource,
            FileSystemOriginalSource,
            CachePackageSource,
        ]

        all_correct = True

        for model in models_to_check:
            try:
                self.stdout.write(f"检测模型: {model.__name__}")

                # 如果没有特殊业务，检查全部业务
                if not special_business_id or not special_tenant_id:
                    incorrect_records = model.objects.exclude(tenant_id=target_tenant_id)
                    incorrect_count = incorrect_records.count()

                    if incorrect_count == 0:
                        self.stdout.write(self.style.SUCCESS("所有记录租户ID一致"))
                    else:
                        self.stdout.write(self.style.ERROR(f"发现 {incorrect_count} 条记录租户ID不一致"))
                        all_correct = False

                # 如果有特殊业务，只检查特殊业务
                else:
                    if model.__name__ == "Business":
                        special_records = model.objects.filter(cc_id__in=special_business_id)
                        special_incorrect = special_records.exclude(tenant_id=special_tenant_id).count()
                    elif model.__name__ == "Project":
                        special_records = model.objects.filter(bk_biz_id__in=special_business_id)
                        special_incorrect = special_records.exclude(tenant_id=special_tenant_id).count()
                    else:
                        special_incorrect = 0

                    if special_incorrect == 0:
                        self.stdout.write(self.style.SUCCESS("特殊业务记录租户ID一致"))
                    else:
                        self.stdout.write(self.style.ERROR(f"特殊业务有 {special_incorrect} 条记录租户ID不一致"))
                        all_correct = False

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"检测模型{model.__name__}失败: {e}"))
                logger.error(f"检测模型{model.__name__}失败: {e}")
                all_correct = False

        # 输出最终结果
        self.stdout.write("\n=== 检测结果 ===")
        if all_correct:
            self.stdout.write(self.style.SUCCESS("所有租户ID字段检测通过"))
        else:
            self.stdout.write(self.style.ERROR("存在租户ID字段不一致的记录"))

        self.stdout.write("租户ID一致性检测完成")
