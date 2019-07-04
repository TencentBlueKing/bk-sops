# -*- coding: utf-8 -*-
"""testapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from home_application import views

urlpatterns = (
    url(r'^$', views.home),
    url(r'helloworld$', views.helloworld, name='helloworld'),
    url(r'index$', views.index, name='index'),
    url(r'forms$', views.forms, name='forms'),
    url(r'tables$', views.tables, name='tables'),
    url(r'get_capacity$', views.get_capacity, name='get_capacity'),
    url(r'disk_use$', views.disk_use, name='disk_use'),
    url(r'get_disk_usage/$', views.api_disk_usage, name='api_disk_usage'),
    url(r'get_usage_data$', views.get_usage_data, name='get_usage_data'),
    url(r'usage_data_view$', views.usage_data_view, name='usage_data_view'),
)
