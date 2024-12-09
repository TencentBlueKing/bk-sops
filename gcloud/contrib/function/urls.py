# -*- coding: utf-8 -*-
from django.urls import re_path

from gcloud.contrib.function import api

urlpatterns = (re_path(r"^api/function_task_claimant_transfer/$", api.FunctionTaskClaimantTransferView.as_view()),)
