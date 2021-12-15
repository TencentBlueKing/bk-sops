# -*- coding: utf-8 -*-
from django.conf.urls import url

from gcloud.contrib.function import api

urlpatterns = (
    url(r"^api/function_task_claimant_transfer/$", api.FunctionTaskClaimantTransferView.as_view()),
)
