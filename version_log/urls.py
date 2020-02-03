# -*- coding: utf-8 -*-
from django.conf.urls import url

from version_log import views

urlpatterns = (
    # 版本日志单页面
    url(r'^$', views.version_logs_page, name='version_log_page'),
    # 获取版本日志块页面（用于对话框场景）
    url(r'^block/$', views.version_logs_block),
    # 获取版本日志列表
    url(r'^version_logs_list/$', views.version_logs_list),
    # 获取版本日志详情
    url(r'^version_log_detail/', views.get_version_log_detail),
)
