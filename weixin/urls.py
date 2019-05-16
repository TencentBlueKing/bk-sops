# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from tastypie.api import Api
from resources import (
    WxBusinessResource,
    WxTaskTemplateResource,
    WxTaskFlowInstanceResource,
    WxTemplateSchemeResource
)

weixin_v3_api = Api(api_name='v3')
weixin_v3_api.register(WxBusinessResource())
weixin_v3_api.register(WxTaskTemplateResource())
weixin_v3_api.register(WxTemplateSchemeResource())
weixin_v3_api.register(WxTaskFlowInstanceResource())

urlpatterns = [
    url(r'^api/', include(weixin_v3_api.urls)),
    url(r'^taskflow/', include('gcloud.taskflow3.urls')),
    url(r'^template/', include('gcloud.tasktmpl3.urls'))
]