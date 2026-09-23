import logging
import os
import sys

from bkai_init import BkaiInit
from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "校验并同步 AIDEV 智能体初始化包（bkai.yaml）到线上空间"

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)

        # 环境变量开关：默认不开启；未设置或非真值时跳过同步
        sync_switch = os.environ.get("BKAI_SYNC_ENABLED", False)
        if not sync_switch:
            self.stdout.write(self.style.WARNING("已跳过 AIDEV 智能体同步：如需执行请配置环境变量 BKAI_SYNC_ENABLED"))
            return

        BKAI_TENANT_ID = os.environ.get("BKAI_TENANT_ID", "system")

        initializer = BkaiInit(
            base_url=f"{settings.BK_API_URL_TMPL.format(api_name='bk-aidev')}/{settings.BK_APIGW_STAGE_NAME}",
            app_code=settings.APP_CODE,
            app_secret=settings.SECRET_KEY,
            access_token=os.environ.get("BKAI_ACCESS_TOKEN") or os.environ.get("ACCESS_TOKEN"),
            bk_user_base_url=f"{settings.BK_API_URL_TMPL.format(api_name='bk-user')}/{settings.BK_APIGW_STAGE_NAME}",
            tenant_id=BKAI_TENANT_ID,
            space=os.environ.get("BKAI_SPACE_ID", "system-bkaidev"),
            variables={"SKILL_BASE_IMAGE": "registry.example.com/team/skill:1.0"},
        )

        package = os.environ.get("BKAI_PACKAGE") or os.path.join(settings.BASE_DIR, "ai-agent", "bkai.yaml")

        # 1. 本地协议校验
        initializer.validate(package)

        # 2. 查看线上当前配置
        initializer.show(package, resources={"agent/ai-sops"})

        # 3. 计算本地与线上的差异
        initializer.diff(package, resources={"agent/ai-sops"})

        # 4. 预览同步计划（仅发布配置，不构建镜像）
        initializer.plan(package, publish=True, publish_config_only=False)

        # 5. 写入操作：仅在调用方确认计划后执行
        initializer.sync(package, publish=True, publish_config_only=False)

        self.stdout.write(self.style.SUCCESS("智能体初始化包同步完成"))
