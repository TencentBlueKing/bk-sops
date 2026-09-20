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

        # 必填环境变量：开启开关后缺失则给出清晰报错，而非裸 KeyError。
        base_url = os.environ.get("BKAI_BASE_URL")
        space_id = os.environ.get("BKAI_SPACE_ID")
        missing = [name for name, value in (("BKAI_BASE_URL", base_url), ("BKAI_SPACE_ID", space_id)) if not value]
        if missing:
            raise RuntimeError("sync_agent 已开启但缺少必填环境变量：%s。请补充配置后再执行。" % ", ".join(missing))

        initializer = BkaiInit(
            base_url=base_url,
            app_code=settings.APP_CODE,
            app_secret=settings.SECRET_KEY,
            access_token=os.environ.get("BKAI_ACCESS_TOKEN") or os.environ.get("ACCESS_TOKEN"),
            tenant_id="system",
            space=space_id,
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
        initializer.plan(package, publish=True, publish_config_only=True)

        # 5. 写入操作：仅在调用方确认计划后执行
        initializer.sync(package, publish=True, publish_config_only=True)

        self.stdout.write(self.style.SUCCESS("智能体初始化包同步完成"))
