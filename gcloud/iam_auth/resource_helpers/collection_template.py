# -*- coding: utf-8 -*-
from iam.contrib.tastypie.resource import IAMResourceHelper

from gcloud.iam_auth import res_factory
from gcloud.iam_auth.resource_helpers.base import SimpleSubjectEnvHelperMixin


class CollectionTemplateResourceHelper(SimpleSubjectEnvHelperMixin, IAMResourceHelper):
    """
    基于DRF的helper，直接会用obj作为入参
    """

    def get_resources(self, obj):
        return res_factory.resources_for_flow_obj(obj)

    def get_resources_id(self, obj):
        return obj.id
