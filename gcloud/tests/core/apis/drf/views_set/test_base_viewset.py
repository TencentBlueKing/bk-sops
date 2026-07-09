# -*- coding: utf-8 -*-
from types import SimpleNamespace

from django.test import SimpleTestCase
from rest_framework.response import Response

from gcloud.core.apis.drf.viewsets.base import GcloudListViewSet


class _Serializer(object):
    def __init__(self, instance):
        self.instance = instance
        self.data = []


class _EmptyPageViewSet(GcloudListViewSet):
    def __init__(self):
        super(_EmptyPageViewSet, self).__init__()
        self.queryset = object()
        self.serialized_instance = None

    def get_queryset(self):
        return self.queryset

    def filter_queryset(self, queryset):
        return queryset

    def paginate_queryset(self, queryset):
        return []

    def get_serializer(self, instance, many=False):
        self.serialized_instance = instance
        return _Serializer(instance)

    def injection_auth_actions(self, request, serializer_data, queryset_data):
        return serializer_data

    def get_paginated_response(self, data):
        return Response({"results": data})


class TestGcloudListViewSet(SimpleTestCase):
    def test_empty_page_does_not_fall_back_to_full_queryset(self):
        view = _EmptyPageViewSet()

        view.list(SimpleNamespace())

        self.assertEqual(view.serialized_instance, [])
