# -*- coding: utf-8 -*-
from django.conf.urls import url

from gcloud.contrib.function import api

urlpatterns = (
    url(r"^api/", api.FunctionTaskClaimantTransferView.as_view()),
)
