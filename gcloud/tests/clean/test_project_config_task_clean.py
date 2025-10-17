# -*- coding: utf-8 -*-
"""
ProjectConfig 任务清理配置功能测试示例

这个文件提供了一些测试用例示例，说明如何测试项目级任务清理配置功能。
注意：这只是一个示例文件，实际测试需要根据项目的测试框架进行适配。
"""
from django.test import TestCase

from gcloud.core.models import ProjectConfig


class TestProjectConfigTaskClean(TestCase):
    """
    测试 ProjectConfig 的任务清理配置功能
    """

    def setUp(self):
        """测试前准备"""
        self.project_id_1 = 100
        self.project_id_2 = 200
        self.project_id_3 = 300

    def test_project_with_custom_create_methods(self):
        """
        测试：项目配置了自定义的 create_methods
        预期：清理任务时，只清理配置中指定的 create_method
        """
        # 创建项目配置
        ProjectConfig.objects.create(
            project_id=self.project_id_1, task_clean_configs={"create_methods": ["api", "app"]}
        )

        # 验证配置
        config = ProjectConfig.objects.get(project_id=self.project_id_1)
        self.assertEqual(config.task_clean_configs["create_methods"], ["api", "app"])
        print(f"✓ 项目 {self.project_id_1} 配置了自定义 create_methods: {config.task_clean_configs['create_methods']}")

    def test_project_without_custom_config(self):
        """
        测试：项目没有配置 task_clean_configs
        预期：使用全局配置 settings.CLEAN_EXPIRED_V2_TASK_CREATE_METHODS
        """
        # 创建没有 task_clean_configs 的项目配置
        ProjectConfig.objects.create(project_id=self.project_id_2, task_clean_configs={})

        config = ProjectConfig.objects.get(project_id=self.project_id_2)
        self.assertEqual(config.task_clean_configs, {})
        print(f"✓ 项目 {self.project_id_2} 没有自定义配置，将使用全局配置")

    def test_get_projects_with_clean_configs(self):
        """
        测试：获取所有配置了 task_clean_configs 的项目
        """
        # 创建多个项目配置
        ProjectConfig.objects.create(project_id=self.project_id_1, task_clean_configs={"create_methods": ["api"]})
        ProjectConfig.objects.create(project_id=self.project_id_2, task_clean_configs={"create_methods": ["app"]})
        ProjectConfig.objects.create(project_id=self.project_id_3, task_clean_configs={})

        # 查询有配置的项目
        project_clean_configs = {}
        for config in ProjectConfig.objects.filter(task_clean_configs__isnull=False).values(
            "project_id", "task_clean_configs"
        ):
            if config["task_clean_configs"] and isinstance(config["task_clean_configs"], dict):
                create_methods = config["task_clean_configs"].get("create_methods", [])
                if create_methods:
                    project_clean_configs[config["project_id"]] = config["task_clean_configs"]

        self.assertIn(self.project_id_1, project_clean_configs)
        self.assertIn(self.project_id_2, project_clean_configs)
        self.assertNotIn(self.project_id_3, project_clean_configs)

        print(f"✓ 找到 {len(project_clean_configs)} 个配置了 task_clean_configs 的项目")
        for pid, config in project_clean_configs.items():
            print(f"  - 项目 {pid}: create_methods={config['create_methods']}")

    def test_config_validation(self):
        """
        测试：验证配置的有效性
        """
        # 测试有效的配置
        valid_configs = [
            {"create_methods": ["api"]},
            {"create_methods": ["api", "app"]},
            {"create_methods": ["api", "app", "app_maker"]},
        ]

        for config in valid_configs:
            create_methods = config.get("create_methods", [])
            self.assertIsInstance(create_methods, list)
            self.assertTrue(all(isinstance(m, str) for m in create_methods))
            print(f"✓ 配置有效: {config}")

        # 测试空配置
        empty_configs = [
            {},
            {"create_methods": []},
            None,
        ]

        for config in empty_configs:
            if config:
                create_methods = config.get("create_methods", [])
                self.assertIsInstance(create_methods, list)
            print(f"✓ 空配置处理正确: {config}")


def demonstrate_usage():
    """
    演示如何使用 ProjectConfig 的任务清理配置
    """
    print("\n" + "=" * 60)
    print("ProjectConfig 任务清理配置使用演示")
    print("=" * 60 + "\n")

    # 示例 1: 创建项目配置
    print("示例 1: 为项目 100 配置只清理 API 和 APP 创建的任务")
    print("-" * 60)
    config1, created = ProjectConfig.objects.update_or_create(
        project_id=100, defaults={"task_clean_configs": {"create_methods": ["api", "app"]}}
    )
    print(f"项目 100 配置{'创建' if created else '更新'}成功")
    print(f"配置内容: {config1.task_clean_configs}\n")

    # 示例 2: 更新项目配置
    print("示例 2: 更新项目 200 的配置")
    print("-" * 60)
    config2, created = ProjectConfig.objects.get_or_create(project_id=200, defaults={"task_clean_configs": {}})
    config2.task_clean_configs = {"create_methods": ["api"]}
    config2.save()
    print("项目 200 配置更新成功")
    print(f"配置内容: {config2.task_clean_configs}\n")

    # 示例 3: 查询所有配置
    print("示例 3: 查询所有有特殊清理配置的项目")
    print("-" * 60)
    configs = ProjectConfig.objects.filter(task_clean_configs__isnull=False).exclude(task_clean_configs={})
    print(f"找到 {configs.count()} 个配置:")
    for config in configs:
        create_methods = config.task_clean_configs.get("create_methods", [])
        if create_methods:
            print(f"  - 项目 {config.project_id}: create_methods={create_methods}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    """
    运行演示脚本

    使用方法:
    python test_project_config_task_clean.py

    或在 Django shell 中:
    from test_project_config_task_clean import demonstrate_usage
    demonstrate_usage()
    """
    print("这是一个测试示例文件")
    print("请在 Django 环境中运行测试用例或演示函数")
    print("\n运行测试:")
    print("  python manage.py test test_project_config_task_clean")
    print("\n运行演示:")
    print("  python manage.py shell")
    print("  >>> from test_project_config_task_clean import demonstrate_usage")
    print("  >>> demonstrate_usage()")
