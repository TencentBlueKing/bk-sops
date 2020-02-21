# -*- coding: utf-8 -*-
from django.conf.urls import url

from blueapps.account import views

app_name = 'account'

urlpatterns = [
    url(r'^login_success/$', views.login_success, name="login_success"),
    url(r'^login_page/$', views.login_page, name="login_page"),
    url(r'^send_code/$', views.send_code_view, name="send_code"),
    url(r'^get_user_info/$', views.get_user_info, name="get_user_info")
]
