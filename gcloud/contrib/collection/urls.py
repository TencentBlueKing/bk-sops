# -*- coding: utf-8 -*-
from django.conf.urls import url

from gcloud.contrib.collection.api import BatchCancelCollectionApiView

urlpatterns = (
    url(r"^api/batch_cancel_collection/$", BatchCancelCollectionApiView.as_view()),
)
