# -*- coding: utf-8 -*-

from django.http.response import HttpResponseForbidden
from gcloud.webservice3.resources import (
    BusinessResource,
    TaskTemplateResource,
    TemplateSchemeResource,
    TaskFlowInstanceResource
)


class WxBusinessResource(BusinessResource):
    def obj_delete(self, bundle, **kwargs):
        """
        obj delete is forbidden
        """
        return HttpResponseForbidden()


class WxTaskTemplateResource(TaskTemplateResource):
    pass


class WxTaskFlowInstanceResource(TaskFlowInstanceResource):
    pass


class WxTemplateSchemeResource(TemplateSchemeResource):
    def obj_delete(self, bundle, **kwargs):
        """
        obj delete is forbidden
        """
        return HttpResponseForbidden()
