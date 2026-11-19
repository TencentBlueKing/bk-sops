"""
管理员用户名获取工具函数
用于获取系统默认管理员用户名，支持随机化配置
"""

from django.conf import settings


def get_admin_username():
    """
    获取系统默认管理员用户名

    返回系统配置的管理员用户名，支持通过环境变量 bkAdminUsername
    进行配置（PaaS 平台约定的变量名），未配置时返回默认值 "admin"

    实现说明：
       从 settings.BK_ADMIN_USERNAME 读取，该值在 env.py 中从环境变量加载

    Returns:
       str: 管理员用户名

    """
    return getattr(settings, "BK_ADMIN_USERNAME", "admin")


def is_admin_username(username):
    """
    判断给定的用户名是否是系统管理员

    兼容当前配置的管理员和历史遗留值（admin, bk_admin）

    Args:
        username (str): 要检查的用户名

    Returns:
        bool: 如果是系统管理员返回 True，否则返回 False

    """
    if not username:
        return False

    current_admin = get_admin_username()

    # 1. 匹配当前配置的管理员
    if username == current_admin:
        return True

    # 2. 兼容历史遗留值
    legacy_admins = ["admin", "bk_admin"]
    if username in legacy_admins:
        return True

    return False
