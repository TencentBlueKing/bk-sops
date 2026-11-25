# -*- coding: utf-8 -*-
"""
检查 S3 包源配置是否符合 SSRF 防护规范

使用方法:
    python manage.py check_s3_sources          # 仅检查
    python manage.py check_s3_sources --fix    # 检查并禁用不合规配置
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from gcloud.external_plugins.models import S3OriginalSource
from gcloud.external_plugins.protocol.readers import validate_s3_service_address
from gcloud.external_plugins.exceptions import ForbiddenExternalPluginSourceError


class Command(BaseCommand):
    help = '检查 S3 包源配置是否符合 SSRF 防护规范'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='禁用不合规的 S3 包源（添加标记，不删除数据）',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(self.style.WARNING('S3 包源 SSRF 防护规范检查'))
        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write('')

        # 获取所有 S3 包源
        sources = S3OriginalSource.objects.all()

        if not sources.exists():
            self.stdout.write(self.style.SUCCESS('✓ 数据库中没有 S3 包源配置'))
            return

        self.stdout.write(f'共找到 {sources.count()} 个 S3 包源配置\n')

        invalid_sources = []
        valid_sources = []

        # 逐个检查
        for source in sources:
            try:
                validate_s3_service_address(source.service_address)
                valid_sources.append(source)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ [{source.id}] {source.name}: {source.service_address}'
                    )
                )
            except ForbiddenExternalPluginSourceError as e:
                invalid_sources.append((source, str(e)))
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ [{source.id}] {source.name}: {source.service_address}'
                    )
                )
                self.stdout.write(
                    self.style.ERROR(f'  原因: {e}')
                )

        # 输出统计
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('-' * 60))
        self.stdout.write(f'检查结果统计:')
        self.stdout.write(f'  合规: {len(valid_sources)} 个')
        self.stdout.write(f'  不合规: {len(invalid_sources)} 个')
        self.stdout.write(self.style.WARNING('-' * 60))
        self.stdout.write('')

        # 如果有不合规配置
        if invalid_sources:
            self.stdout.write(self.style.ERROR('发现不合规配置！'))
            self.stdout.write('')

            if options['fix']:
                self.stdout.write(self.style.WARNING('开始处理不合规配置...'))
                self._fix_invalid_sources(invalid_sources)
            else:
                self.stdout.write(self.style.WARNING('建议处理方案:'))
                self.stdout.write('1. 联系相关用户，修改为合规的域名配置')
                self.stdout.write('2. 或运行 python manage.py check_s3_sources --fix 禁用不合规配置')
                self.stdout.write('')
                self.stdout.write(self.style.ERROR('⚠️  不合规配置将无法使用！'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ 所有配置均符合规范'))

    def _fix_invalid_sources(self, invalid_sources):
        """处理不合规的包源（标记为不可用，但不删除）"""
        self.stdout.write('')

        for source, reason in invalid_sources:
            # 这里可以添加一个 is_active 字段标记
            # 或者在包源名称前添加 [已禁用] 标记
            original_name = source.name
            if not source.name.startswith('[已禁用-SSRF不合规]'):
                source.name = f'[已禁用-SSRF不合规] {source.name}'
                source.save(update_fields=['name'])

                self.stdout.write(
                    self.style.WARNING(
                        f'✓ 已标记包源为禁用: [{source.id}] {original_name}'
                    )
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'已处理 {len(invalid_sources)} 个不合规配置'))
        self.stdout.write(self.style.WARNING('注意: 数据未删除，仅添加禁用标记'))
