from urllib.parse import urlparse

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from gcloud.contrib.appmaker.models import AppMaker
from gcloud.core.api_adapter import get_app_logo_url

from . import sync_config


class Command(BaseCommand):
    help = _("自动识别并替换轻应用link字段域名")

    def add_arguments(self, parser):
        parser.add_argument("--new-domain", type=str, required=True, help=_("替换后的新域名（例如：new-example.com）"))

    def handle(self, *args, **options):
        new_domain = options["new_domain"]

        self.stdout.write("开始域名替换...")
        self.stdout.write(f"新域名: {new_domain}")
        tenant_id = sync_config.TENANT_CONFIG["tenant_id"]

        # 获取所有未删除的轻应用
        appmakers = AppMaker.objects.all()
        total_count = appmakers.count()

        if total_count == 0:
            self.stdout.write(self.style.WARNING("未找到轻应用"))
            return

        with transaction.atomic():
            for appmaker in appmakers:
                original_link = appmaker.link

                # 从链接中提取当前域名
                parsed = urlparse(original_link)
                current_domain = parsed.netloc

                if not current_domain:
                    self.stdout.write(f"ID={appmaker.id}, 名称='{appmaker.name}' - 解析域名失败")
                    self.stdout.write(f"当前链接: {original_link}")
                    raise

                # 如果已经是新域名，跳过
                if current_domain == new_domain:
                    continue

                # 替换域名
                new_link = parsed._replace(netloc=new_domain).geturl()

                try:
                    appmaker.link = new_link
                    appmaker.logo_url = get_app_logo_url(app_code=appmaker.code, tenant_id=tenant_id)
                    appmaker.save()
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"更新失败: {str(e)}"))
                    raise

        self.stdout.write(self.style.SUCCESS("操作已完成"))
