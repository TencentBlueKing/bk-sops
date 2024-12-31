# -*- coding: utf-8 -*-
from django.urls import re_path

from gcloud.contrib.collection.api import BatchCancelCollectionApiView

urlpatterns = (re_path(r"^api/batch_cancel_collection/$", BatchCancelCollectionApiView.as_view()),)
