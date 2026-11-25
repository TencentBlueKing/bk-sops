# -*- coding: utf-8 -*-
from types import SimpleNamespace

from django.test import TestCase, override_settings
from django.urls import resolve, reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from gcloud.core.models import Business


@override_settings(ENABLE_MULTI_TENANT_MODE=True)
class TestBusinessTenantIsolation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.business_a = Business.objects.create(
            cc_id=1001, cc_name="Business A", cc_owner="0", cc_company="0", tenant_id="tenant-a"
        )
        cls.business_b = Business.objects.create(
            cc_id=1002, cc_name="Business B", cc_owner="0", cc_company="0", tenant_id="tenant-b"
        )

    def setUp(self):
        self.factory = APIRequestFactory()

    def request_as_tenant(self, tenant_id, url_name, **kwargs):
        url = reverse(url_name, kwargs=kwargs)
        match = resolve(url)
        request = self.factory.get(url)
        force_authenticate(request, user=SimpleNamespace(is_authenticated=True, tenant_id=tenant_id))
        return match.func(request, **match.kwargs)

    def test_list_only_returns_current_tenant_businesses(self):
        for business in (self.business_a, self.business_b):
            with self.subTest(tenant=business.tenant_id):
                response = self.request_as_tenant(business.tenant_id, "business-list")

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                data = response.data["data"]
                self.assertEqual(data["count"], 1)
                self.assertEqual([item["cc_id"] for item in data["results"]], [business.cc_id])

    def test_detail_only_returns_current_tenant_business(self):
        for own, other in ((self.business_a, self.business_b), (self.business_b, self.business_a)):
            with self.subTest(tenant=own.tenant_id):
                own_response = self.request_as_tenant(own.tenant_id, "business-detail", pk=own.pk)
                other_response = self.request_as_tenant(own.tenant_id, "business-detail", pk=other.pk)

                self.assertEqual(own_response.status_code, status.HTTP_200_OK)
                self.assertEqual(own_response.data["data"]["cc_id"], own.cc_id)
                self.assertEqual(other_response.status_code, status.HTTP_403_FORBIDDEN)
