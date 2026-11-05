# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.contrib import admin
from django.test import TestCase, override_settings
from django.urls import reverse, NoReverseMatch
from pipeline.contrib.external_plugins.models import S3Source, GitRepoSource, FileSystemSource


class TestExternalPluginsDisabled(TestCase):
    """
    启动回归测试：验证远程插件加载功能已彻底下架

    背景：
    - 远程插件加载功能存在 SSRF 漏洞和远程代码执行风险
    - commit afdfc27b 初步下架，但 Code Review 发现 P1+P2 遗留问题
    - 本测试验证修复后的效果

    验证范围：
    1. 三个包源模型（S3Source、GitRepoSource、FileSystemSource）未注册到 Admin
    2. Admin 列表页 URL 不可访问（404）
    3. Admin 新增页 URL 不可访问（404）
    4. Admin 编辑页 URL 不可访问（404）
    """

    def test_s3source_not_registered_in_admin(self):
        """
        验证：S3Source 未注册到 Django Admin

        如果失败：说明 Admin 注销逻辑未生效
        排查：检查 gcloud.external_plugins.apps.py 中的 _unregister_pipeline_admin() 是否执行
        """
        self.assertNotIn(
            S3Source,
            admin.site._registry,
            "S3Source 仍在 Admin 中注册。"
            "检查点：gcloud/external_plugins/apps.py 的 _unregister_pipeline_admin() 方法"
        )

    def test_gitreposource_not_registered_in_admin(self):
        """
        验证：GitRepoSource 未注册到 Django Admin

        如果失败：说明 Admin 注销逻辑未生效
        排查：检查 gcloud.external_plugins.apps.py 中的 _unregister_pipeline_admin() 是否执行
        """
        self.assertNotIn(
            GitRepoSource,
            admin.site._registry,
            "GitRepoSource 仍在 Admin 中注册。"
            "检查点：gcloud/external_plugins/apps.py 的 _unregister_pipeline_admin() 方法"
        )

    def test_filesystemsource_not_registered_in_admin(self):
        """
        验证：FileSystemSource 未注册到 Django Admin

        如果失败：说明 Admin 注销逻辑未生效
        排查：检查 gcloud.external_plugins.apps.py 中的 _unregister_pipeline_admin() 是否执行
        """
        self.assertNotIn(
            FileSystemSource,
            admin.site._registry,
            "FileSystemSource 仍在 Admin 中注册。"
            "检查点：gcloud/external_plugins/apps.py 的 _unregister_pipeline_admin() 方法"
        )

    def test_s3source_admin_list_url_not_accessible(self):
        """
        验证：S3Source Admin 列表页 URL 不可访问

        URL: /django_admin/pipeline_external_plugins/s3source/
        预期：404 Not Found

        如果返回 200：说明 Admin 仍可访问，存在安全风险
        """
        try:
            url = reverse('admin:pipeline_external_plugins_s3source_changelist')
            # 如果 URL 能解析，尝试访问
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                404,
                f"S3Source Admin 列表页仍可访问（返回 {response.status_code}），应返回 404"
            )
        except NoReverseMatch:
            # URL 无法解析是预期行为（Admin 未注册）
            pass

    def test_gitreposource_admin_add_url_not_accessible(self):
        """
        验证：GitRepoSource Admin 新增页 URL 不可访问

        URL: /django_admin/pipeline_external_plugins/gitreposource/add/
        预期：404 Not Found

        如果返回 200：说明可以通过 Admin 创建恶意包源，存在安全风险
        """
        try:
            url = reverse('admin:pipeline_external_plugins_gitreposource_add')
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                404,
                f"GitRepoSource Admin 新增页仍可访问（返回 {response.status_code}），应返回 404"
            )
        except NoReverseMatch:
            # URL 无法解析是预期行为（Admin 未注册）
            pass

    def test_filesystemsource_admin_change_url_not_accessible(self):
        """
        验证：FileSystemSource Admin 编辑页 URL 不可访问

        URL: /django_admin/pipeline_external_plugins/filesystemsource/1/change/
        预期：404 Not Found

        如果返回 200：说明可以通过 Admin 修改包源配置，存在安全风险
        """
        try:
            url = reverse('admin:pipeline_external_plugins_filesystemsource_change', args=[1])
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                404,
                f"FileSystemSource Admin 编辑页仍可访问（返回 {response.status_code}），应返回 404"
            )
        except NoReverseMatch:
            # URL 无法解析是预期行为（Admin 未注册）
            pass

    def test_all_models_unregistered_together(self):
        """
        综合验证：三个模型全部未注册

        这是启动回归的核心检查点：
        - 确保没有遗漏任何一个模型
        - 验证注销逻辑批量生效
        """
        models_to_check = [
            ('S3Source', S3Source),
            ('GitRepoSource', GitRepoSource),
            ('FileSystemSource', FileSystemSource),
        ]

        registered_models = []
        for model_name, model_class in models_to_check:
            if model_class in admin.site._registry:
                registered_models.append(model_name)

        self.assertEqual(
            len(registered_models),
            0,
            f"以下模型仍在 Admin 中注册：{', '.join(registered_models)}。"
            f"远程插件加载功能未完全下架，存在安全风险。"
        )
