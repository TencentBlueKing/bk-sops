"""
管理员工具函数单元测试
"""
from django.test import TestCase, override_settings

from gcloud.utils.admin import get_admin_username, is_admin_username


class TestAdminUtils(TestCase):
    """测试管理员工具函数"""

    def test_get_admin_username_default(self):
        """测试默认值"""
        with override_settings():
            from django.conf import settings

            if hasattr(settings, "BK_ADMIN_USERNAME"):
                delattr(settings, "BK_ADMIN_USERNAME")
            self.assertEqual(get_admin_username(), "admin")

    @override_settings(BK_ADMIN_USERNAME="bk_admin_test123")
    def test_get_admin_username_configured(self):
        """测试配置值"""
        self.assertEqual(get_admin_username(), "bk_admin_test123")

    @override_settings(BK_ADMIN_USERNAME="bk_admin_xyz")
    def test_is_admin_username_current(self):
        """测试当前配置的管理员"""
        self.assertTrue(is_admin_username("bk_admin_xyz"))
        self.assertFalse(is_admin_username("other_user"))

    def test_is_admin_username_legacy(self):
        """测试历史遗留值"""
        self.assertTrue(is_admin_username("admin"))
        self.assertTrue(is_admin_username("bk_admin"))

    def test_is_admin_username_empty(self):
        """测试空值"""
        self.assertFalse(is_admin_username(""))
        self.assertFalse(is_admin_username(None))
